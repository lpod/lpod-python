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


def _alpha_to_digit(alpha):
    """Translates A to 0, B to 1, etc. So "AB" is value 27.
    """
    if type(alpha) is int:
        return alpha
    if not alpha.isalpha():
        raise ValueError, 'column name "%s" is malformed' % alpha
    column = 0
    for c in alpha.lower():
        v = ord(c) - ord('a') + 1
        column = column * 26 + v
    return column - 1



def _digit_to_alpha(digit):
    if type(digit) is str and digit.isalpha():
        return digit
    if not type(digit) is int:
        raise ValueError, 'column number "%s" is invalid' % digit
    digit += 1
    column = ''
    while digit:
        column = chr(65 + ((digit - 1) % 26)) + column
        digit = (digit - 1) / 26
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
        column = _alpha_to_digit(alpha)
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
    return column, line - 1



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
                    currency=None, repeated=None, style=None):
    """Create a cell element containing the given value. The textual
    representation is automatically formatted but can be provided. Cell type
    can be deduced as well, unless the number is a percentage or currency. If
    cell type is "currency", the currency must be given. The cell can be
    repeated on the given number of columns.

    Arguments:

        value -- bool, int, float, Decimal, date, datetime, str, unicode,
                 timedelta

        representation -- unicode

        cell_type -- 'boolean', 'currency', 'date', 'float', 'percentage',
                     'string' or 'time'

        currency -- three-letter str

        repeated -- int

        style -- unicode

    Return: odf_cell
    """

    element = odf_create_element('<table:table-cell/>')
    element.set_cell_value(value, representation=representation,
            cell_type=cell_type, currency=currency)
    if repeated and repeated > 1:
        element.set_cell_repeated(repeated)
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
            element.append_element(odf_create_cell())
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
        if protection_key is None:
            raise ValueError, "missing protection key"
        # TODO
        raise NotImplementedError, "protected"
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

    def get_cell_value(self):
        """Get the Python value that represent the cell.

        Possible return types are unicode, int, Decimal, datetime,
        timedelta.

        Return: Python type
        """
        return get_value(self)


    def set_cell_value(self, value, representation=None, cell_type=None,
            currency=None):
        """Set the cell state from the Python value type.

        Representation is how the cell is displayed. Cell type is guessed,
        unless provided.

        For monetary values, provide the name of the currency.

        Arguments:

            value -- Python type

            representation -- unicode

            cell_type -- 'boolean', 'float', 'date', 'string' or 'time'

            currency -- unicode
        """
        representation = _set_value_and_type(self, value=value,
                representation=representation, value_type=cell_type,
                currency=currency)
        if representation is not None:
            self.set_text_content(representation)


    def get_cell_type(self):
        """Get the type of the cell: boolean, float, date, string or time.

        Return: str
        """
        return self.get_attribute('office:value-type')


    def set_cell_type(self, cell_type):
        """Set the type ofthe cell manually.

        Arguments:

            value -- Python type

            representation -- unicode

            cell_type -- 'boolean', 'float', 'date', 'string' or 'time'
        """
        self.set_attribute('office:value-type', cell_type)


    def get_cell_currency(self):
        """Get the currency used for monetary values.
        """
        return self.get_attribute('office:currency')


    def set_cell_currency(self, currency):
        """Set the currency used for monetary values.

        Arguments:

            currency -- unicode
        """
        self.set_attribute('office:currency', currency)


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
        if repeated is None or repeated < 2:
            try:
                self.del_attribute('table:number-columns-repeated')
            except KeyError:
                pass
            return
        self.set_attribute('table:number-columns-repeated', str(repeated))


    def get_cell_style(self):
        """Get the style of the cell itself.

        Return: unicode
        """
        return self.get_attribute('table:style-name')


    def set_cell_style(self, style):
        """Set the style of the cell itself.

        Arguments:

            style -- unicode
        """
        self.set_attribute('table:style-name', style)



