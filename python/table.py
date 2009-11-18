# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          Romain Gauthier <romain@itaapy.com>
#
# This file is part of Lpod (see: http://lpod-project.org).
# Lpod is free software; you can redistribute it and/or modify it under
# the terms of either:
#
# a) the GNU General Public License as published by the Free Software
#    Foundation, either version 3 of the License, or (at your option)
#    any later version.
#    Lpod is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#    along with Lpod.  If not, see <http://www.gnu.org/licenses/>.
#
# b) the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
#

# Import from the Standard Library
from csv import reader, Sniffer

# Import from lpod
from datatype import Boolean, Date, DateTime, Duration
from element import odf_create_element, register_element_class, odf_element
from utils import get_value, _set_value_and_type
from vfs import vfs


def alpha_to_base10(alpha):
    """Translates A to 1, B to 2, etc. So "AB" is value 28.
    """
    if type(alpha) is int:
        return alpha
    if not alpha.isalpha():
        raise ValueError, 'column name "%s" is malformed' % alpha
    column = 0
    for c in alpha.lower():
        v = ord(c) - ord('a') + 1
        column = column * 26 + v
    return column


def _get_cell_coordinates(obj):
    """Translates "D3" to (3, 2) or return (1, 2) untouched.
    """
    # By (1, 2) ?
    if isinstance(obj, (list, tuple)):
        return tuple(obj)
    # Or by 'B3' notation ?
    if not isinstance(obj, (str, unicode)):
        raise ValueError, 'bad coordinates type: "%s"' % type(obj)
    # First "B"
    alpha = ''
    for c in obj:
        if c.isalpha():
            alpha += c
        else:
            break
    try:
        column = alpha_to_base10(alpha)
    except ValueError:
        raise ValueError, 'cell name "%s" is malformed' % obj
    # Then "3"
    try:
        line = int(obj[len(alpha):])
    except ValueError:
        raise ValueError, 'cell name "%s" is malformed' % obj
    if line <= 0:
        raise ValueError, 'cell name "%s" is malformed' % obj
    # Indexes start at 0
    return column - 1, line - 1



def _get_python_value(data, encoding):
    """Try and guess the most appropriate Python type to load the data, with
    regard to ODF types.
    """
    data = unicode(data, encoding)
    # An int ?
    try:
        return int(data)
    except ValueError:
        pass
    # A float ?
    try:
        return float(data)
    except ValueError:
        pass
    # A Date ?
    try:
        return Date.decode(data)
    except ValueError:
        pass
    # A DateTime ?
    try:
        # Two tests: "yyyy-mm-dd hh:mm:ss" or "yyyy-mm-ddThh:mm:ss"
        return DateTime.decode(data.replace(' ', 'T'))
    except ValueError:
        pass
    # A Duration ?
    try:
        return Duration.decode(data)
    except ValueError:
        pass
    # A Boolean ?
    try:
        # "True" or "False" with a .lower
        return Boolean.decode(data.lower())
    except ValueError:
        pass
    # TODO Try some other types ?
    # So a text
    return data



def _set_element(position, new_element, real_elements, get_repeated,
        set_repeated):
    p = 0
    for real_element in real_elements:
        repeated = get_repeated(real_element) or 1
        for current_repetition in xrange(repeated):
            if p == position:
                # Repetitions start counting at 1
                current_repetition += 1
                break
            p += 1
        else:
            # Not found on this(these) element(s)
            continue
        parent = real_element.get_parent()
        index = parent.index(real_element)
        # Split, update repetitions and insert the new one
        repeated_after = repeated - current_repetition
        repeated_before = current_repetition - 1
        if repeated_before:
            # Update repetition
            set_repeated(real_element, repeated_before)
        else:
            # Replacing the first occurence
            parent.delete_element(real_element)
            index -= 1
        # Insert new element
        parent.insert_element(new_element.clone(), position=index + 1, )
        # Insert the remaining repetitions
        if repeated_after:
            element_after = real_element.clone()
            set_repeated(element_after, repeated_after)
            parent.insert_element(element_after, position=index + 2)
        return