class odf_row(odf_element):

    # Private API

    def __check_x(self, x):
        x = _alpha_to_digit(x)
        width = self.get_row_width()
        if x < 0:
            x = width + x
        if x < 0 or x >= width:
            raise ValueError, "X %d outside of row" % x
        return x


    def _get_cells(self):
        return self.get_element_list(
                '(table:table-cell|table:covered-table-cell)')

    # Public API

    def get_row_repeated(self):
        """Get the number of times the "real" row is repeated.

        Always None when using the table API.

        Return: int or None
        """
        repeated = self.get_attribute('table:number-rows-repeated')
        if repeated is None:
            return None
        return int(repeated)


    def set_row_repeated(self, repeated):
        """Set the number of times the "real" row is repeated.

        Useless and even dangerous when using the table API.

        Arguments:

            repeated -- int or None
        """
        if repeated is None or repeated < 2:
            try:
                self.del_attribute('table:number-rows-repeated')
            except KeyError:
                pass
            return
        self.set_attribute('table:number-rows-repeated', str(repeated))


    def get_row_style(self):
        """Get the style of the row itself.

        Return: unicode
        """
        return self.get_attribute('table:style-name')


    def set_row_style(self, style):
        """Set the style of the row itself.

        Arguments:

            style -- unicode
        """
        self.set_attribute('table:style-name', style)


    def get_row_width(self):
        """Get the number of expected cells in the row, i.e. addition
        repetitions.

        Return: int
        """
        cells = self._get_cells()
        repeated = self.xpath(
                '(table:table-cell|table:covered-table-cell)/'
                '@table:number-columns-repeated')
        unrepeated = len(cells) - len(repeated)
        return sum(int(r) for r in repeated) + unrepeated


    def traverse_cells(self):
        """Yield as many cell elements as expected cells in the row, i.e.
        expand repetitions by returning the same cell as many times as
        necessary.

        Copies are returned, use ``set_cell`` to push them back.
        """
        for cell in self._get_cells():
            repeated = cell.get_cell_repeated() or 1
            for i in xrange(repeated):
                # Return a copy without the now obsolete repetition
                cell = cell.clone()
                cell.set_cell_repeated(None)
                yield cell


    def get_cell_list(self, regex=None, style=None):
        """Get the list of cells matching the criteria. Each result is a
        tuple of (x, y, cell).

        Arguments:

            regex -- unicode

            style -- unicode

        Return: list of tuples
        """
        cells = []
        for x, cell in enumerate(self.traverse_cells()):
            # Filter the cells with the regex
            if regex and not cell.match(regex):
                continue
            # Filter the cells with the style
            if style and style != cell.get_cell_style():
                continue
            cells.append((x, cell))
        # Return the coordinate and element
        return cells


    def get_cell(self, x):
        """Get the cell at position "x" starting from 0. Alphabetical
        positions like "D" are accepted.

        A  copy is returned, use ``set_cell`` to push it back.

        Arguments:

            x -- int or str

        Return: odf_cell
        """
        x = self.__check_x(x)
        for w, cell in enumerate(self.traverse_cells()):
            if w == x:
                return cell


    def get_cell_value(self, x):
        """Shortcut to get the value of the cell at position "x".

        See ``get_cell`` and ``odf_cell.get_cell_value``.
        """
        return self.get_cell(x).get_cell_value()



    def set_cell(self, x, cell):
        """Push the cell back in the row at position "x" starting from 0.
        Alphabetical positions like "D" are accepted.

        Arguments:

            x -- int or str
        """
        x = self.__check_x(x)
        if cell.get_cell_repeated():
            raise ValueError, "setting a repeted cell not supported"
        _set_element(x, cell, self._get_cells(), odf_cell.get_cell_repeated,
                odf_cell.set_cell_repeated)


    def set_cell_value(self, x, value):
        """Shortcut to set the value of the cell at position "x".

        See ``get_cell`` and ``odf_cell.get_cell_value``.
        """
        self.set_cell(x, odf_create_cell(value))


    def insert_cell(self, x, cell):
        """Insert the given cell at position "x" starting from 0.
        Alphabetical positions like "D" are accepted.

        Do not use when working on a table, use ``odf_table.insert_cell``.

        Arguments:

            x -- int or str

            cell -- odf_cell
        """
        x = self.__check_x(x)
        # Inserting a repeated cell accepted
        _insert_element(x, cell, self._get_cells(),
                odf_cell.get_cell_repeated, odf_cell.set_cell_repeated)


    def append_cell(self, cell):
        """Append the given cell at the end of the row. Repeated cells are
        accepted.

        Do not use when working on a table, use ``odf_table.append_cell``.

        Arguments:

            cell -- odf_cell
        """
        self.append_element(cell)


    def delete_cell(self, x):
        """Delete the cell at the given position "x" starting from 0.
        Alphabetical positions like "D" are accepted.

        Do not use when working on a table, use ``odf_table.delete_cell``.

        Arguments:

            x -- int or str
        """
        x = self.__check_x(x)
        _delete_element(x, self._get_cells(), odf_cell.get_cell_repeated,
                odf_cell.set_cell_repeated)


    def get_cell_values(self):
        """Get the list of all cell values in this row.

        Return: list of Python types
        """
        return [cell.get_cell_value() for cell in self.traverse_cells()]


    def set_cell_values(self, values):
        """Set the list of all cell values in this row. The list must have
        the same length than the row.

        Arguments:

            values -- list of Python types
        """
        width = self.get_row_width()
        if len(values) != width:
            raise ValueError, "row mismatch: %s cells expected" % width
        for x, value in enumerate(values):
            self.set_cell_value(x, value)


    def rstrip_row(self):
        """Remove *in-place* the empty cells at the right of the row.

        Do not use when working on a table, use ``odf_table.rstrip_table``.

        """
        for cell in reversed(self._get_cells()):
            if (cell.get_cell_style() is None
                    and cell.get_cell_value() is None):
                self.delete_element(cell)
            else:
                return


    def is_row_empty(self):
        """Wether all cells in the row are empty.

        Return: bool
        """
        for cell in self._get_cells():
            if (cell.get_cell_style() is not None
                    or cell.get_cell_value() is not None):
                return False
        return True



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
        if repeated is None or repeated < 2:
            try:
                self.del_attribute('table:number-columns-repeated')
            except KeyError:
                pass
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
            x = width + x
        if x < 0 or x >= width:
            raise ValueError, "X %d outside of table" % x
        return x


    def __check_y(self, y):
        height = self.get_table_height()
        if y < 0:
            y = height + y
        if y < 0 or y >= height:
            raise ValueError, "Y %d outside of table" % y
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

        Return: int
        """
        rows = self._get_rows()
        repeated = self.xpath('table:table-row/@table:number-rows-repeated')
        unrepeated = len(rows) - len(repeated)
        return sum(int(r) for r in repeated) + unrepeated


    def get_table_width(self):
        """Get the current width of the table.

        Measured on columns. Use the odf_table API to ensure width
        consistency.

        Return: int
        """
        # Count columns: a good way to ensure consistency with row width
        columns = self._get_columns()
        repeated = self.xpath(
                'table:table-column/@table:number-columns-repeated')
        unrepeated = len(columns) - len(repeated)
        return sum(int(r) for r in repeated) + unrepeated


    def get_table_size(self):
        """Shortcut to get the current width and height of the table.

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


    def get_table_values(self):
        """Get a matrix of all Python values of the cells.

        Return: list of lists
        """
        return [row.get_cell_values() for row in self.traverse_rows()]


    def set_table_values(self, values):
        """Set all Python values of all the cells.

        A list of lists is expected, with as many lists as rows, and as many
        items in each sublist as cells.

        Arguments:

            values -- list of lists
        """
        values = iter(values)
        for y, row in enumerate(self.traverse_rows()):
            row.set_cell_values(values.next())
            self.set_row(y, row)


    def rstrip_table(self):
        """Remove *in-place* empty rows below and empty cells at the right of
        the table.
        """
        # Step 1: remove empty rows below the table
        for row in reversed(self._get_rows()):
            if row.is_row_empty():
                row.get_parent().delete_element(row)
            else:
                break
        # Step 2: remove empty columns of cells for remaining rows
        for x in xrange(self.get_table_width() - 1, -1, -1):
            if self.is_column_empty(x):
                self.delete_column(x)
            else:
                break



    #
    # Rows
    #

    def _get_rows(self):
        return self.get_element_list('table:table-row')


    def traverse_rows(self):
        """Yield as many row elements as expected rows in the table, i.e.
        expand repetitions by returning the same row as many times as
        necessary.

        Copies are returned, use ``set_row`` to push them back.
        """
        for row in self._get_rows():
            repeated = row.get_row_repeated() or 1
            for i in xrange(repeated):
                # Return a copy without the now obsolete repetition
                row = row.clone()
                row.set_row_repeated(None)
                yield row


    def get_row_list(self, regex=None, style=None):
        """Get the list of rows matching the criteria. Each result is a
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
            if style and style != row.get_row_style():
                continue
            rows.append((y, row))
        return rows


    def get_row(self, y):
        """Get the row at the given "y" position.

        Position start at 0. So cell A4 is on row 3.

        A copy is returned, use ``set_cell`` to push it back.

        Arguments:

            y -- int

        Return: odf_row
        """
        y = self.__check_y(y)
        for h, row in enumerate(self.traverse_rows()):
            if h == y:
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
        _set_element(y, row, self._get_rows(), odf_row.get_row_repeated,
                odf_row.set_row_repeated)


    def insert_row(self, y, row):
        """Insert the row before the given "y" position. It must have the
        same number of cells.

        Position start at 0. So cell A4 is on row 3.

        Arguments:

            y -- int

            row -- odf_row
        """
        y = self.__check_y(y)
        self.__check_width(row)
        # Inserting a repeated row accepted
        _insert_element(y, row, self._get_rows(), odf_row.get_row_repeated,
                odf_row.set_row_repeated)


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
        """Delete the row at the given "y" position.

        Position start at 0. So cell A4 is on row 3.

        Arguments:

            y -- int
        """
        y = self.__check_y(y)
        _delete_element(y, self._get_rows(), odf_row.get_row_repeated,
                odf_row.set_row_repeated)


    def get_row_values(self, y):
        """Get the list of Python values for the cells of the row at the
        given "y" position.

        Position start at 0. So cell A4 is on row 3.

        Arguments:

            y -- int
        """
        return self.get_row(y).get_cell_values()


    def set_row_values(self, y, values):
        """Set the values of all cells of the row at the given "y" position.
        It must have the same number of cells.

        Position start at 0. So cell A4 is on row 3.

        Arguments:

            y -- int

            values -- list of Python types
        """
        row = self.get_row(y)
        row.set_cell_values(values)
        self.set_row(y, row)


    def is_row_empty(self, y):
        """Wether all the cells of the row at the given "y" position are
        undefined.

        Position start at 0. So cell A4 is on row 3.

        Arguments:

            y -- int
        """
        return self.get_row(y).is_row_empty()


    #
    # Cells
    #

    def get_cell_list(self, regex=None, style=None):
        """Get the list of cells matching the criteria. Each result is a
        tuple of (x, y, cell).

        Arguments:

            regex -- unicode

            style -- unicode

        Return: list of tuples
        """
        cells = []
        for y, row in enumerate(self.traverse_rows()):
            for x, cell in row.get_cell_list(regex=regex, style=style):
                cells.append((x, y, cell))
        # Return the coordinates and element
        return cells


    def get_cell(self, coordinates):
        """Get the cell at the given coordinates.

        They are either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4".

        A  copy is returned, use ``set_cell`` to push it back.

        Arguments:

            coordinates -- (int, int) or str

        Return: odf_cell
        """
        x, y = _get_cell_coordinates(coordinates)
        y = self.__check_y(y)
        for h, row in enumerate(self.traverse_rows()):
            if h == y:
                return row.get_cell(x)


    def get_cell_value(self, coordinates):
        """Get the Python value of the cell at the given coordinates.

        They are either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4".
        Arguments:

            coordinates -- (int, int) or str

        Return: Python type
        """
        return self.get_cell().get_cell_value()


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
                row.set_cell(x, cell)
                self.set_row(h, row)


    def set_cell_value(self, coordinates, value):
        """Set the Python value of the cell at the given coordinates.

        They are either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4".

        Arguments:

            coordinates -- (int, int) or str

            value -- Python type
        """
        self.set_cell(coordinates, odf_create_cell(value))


    def set_cell_image(self, coordinates, image_frame):
        """Do all the magic to display an image in the cell at the given
        coordinates.

        They are either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4".

        The frame element must contain the expected image position and
        dimensions.

        Arguments:

            coordinates -- (int, int) or str

            image_frame -- odf_frame including an image
        """
        x, y = _get_cell_coordinates(coordinates)
        x = _digit_to_alpha(self.__check_x(x))
        y = self.__check_y(y) + 1
        # FIXME what happens when the address changes?
        address = u"%s.%s%s" % (self.get_table_name(), x, y)
        # Naive approach: duplicate attributes
        image_frame = image_frame.clone()
        image_frame.set_frame_anchor_type(None)
        width, height = image_frame.get_frame_size()
        image_frame.set_attribute('table:end-x', width)
        image_frame.set_attribute('table:end-y', height)
        image_frame.set_attribute('table:end-cell-address', address)
        # Remove any previous paragraph, frame, etc.
        cell = self.get_cell(coordinates)
        for child in cell.get_children():
            cell.delete_element(child)
        cell.append_element(image_frame)
        self.set_cell(coordinates, cell)


    def insert_cell(self, coordinates, cell):
        """Insert the given cell at the given coordinates.

        They are either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4".

        Other rows are expanded to maintain width consistency.

        Arguments:

            coordinates -- (int, int) or str

            cell -- odf_cell
        """
        x, y = _get_cell_coordinates(coordinates)
        x = self.__check_x(x)
        y = self.__check_y(y)
        # Repetited cells are accepted
        repeated = cell.get_cell_repeated()
        stub = odf_create_cell(repeated=repeated)
        # Must update width if not done to pass checks
        future_width = self._get_rows()[0].get_row_width() + (repeated or 1)
        if self.get_table_width() != future_width:
            self.insert_column(x, odf_create_column(repeated=repeated))
        # Now an empty column has been inserted
        for h, row in enumerate(self.traverse_rows()):
            if h == y:
                row.set_cell(x, cell)
                self.set_row(h, row)


    def append_cell(self, y, cell):
        """Append the given cell at the "y" coordinate. Repeated cells are
        accepted.

        Position start at 0. So cell A4 is on row 3.

        Other rows are expanded to maintain width consistency.

        Arguments:

            y -- int

            cell -- odf_cell
        """
        y = self.__check_y(y)
        # Repetited cells are accepted
        repeated = cell.get_cell_repeated()
        stub = odf_create_cell(repeated=repeated)
        # Must update width if not done to pass checks
        future_width = self._get_rows()[0].get_row_width() + (repeated or 1)
        if self.get_table_width() != future_width:
            self.append_column(odf_create_column(repeated=repeated))
        # Now an empty column has been appended
        for h, row in enumerate(self.traverse_rows()):
            if h == y:
                row.set_cell(future_width - 1, cell)
                self.set_row(h, row)
                return


    def delete_cell(self, coordinates):
        """Delete the cell at the given coordinates.

        They are either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4".

        Other rows are reduced to maintain width consistency.

        Arguments:

            coordinates -- (int, int) or str
        """
        x, y = _get_cell_coordinates(coordinates)
        x = self.__check_x(x)
        y = self.__check_y(y)
        # Must update width if not done to pass checks
        future_width = self._get_rows()[0].get_row_width() - 1
        if self.get_table_width() != future_width:
            self.delete_column(x)
            # Will have deleted cells in rows too
        # Else nothing to do



    #
    # Columns
    #

    def _get_columns(self):
        return self.get_element_list('table:table-column')


    def traverse_columns(self):
        """Yield as many column elements as expected columns in the table,
        i.e. expand repetitions by returning the same column as many times as
        necessary.

        Copies are returned, use ``set_column`` to push them back.
        """
        for column in self._get_columns():
            repeated = column.get_column_repeated() or 1
            for i in xrange(repeated):
                # Return a copy without the now obsolete repetition
                column = column.clone()
                column.set_column_repeated(None)
                yield column


    def get_column_list(self, style=None):
        """Get the list of columns matching the criteria. Each result is a
        tuple of (x, column).

        The original column elements are returned, with their repetition
        attribute.

        Arguments:

            style -- unicode

        Return: list of tuples
        """
        columns = []
        for w, column in enumerate(self.traverse_columns()):
            if style and style != column.get_column_style():
                continue
            columns.append((w, column))
        return columns


    def get_column(self, x):
        """Get the column at the given "x" position.

        ODF columns don't contain cells, only style information.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        A copy is returned, use ``set_column`` to push it back.

        Arguments:

            x -- int or str.isalpha()

        Return: odf_column
        """
        x = self.__check_x(x)
        for w, column in enumerate(self.traverse_columns()):
            if w == x:
                return column


    def set_column(self, x, column):
        """Replace the column at the given "x" position.

        ODF columns don't contain cells, only style information.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        Arguments:

            x -- int or str.isalpha()

            column -- odf_column
        """
        x = self.__check_x(x)
        _set_element(x, column, self._get_columns(),
                odf_column.get_column_repeated,
                odf_column.set_column_repeated)



    def insert_column(self, x, column):
        """Insert the column before the given "x" position.

        ODF columns don't contain cells, only style information.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        Arguments:

            x -- int or str.isalpha()

            column -- odf_column
        """
        x = self.__check_x(x)
        _insert_element(x, column, self._get_columns(),
                odf_column.get_column_repeated,
                odf_column.set_column_repeated)
        # Update width if not done
        width = self.get_table_width()
        for row in self._get_rows():
            if row.get_row_width() != width:
                row.insert_cell(x, odf_create_cell())


    def append_column(self, column):
        """Append the column at the end of the table.

        ODF columns don't contain cells, only style information.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        Arguments:

            column -- odf_column
        """
        self.append_element(column)
        # Update width if not done
        width = self.get_table_width()
        for row in self._get_rows():
            if row.get_row_width() != width:
                row.append_cell(odf_create_cell())


    def delete_column(self, x):
        """Delete the column at the given position. ODF columns don't contain
        cells, only style information.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        Arguments:

            x -- int or str.isalpha()
        """
        x = self.__check_x(x)
        _delete_element(x, self._get_columns(),
                odf_column.get_column_repeated,
                odf_column.set_column_repeated)
        # Update width if not done
        width = self.get_table_width()
        for row in self._get_rows():
            if row.get_row_width() != width:
                row.delete_cell(x)


    def get_column_cells(self, x):
        """Get the list of cells at the given position.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        Arguments:

            x -- int or str.isalpha()

        Return: list of odf_cell
        """
        return [row.get_cell(x) for row in self.traverse_rows()]


    def get_column_cell_values(self, x):
        """Get the list of Python values for the cells at the given position.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        Arguments:

            x -- int or str.isalpha()

        Return: list of Python types
        """
        return [cell.get_cell_value() for cell in self.get_column_cells(x)]


    def set_column_cells(self, x, cells):
        """Set the list of cells at the given position.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        The list must have the same length than the table height.

        Arguments:

            x -- int or str.isalpha()

            cells -- list of odf_cell
        """
        height = self.get_table_height()
        if len(cells) != height:
            raise ValueError, "col mismatch: %s cells expected" % height
        cells = iter(cells)
        for y, row in enumerate(self.traverse_rows()):
            row.set_cell(x, cells.next())
            self.set_row(y, row)


    def set_column_cell_values(self, x, values):
        """Set the list of Python values of cells at the given position.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        The list must have the same length than the table height.

        Arguments:

            x -- int or str.isalpha()

            values -- list of Python types
        """
        cells = [odf_create_cell(value) for value in values]
        self.set_column_cells(x, cells)


    def is_column_empty(self, x):
        """Wether all the cells at the given position are empty.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        Return: bool
        """
        for cell in self.get_column_cells(x):
            if (cell.get_cell_style() is not None
                    or cell.get_cell_value() is not None):
                return False
        return True



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
            for value in row.get_cell_values():
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
    # Make the columns (FIXME by hand)
    table.insert_element(odf_create_column(repeated=len(line)), position=0)
    return table



# Register
register_element_class('table:table-cell', odf_cell)
register_element_class('table:covered-table-cell', odf_cell)
register_element_class('table:table-row', odf_row)
register_element_class('table:table-column', odf_column)
register_element_class('table:table', odf_table)