def _insert_element(position, new_element, real_elements, get_repeated,
        set_repeated):
    p = 0
    for real_element in real_elements:
        repeated = get_repeated(real_element) or 1
        for current_repetition in xrange(repeated):
            if p == position:
                # Repetitions start counting at 1
                current_repetition += 1
                break
            p += 1
        else:
            # Not found on this(these) element(s)
            continue
        parent = real_element.get_parent()
        index = parent.index(real_element)
        if repeated == 1 or current_repetition == 1:
            # Just insert before
            parent.insert_element(new_element.clone(), position=index)
        else:
            repeated_after = repeated - current_repetition + 1
            repeated_before = current_repetition - 1
            # Update repetition
            set_repeated(real_element, repeated_before)
            # Insert new element
            parent.insert_element(new_element.clone(), position=index + 1)
            # Insert the remaining repetitions
            if repeated_after:
                element_after = real_element.clone()
                set_repeated(element_after, repeated_after)
                parent.insert_element(element_after, position=index + 2)
        return



def _delete_element(position, real_elements, get_repeated, set_repeated):
    p = 0
    for real_element in real_elements:
        repeated = get_repeated(real_element) or 1
        for current_repetition in xrange(repeated):
            if p == position:
                break
            p += 1
        else:
            # Not found on this(these) element(s)
            continue
        # Lost 1 credit
        repeated -= 1
        if repeated:
            set_repeated(real_element, repeated)
        else:
            # Game over
            parent = real_element.get_parent()
            parent.delete_element(real_element)
        return



def odf_create_cell(value=None, representation=None, cell_type=None,
                    currency=None, style=None):
    """Create a cell element containing the given value. The textual
    representation is automatically formatted but can be provided. Cell type
    can be deduced as well, unless the number is a percentage or currency. If
    cell type is "currency", the currency must be given.

    Arguments:

        value -- bool, int, float, Decimal, date, datetime, str, unicode,
                 timedelta

        representation -- unicode

        cell_type -- 'boolean', 'currency', 'date', 'float', 'percentage',
                     'string' or 'time'

        currency -- three-letter str

        style -- unicode

    Return: odf_cell
    """

    element = odf_create_element('<table:table-cell/>')
    element.set_cell_value(value, representation=representation,
            cell_type=cell_type, currency=currency)
    if style is not None:
        element.set_cell_style(style)
    return element



def odf_create_row(width=None, repeated=None, style=None):
    """Create a row element, optionally filled with "width" number of cells.

    Rows contain cells, their number determine the number of columns.

    You don't generally have to create rows by hand, use the odf_table API.

    Arguments:

        width -- int

        repeated -- int

        style -- unicode

    Return: odf_row
    """
    element = odf_create_element('<table:table-row/>')
    if width is not None:
        for i in xrange(width):
            cell = odf_create_cell(u"")
            element.append_element(cell)
    if repeated:
        element.set_row_repeated(repeated)
    if style is not None:
        element.set_row_style(style)
    return element



def odf_create_row_group(height=None, width=None):
    """Create a group of rows, optionnaly filled with "height" number of rows,
    of "width" cells each.

    Row group bear style information applied to a series of rows.

    Arguments:

        height -- int

    Return odf_row_group
    """
    element = odf_create_row_group('<table:table-row-group')
    if height is not None:
        for i in xrange(height):
            row = odf_create_row(width)
            element.append_element(row)
    return element



def odf_create_column(default_cell_style=None, repeated=None, style=None):
    """Create a column group element of the optionally given style. Cell
    style can be set for the whole column. If the properties apply to several
    columns, give the number of repeated columns.

    Columns don't contain cells, just style information.

    You don't generally have to create columns by hand, use the odf_table API.

    Arguments:

        default_cell_style -- unicode

        repeated -- int

        style -- unicode

    Return: odf_column
    """
    element = odf_create_element('<table:table-column/>')
    if default_cell_style:
        element.set_column_default_cell_style(default_cell_style)
    if repeated:
        element.set_column_repeated(repeated)
    if style:
        element.set_column_style(style)
    return element



def odf_create_table(name, width=None, height=None, protected=False,
        protection_key=None, display=True, printable=True, print_ranges=None,
        style=None):
    """Create a table element, optionally prefilled with "height" rows of
    "width" cells each.

    If the table is to be protected, a protection key must be provided, i.e. a
    hash value of the password (XXX what algorithm?).

    If the table must not be displayed, set "display" to False.

    If the table must not be printed, set "printable" to False. The table will
    not be printed when it is not displayed, whatever the value of this
    argument.

    Ranges of cells to print can be provided as a list of cell ranges, e.g.
    ['E6:K12', 'P6:R12'] or directly as a raw string, e.g. "E6:K12 P6:R12".

    You can access and modify the XML tree manually, but you probably want to
    use the API to access and alter cells. It will save you from handling
    repetitions and the same number of cells for each row.

    If you use both the table API and the XML API, you are on your own for
    ensuiring model integrity.

    Arguments:

        name -- unicode

        width -- int

        height -- int

        protected -- bool

        protection_key -- str

        display -- bool

        printable -- bool

        print_ranges -- list

        style -- unicode

    Return: odf_table
    """
    element = odf_create_element(u'<table:table table:name="%s"/>' % name)
    if protected:
        raise NotImplementedError, "protected"
        # TODO
        if protection_key is None:
            raise ValueError, "missing protection key"
        element.set_table_protected(protected)
    if not display:
        element.set_table_displayed(display)
    if not printable:
        element.set_table_printable(printable)
    if print_ranges:
        element.set_table_print_ranges(print_ranges)
    if style:
        element.set_table_style(style)
    # Prefill the table
    if width is not None or height is not None:
        width = width or 1
        height = height or 1
        # Column groups for style information
        columns = odf_create_column(repeated=width)
        element.append_element(columns)
        for i in xrange(height):
            row = odf_create_row(width)
            element.append_element(row)
    return element



class odf_cell(odf_element):
    """Class for the table cell element.
    """

    def get_cell_value(self, try_get_text=False):
        return get_value(self, try_get_text=try_get_text)


    def set_cell_value(self, value, representation=None, cell_type=None,
            currency=None):
        representation = _set_value_and_type(self, value=value,
                representation=representation, value_type=cell_type,
                currency=currency)
        if representation is not None:
            self.set_text_content(representation)


    def get_cell_repeated(self):
        """Get the integer value of the cell repetition attribute, or None if
        undefined.

        Return: int or None
        """
        repeated = self.get_attribute('table:number-columns-repeated')
        if repeated is None:
            return None
        return int(repeated)


    def set_cell_repeated(self, repeated):
        """Set the cell repetition attribute, or None to delete it.

        Arguments:

            repeated -- int or None
        """
        if repeated is None or repeated == 0:
            try:
                self.del_attribute('table:number-columns-repeated')
            except KeyError:
                return
        self.set_attribute('table:number-columns-repeated', str(repeated))


    def get_cell_style(self):
        return self.get_attribute('table:style-name')


    def set_cell_style(self, style):
        self.set_attribute('table:style-name', style)



class odf_row(odf_element):


    def __check_x(self, x):
        width = self.get_row_width()
        if x < 0:
            x = width - x
        if x < 0 or x >= width:
            raise ValueError, "X outside of row"
        return x


    def get_row_repeated(self):
        repeated = self.get_attribute('table:number-rows-repeated')
        if repeated is None:
            return None
        return int(repeated)


    def set_row_repeated(self, repeated):
        if repeated is None or repeated == 0:
            try:
                self.del_attribute('table:number-rows-repeated')
            except KeyError:
                return
        self.set_attribute('table:number-rows-repeated', str(repeated))


    def get_row_style(self):
        return self.get_attribute('table:style-name')


    def set_row_style(self, style):
        self.set_attribute('table:style-name', style)


    def traverse_cells(self):
        """Return as many cell elements as expected cells in the row, i.e.
        expand repetitions by returning the same cell as many times as
        necessary.

        The original cell element is returned, with its repetition
        attribute.

        Mostly used by the odf_table API.
        """
        for cell in self.get_element_list(
                '(table:table-cell|table:covered-table-cell)'):
            repeated = cell.get_cell_repeated() or 1
            for i in xrange(repeated):
                yield cell


    def get_cell(self, x):
        x = alpha_to_base10(x)
        x = self.__check_x(x)
        for w, cell in enumerate(self.traverse_cells()):
            if w == x:
                # Return a copy without the now obsolete repetition
                cell = cell.clone()
                cell.set_cell_repeated(None)
                return cell



    def set_cell(self, x, cell):
        x = self.__check_x(x)
        if cell.get_cell_repeated():
            raise ValueError, "setting a repeted cell not supported"
        _set_element(x, cell, self.get_element_list(
                '(table:table-cell|table:covered-table-cell)'),
                odf_cell.get_cell_repeated, odf_cell.set_cell_repeated)


    def insert_cell(self, x, cell):
        x = self.__check_x(x)
        # Inserting a repeated cell accepted
        _insert_element(x, cell, self.get_element_list(
                '(table:table-cell|table:covered-table-cell)'),
                odf_cell.get_cell_repeated, odf_cell.set_cell_repeated)


    def append_cell(self, cell):
        # Appending a repeated cell accepted
        self.append_element(cell)


    def delete_cell(self, x):
        x = self.__check_x(x)
        _delete_element(x, self.get_element_list(
                '(table:table-cell|table:covered-table-cell)/'),
                odf_cell.get_cell_repeated, odf_cell.set_cell_repeated)


    def get_row_width(self):
        """Return the number of expected cells in the row, i.e. addition
        repetitions.
        """
        cells = self.get_element_list(
                '(table:table-cell|table:covered-table-cell)')
        repeated = self.xpath(
                '(table:table-cell|table:covered-table-cell)/'
                '@table:number-columns-repeated')
        unrepeated = len(cells) - len(repeated)
        return sum(int(r) for r in repeated) + unrepeated



class odf_row_group(odf_element):
    """Class to group rows with common properties.
    """
    # TODO
    pass



class odf_column(odf_element):

    def get_column_default_cell_style(self):
        return self.get_attribute('table:default-cell-style-name')


    def set_column_default_cell_style(self, style):
        self.set_attribute('table:default-cell-style-name', style)


    def get_column_repeated(self):
        repeated = self.get_attribute('table:number-columns-repeated')
        if repeated is None:
            return None
        return int(repeated)


    def set_column_repeated(self, repeated):
        if repeated is None or repeated == 0:
            try:
                self.del_attribute('table:number-columns-repeated')
            except KeyError:
                return
        self.set_attribute('table:number-columns-repeated', str(repeated))


    def get_column_style(self):
        return self.get_attribute('table:style-name')


    def set_column_style(self, style):
        self.set_attribute('table:style-name', style)



class odf_table(odf_element):
    #
    # Private API
    #

    def __check_x(self, x):
        width = self.get_table_width()
        if x < 0:
            x = width - x
        if x < 0 or x >= width:
            raise ValueError, "X outside of table"
        return x


    def __check_y(self, y):
        height = self.get_table_height()
        if y < 0:
            y = height - y
        if y < 0 or y >= height:
            raise ValueError, "Y outside of table"
        return y


    def __check_width(self, row):
        width = self.get_table_width()
        if width and row.get_row_width() != width:
            raise ValueError, "row mismatch: %s cells expected" % width


    #
    # Public API
    #


    def get_table_height(self):
        """Get the current height of the table.
        """
        rows = self.get_element_list('table:table-row')
        repeated = self.xpath('table:table-row/@table:number-rows-repeated')
        unrepeated = len(rows) - len(repeated)
        return sum(int(r) for r in repeated) + unrepeated


    def get_table_width(self):
        """Get the current width of the table.
        """
        # Count columns: a good way to ensure consistency with row width
        columns = self.get_element_list('table:table-column')
        repeated = self.xpath(
                'table:table-column/@table:number-columns-repeated')
        unrepeated = len(columns) - len(repeated)
        return sum(int(r) for r in repeated) + unrepeated


    def get_table_size(self):
        """Get the current width and height of the table.

        Return: (int, int)
        """
        return self.get_table_width(), self.get_table_height()


    def get_table_name(self):
        return self.get_attribute('table:name')


    def is_table_protected(self):
        return self.get_attribute('table:protected') == 'true'


    def set_table_protected(self, protect):
        self.set_attribute('table:protected', Boolean.encode(protect))


    def is_table_displayed(self):
        return self.get_attribute('table:display') == 'true'


    def set_table_displayed(self, display):
        self.set_attribute('table:display', Boolean.encode(display))


    def is_table_printable(self):
        printable = self.get_attribute('table:print')
        # Default value
        if printable is None:
            printable = 'true'
        return printable == 'true'


    def set_table_printable(self, printable):
        self.set_attribute('table:print', Boolean.encode(printable))


    def get_table_print_ranges(self):
        return self.get_attribute('table:print-ranges').split()


    def set_table_print_ranges(self, print_ranges):
        if isinstance(print_ranges, (tuple, list)):
            print_ranges = ' '.join(print_ranges)
        self.set_attribute('table:print-ranges', print_ranges)


    def get_table_style(self):
        return self.get_attribute('table:style-name')


    def set_table_style(self, style):
        self.set_attribute('table:style-name', style)


    def get_formated_text(self, context):
        result = []
        for row in self.traverse_rows():
            for cell in row.traverse_cells():
                value = get_value(cell, try_get_text=False)
                # None ?
                if value is None:
                    # Try with get_formated_text on the elements
                    value = []
                    for element in cell.get_children():
                        value.append(element.get_formated_text(context))
                    value = u''.join(value)
                else:
                    value = unicode(value)
                result.append(value)
                result.append(u'\n')
            result.append(u'\n')
        return u''.join(result)


    #
    # Rows
    #

    def traverse_rows(self):
        """Return as many row elements as expected rows, i.e. expand
        repetitions by returning the same row as many times as necessary.

        The original row element is returned, with its repetition attribute.

        Mostly used by the higher-level API like "get_row" and "set_row".
        """
        for row in self.get_element_list('table:table-row'):
            repeated = row.get_row_repeated() or 1
            for i in xrange(repeated):
                yield row


    def get_row_list(self, regex=None, style=None):
        """Return the list of rows matching the criteria. Each result is a
        tuple of (y, row).

        The original row elements are returned, with their repetition
        attribute.

        Arguments:

            regex -- unicode

            style -- unicode

        Return: list of tuples
        """
        rows = []
        for y, row in enumerate(self.traverse_rows()):
            if regex and not row.match(regex):
                continue
            if style and row.get_row_style() != style:
                continue
            rows.append((y, row))
        return rows


    def get_row(self, y):
        """Return a copy of the row at the given position. The object is
        editable but only taken into account when put back using "set_row".

        Position start at 0. So cell A4 is on row 3.

        Arguments:

            y -- int
        """
        y = self.__check_y(y)
        for h, row in enumerate(self.traverse_rows()):
            if h == y:
                # Return a copy without the now obsolete repetition
                row = row.clone()
                row.set_row_repeated(None)
                return row


    def set_row(self, y, row):
        """Replace the row at the given position with the new one. It must
        have the same number of cells. Repetion of the old row will be
        adjusted.

        Position start at 0. So cell A4 is on row 3.

        Arguments:

            y -- int

            row -- odf_row
        """
        y = self.__check_y(y)
        self.__check_width(row)
        # Setting a repeated row accepted
        _set_element(y, row, self.get_element_list('table:table-row'),
                odf_row.get_row_repeated, odf_row.set_row_repeated)


    def insert_row(self, y, row):
        """Insert the row before the given position. It must have the same
        number of cells.

        Position start at 0. So cell A4 is on row 3.

        Arguments:

            y -- int

            row -- odf_row
        """
        y = self.__check_y(y)
        self.__check_width(row)
        # Inserting a repeated row accepted
        _insert_element(y, row, self.get_element_list('table:table-row'),
                odf_row.get_row_repeated, odf_row.set_row_repeated)


    def append_row(self, row):
        """Append the row at the end of the table.

        Position start at 0. So cell A4 is on row 3.

        Arguments:

            row -- odf_row
        """
        self.__check_width(row)
        # Appending a repeated row accepted
        # Do not insert next to the last row because it could be in a group
        self.append_element(row)


    def delete_row(self, y):
        """Delete the row at the given position.

        Position start at 0. So cell A4 is on row 3.

        Arguments:

            y -- int
        """
        y = self.__check_y(y)
        _delete_element(y, self.get_element_list('table:table-row'),
                odf_row.get_row_repeated, odf_row.set_row_repeated)


    #
    # Cells
    #

    def get_cell(self, coordinates):
        """Return the cell at the given coordinates.

        They are either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4".

        The cell object is modifiable but you need to put it back using
        "set_cell".

        Arguments:

            coordinates -- (int, int) or str

        Return: odf_cell
        """
        x, y = _get_cell_coordinates(coordinates)
        y = self.__check_y(y)
        for h, row in enumerate(self.traverse_rows()):
            if h == y:
                return row.get_cell(x)


    def set_cell(self, coordinates, cell):
        """Replace a cell of the table at the given coordinates.

        They are either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4".

        Arguments:

            coordinates -- (int, int) or str

            cell -- odf_cell
        """
        x, y = _get_cell_coordinates(coordinates)
        y = self.__check_y(y)
        for h, row in enumerate(self.traverse_rows()):
            if h == y:
                return row.set_cell(x, cell)


    def get_cell_list(self, regex=None, style=None):
        """Return the list of cells matching the criteria. Each result is a
        tuple of (x, y, cell).

        Arguments:

            regex -- unicode

            style -- unicode

        Return: list of tuples
        """
        cells = []
        for y, row in enumerate(self.traverse_rows()):
            for x, cell in enumerate(row.traverse_cells()):
                # Filter the cells with the regex
                if regex and not cell.match(regex):
                    continue
                # Filter the cells with the style
                if style and cell.get_cell_style() != style:
                        continue
                cells.append((x, y, cell))
        # Return the coordinates and element
        return cells


    #
    # Columns
    #

    def traverse_columns(self):
        """Return as many column elements as expected columns, i.e. expand
        repetitions by returning the same column as many times as necessary.

        The original column elements are returned, with their repetition
        attribute.

        Mostly used by the higher-level API like "get_column" and
        "set_column".
        """
        for column in self.get_element_list('table:table-column'):
            repeated = column.get_column_repeated() or 1
            for i in xrange(repeated):
                yield column


    def get_column_list(self, style=None):
        """Return the list of columns matching the criteria. Each result is a
        tuple of (x, column).

        The original column elements are returned, with their repetition
        attribute.

        Arguments:

            style -- unicode

        Return: list of tuples
        """
        columns = []
        for w, column in enumerate(self.traverse_columns()):
            if column.get_column_style() != style:
                continue
            columns.append((w, column))
        return columns


    def get_column(self, x):
        """Return a copy of the column at the given position. The object is
        editable but only taken into account when put back using "set_column".

        ODF columns don't contain cells, only style information.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        Arguments:

            x -- int or str.isalpha()

        Return: odf_column
        """
        x = self.__check_x(x)
        for w, column in enumerate(self.traverse_columns()):
            if w == x:
                # Return a copy without the now obsolete repetition
                column = column.clone()
                column.set_column_repeated(None)
                return column


    def set_column(self, x, column):
        """Replace the column at the given position.

        ODF columns don't contain cells, only style information.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        Arguments:

            x -- int or str.isalpha()

            column -- odf_column
        """
        x = self.__check_x(x)
        _set_element(x, column, self.get_element_list('table:table-column'),
                odf_column.get_column_repeated,
                odf_column.set_column_repeated)



    def insert_column(self, x, column):
        """Insert the column before the given position.

        ODF columns don't contain cells, only style information.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        Arguments:

            x -- int or str.isalpha()

            column -- odf_column
        """
        x = self.__check_x(x)
        _insert_element(x, column,
                self.get_element_list('table:table-column'),
                odf_column.get_column_repeated,
                odf_column.set_column_repeated)


    def append_column(self, column):
        """Append the column at the end of the table.

        ODF columns don't contain cells, only style information.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        Arguments:

            column -- odf_column
        """
        self.append_element(column)


    def delete_column(self, x):
        """Delete the column at the given position. ODF columns don't contain
        cells, only style information.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        Arguments:

            x -- int or str.isalpha()
        """
        x = self.__check_x(x)
        _delete_element(x, self.get_element_list('table:table-column'),
                odf_column.get_column_repeated,
                odf_column.set_column_repeated)



    #
    # Utilities
    #

    def export_to_csv(self, file, delimiter=';', quotechar='"',
                      lineterminator='\n', encoding='utf-8'):
        """
        Write the table as CSV in the file. If the file is a name, it is
        opened as a URI. Else a file-like is expected. Opened file-like
        are closed, given file-like are left open.

        Arguments:

            file -- file-like or URI

            delimiter -- str

            quotechar -- str

            lineterminator -- str

            encoding -- str
        """
        close_after = False
        if type(file) is str or type(file) is unicode:
            file = vfs.open(file, 'w')
            close_after = True
        quoted = '\\' + quotechar
        for row in self.traverse_rows():
            current_row = []
            for cell in row.traverse_cells():
                # Get value
                value = cell.get_cell_value()
                if type(value) is unicode:
                    value = value.encode(encoding)
                if type(value) is str:
                    value = value.strip()
                value = '' if value is None else str(value)
                # Quote
                value = value.replace(quotechar, quoted)
                # Append !
                current_row.append(quotechar + value + quotechar)
            file.write(delimiter.join(current_row) + lineterminator)
        if close_after:
            file.close()



def import_from_csv(file, name, style=None, delimiter=None, quotechar=None,
        lineterminator=None, encoding='utf-8'):
    """Convert the CSV file to an odf_table.

    CSV format can be autodetected to a certain limit, but encoding is
    important.

    Arguments:

      file -- file-like or URI

      name -- unicode

      style -- str

      delimiter -- str

      quotechar -- str

      lineterminator -- str

      encoding -- str
    """

    # Load the data
    # XXX Load the entire file in memory
    # Alternative: a file-wrapper returning the sample then the rest
    if type(file) is str:
        file = vfs.open(file)
        data = file.read().splitlines(True)
        file.close()
    else:
        # Leave the file we were given open
        data = file.read().splitlines(True)
    # Sniff the dialect
    sample = ''.join(data[:100])
    dialect = Sniffer().sniff(sample)
    # We can overload the result
    if delimiter is not None:
        dialect.delimiter = delimiter
    if quotechar is not None:
        dialect.quotechar = quotechar
    if lineterminator is not None:
        dialect.lineterminator = lineterminator
    # Make the rows
    csv = reader(data, dialect)
    table = odf_create_table(name, style=style)
    for line in csv:
        row = odf_create_row()
        for value in line:
            cell = odf_create_cell(_get_python_value(value, encoding))
            row.append_cell(cell)
        table.append_row(row)
    return table



# Register
register_element_class('table:table-cell', odf_cell)
register_element_class('table:table-row', odf_row)
register_element_class('table:table-column', odf_column)
register_element_class('table:table', odf_table)
