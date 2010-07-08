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
from cStringIO import StringIO
from csv import reader, Sniffer
from textwrap import wrap

# Import from lpod
from datatype import Boolean, Date, DateTime, Duration
from element import odf_create_element, register_element_class, odf_element
from utils import get_value, _set_value_and_type


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
    pos = 0
    for real_element in real_elements:
        repeated = get_repeated(real_element) or 1
        for current_repetition in xrange(repeated):
            if pos == position:
                # Repetitions start counting at 1
                current_repetition += 1
                break
            pos += 1
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
            parent.delete(real_element)
            index -= 1
        # Insert new element
        parent.insert(new_element.clone(), position=index + 1, )
        # Insert the remaining repetitions
        if repeated_after:
            element_after = real_element.clone()
            set_repeated(element_after, repeated_after)
            parent.insert(element_after, position=index + 2)
        return



def _insert_element(position, new_element, real_elements, get_repeated,
        set_repeated):
    pos = 0
    for real_element in real_elements:
        repeated = get_repeated(real_element) or 1
        for current_repetition in xrange(repeated):
            if pos == position:
                # Repetitions start counting at 1
                current_repetition += 1
                break
            pos += 1
        else:
            # Not found on this(these) element(s)
            continue
        parent = real_element.get_parent()
        index = parent.index(real_element)
        if repeated == 1 or current_repetition == 1:
            # Just insert before
            parent.insert(new_element.clone(), position=index)
        else:
            repeated_after = repeated - current_repetition + 1
            repeated_before = current_repetition - 1
            # Update repetition
            set_repeated(real_element, repeated_before)
            # Insert new element
            parent.insert(new_element.clone(), position=index + 1)
            # Insert the remaining repetitions
            if repeated_after:
                element_after = real_element.clone()
                set_repeated(element_after, repeated_after)
                parent.insert(element_after, position=index + 2)
        return



def _delete_element(position, real_elements, get_repeated, set_repeated):
    pos = 0
    for real_element in real_elements:
        repeated = get_repeated(real_element) or 1
        for current_repetition in xrange(repeated):
            if pos == position:
                break
            pos += 1
        else:
            # Not found on this(these) element(s)
            continue
        # Lost 1 credit
        repeated -= 1
        if repeated:
            set_repeated(real_element, repeated)
        else:
            # Game over
            real_element.delete()
        return



def odf_create_cell(value=None, text=None, cell_type=None, currency=None,
        repeated=None, style=None):
    """Create a cell element containing the given value. The textual
    representation is automatically formatted but can be provided. Cell type
    can be deduced as well, unless the number is a percentage or currency. If
    cell type is "currency", the currency must be given. The cell can be
    repeated on the given number of columns.

    Arguments:

        value -- bool, int, float, Decimal, date, datetime, str, unicode,
                 timedelta

        text -- unicode

        cell_type -- 'boolean', 'currency', 'date', 'float', 'percentage',
                     'string' or 'time'

        currency -- three-letter str

        repeated -- int

        style -- unicode

    Return: odf_cell
    """

    element = odf_create_element('table:table-cell')
    element.set_value(value, text=text, cell_type=cell_type,
            currency=currency)
    if repeated and repeated > 1:
        element.set_repeated(repeated)
    if style is not None:
        element.set_stylename(style)
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
    element = odf_create_element('table:table-row')
    if width is not None:
        for i in xrange(width):
            element.append(odf_create_cell())
    if repeated:
        element.set_repeated(repeated)
    if style is not None:
        element.set_stylename(style)
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
            element.append(row)
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
    element = odf_create_element('table:table-column')
    if default_cell_style:
        element.set_default_cell_style(default_cell_style)
    if repeated and repeated > 1:
        element.set_repeated(repeated)
    if style:
        element.set_stylename(style)
    return element



def odf_create_header_rows():
    return odf_create_element('table:table-header-rows')



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
    element = odf_create_element('table:table')
    element.set_name(name)
    if protected:
        if protection_key is None:
            raise ValueError, "missing protection key"
        # TODO
        raise NotImplementedError, "protected"
        element.set_protected(protected)
    if not display:
        element.set_displayed(display)
    if not printable:
        element.set_printable(printable)
    if print_ranges:
        element.set_print_ranges(print_ranges)
    if style:
        element.set_stylename(style)
    # Prefill the table
    if width is not None or height is not None:
        width = width or 1
        height = height or 1
        # Column groups for style information
        columns = odf_create_column(repeated=width)
        element.append(columns)
        for i in xrange(height):
            row = odf_create_row(width)
            element.append(row)
    return element



class odf_cell(odf_element):
    """Class for the table cell element.
    """

    def get_value(self):
        """Get the Python value that represent the cell.

        Possible return types are unicode, int, Decimal, datetime,
        timedelta.

        Return: Python type
        """
        return get_value(self)


    def set_value(self, value, text=None, cell_type=None, currency=None):
        """Set the cell state from the Python value type.

        Text is how the cell is displayed. Cell type is guessed,
        unless provided.

        For monetary values, provide the name of the currency.

        Arguments:

            value -- Python type

            text -- unicode

            cell_type -- 'boolean', 'float', 'date', 'string' or 'time'

            currency -- unicode
        """
        text = _set_value_and_type(self, value=value, text=text,
                value_type=cell_type, currency=currency)
        if text is not None:
            self.set_text_content(text)


    def get_type(self):
        """Get the type of the cell: boolean, float, date, string or time.

        Return: str
        """
        return self.get_attribute('office:value-type')


    def set_type(self, cell_type):
        """Set the type ofthe cell manually.

        Arguments:

            cell_type -- 'boolean', 'float', 'date', 'string' or 'time'
        """
        self.set_attribute('office:value-type', cell_type)


    def get_currency(self):
        """Get the currency used for monetary values.
        """
        return self.get_attribute('office:currency')


    def set_currency(self, currency):
        """Set the currency used for monetary values.

        Arguments:

            currency -- unicode
        """
        self.set_attribute('office:currency', currency)


    def get_repeated(self):
        """Get the number of times the cell is repeated.

        Always None when using the table API.

        Return: int or None
        """
        repeated = self.get_attribute('table:number-columns-repeated')
        if repeated is None:
            return None
        return int(repeated)


    def set_repeated(self, repeated):
        """Set the numnber of times the cell is repeated, or None to delete
        it.

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


    def get_stylename(self):
        """Get the style of the cell itself.

        Return: unicode
        """
        return self.get_attribute('table:style-name')


    def set_stylename(self, style):
        """Set the style of the cell itself.

        Arguments:

            style -- unicode
        """
        self.set_attribute('table:style-name', style)


    def get_formula(self):
        """Get the formula of the cell, or None if undefined.

        The formula is not interpreted in any way.

        Return: unicode
        """
        return self.get_attribute('table:formula')


    def set_formula(self, formula):
        """Set the formula of the cell, or None to remove it.

        The formula is not interpreted in any way.

        Arguments:

            formula -- unicode
        """
        self.set_attribute('table:formula', formula)



class odf_row(odf_element):

    # Private API

    def _get_cells(self):
        return self.get_element_list(
                '(table:table-cell|table:covered-table-cell)')


    def _translate_x(self, x):
        x = _alpha_to_digit(x)
        if x < 0:
            x = self.get_width() + x
        return x


    # Public API

    def get_repeated(self):
        """Get the number of times the row is repeated.

        Always None when using the table API.

        Return: int or None
        """
        repeated = self.get_attribute('table:number-rows-repeated')
        if repeated is None:
            return None
        return int(repeated)


    def set_repeated(self, repeated):
        """Set the numnber of times the row is repeated, or None to delete
        it.

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


    def get_stylename(self):
        """Get the style of the row itself.

        Return: unicode
        """
        return self.get_attribute('table:style-name')


    def set_stylename(self, style):
        """Set the style of the row itself.

        Arguments:

            style -- unicode
        """
        self.set_attribute('table:style-name', style)


    def get_width(self):
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


    def traverse(self):
        """Yield as many cell elements as expected cells in the row, i.e.
        expand repetitions by returning the same cell as many times as
        necessary.

        Copies are returned, use ``set_cell`` to push them back.
        """
        for cell in self._get_cells():
            repeated = cell.get_repeated() or 1
            for i in xrange(repeated):
                # Return a copy without the now obsolete repetition
                cell = cell.clone()
                cell.set_repeated(None)
                yield cell


    def get_cell_list(self, style=None, content=None):
        """Get the list of cells matching the criteria. Each result is a
        tuple of (x, y, cell).

        Arguments:

            regex -- unicode

            style -- unicode

        Return: list of tuples
        """
        cells = []
        for x, cell in enumerate(self.traverse()):
            # Filter the cells with the regex
            if content and not cell.match(content):
                continue
            # Filter the cells with the style
            if style and style != cell.get_stylename():
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
        x = self._translate_x(x)
        # Outside the defined row
        if x >= self.get_width():
            return odf_create_cell()
        # Inside the defined row
        cell_number = 0
        for cell in self._get_cells():
            repeated = cell.get_repeated() or 1
            for i in xrange(repeated):
                if cell_number == x:
                    # Return a copy without the now obsolete repetition
                    cell = cell.clone()
                    cell.set_repeated(None)
                    return cell
                cell_number += 1


    def get_value(self, x):
        """Shortcut to get the value of the cell at position "x".

        See ``get_cell`` and ``odf_cell.get_value``.
        """
        return self.get_cell(x).get_value()


    def set_cell(self, x, cell=None):
        """Push the cell back in the row at position "x" starting from 0.
        Alphabetical positions like "D" are accepted.

        Arguments:

            x -- int or str
        """
        if cell is None:
            cell = odf_create_cell()
        x = self._translate_x(x)
        # Outside the defined row
        diff = x - self.get_width()
        if diff > 0:
            self.append_cell(odf_create_cell(repeated=diff))
            self.append_cell(cell.clone())
            return
        # Inside the defined row
        _set_element(x, cell, self._get_cells(), odf_cell.get_repeated,
                odf_cell.set_repeated)


    def set_value(self, x, value):
        """Shortcut to set the value of the cell at position "x".

        See ``get_cell`` and ``odf_cell.get_value``.
        """
        self.set_cell(x, odf_create_cell(value))


    def insert_cell(self, x, cell=None):
        """Insert the given cell at position "x" starting from 0. If no cell
        is given, an empty one is created.

        Alphabetical positions like "D" are accepted.

        Do not use when working on a table, use ``odf_table.insert_cell``.

        Arguments:

            x -- int or str

            cell -- odf_cell
        """
        if cell is None:
            cell = odf_create_cell()
        x = self._translate_x(x)
        # Outside the defined row
        diff = x - self.get_width()
        if diff > 0:
            self.append_cell(odf_create_cell(repeated=diff))
            self.append_cell(cell.clone())
            return
        # Inside the defined row
        # Inserting a repeated cell accepted
        _insert_element(x, cell, self._get_cells(),
                odf_cell.get_repeated, odf_cell.set_repeated)
        return cell


    def append_cell(self, cell=None):
        """Append the given cell at the end of the row. Repeated cells are
        accepted. If no cell is given, an empty one is created.

        Do not use when working on a table, use ``odf_table.append_cell``.

        Arguments:

            cell -- odf_cell
        """
        if cell is None:
            cell = odf_create_cell()
        self.append(cell)
        return cell


    def delete_cell(self, x):
        """Delete the cell at the given position "x" starting from 0.
        Alphabetical positions like "D" are accepted.

        Cells on the right will be shifted to the left. In a table, other
        rows remain unaffected.

        Arguments:

            x -- int or str
        """
        x = self._translate_x(x)
        # Outside the defined row
        if x >= self.get_width():
            return
        # Inside the defined row
        _delete_element(x, self._get_cells(), odf_cell.get_repeated,
                odf_cell.set_repeated)


    def get_values(self):
        """Shortcut to get the list of all cell values in this row.

        Return: list of Python types
        """
        return [cell.get_value() for cell in self.traverse()]


    def set_values(self, values):
        """Shortcut to set the list of all cell values in this row.

        Arguments:

            values -- list of Python types
        """
        width = self.get_width()
        for x, value in enumerate(values[:width]):
            self.set_value(x, value)
        for value in values[width:]:
            self.append_cell(odf_create_cell(value))


    def rstrip(self, aggressive=False):
        """Remove *in-place* empty cells at the right of the row. An empty
        cell has no value but can have style. If "aggressive" is True, style
        is ignored.

        Arguments:

            aggressive -- bool
        """
        for cell in reversed(self._get_cells()):
            if cell.get_value():
                return
            if not aggressive and cell.get_stylename() is not None:
                return
            self.delete(cell)


    def is_empty(self, aggressive=False):
        """Return wether every cell in the row has no value or the value
        evaluates to False (empty string), and no style.

        If aggressive is True, empty cells with style are considered empty.

        Arguments:

            aggressive -- bool

        Return: bool
        """
        for cell in self._get_cells():
            if cell.get_value() is not None:
                return False
            if not aggressive and cell.get_stylename() is not None:
                return False
        return True



class odf_row_group(odf_element):
    """Class to group rows with common properties.
    """
    # TODO
    pass



class odf_column(odf_element):

    def get_default_cell_style(self):
        return self.get_attribute('table:default-cell-style-name')


    def set_default_cell_style(self, style):
        self.set_attribute('table:default-cell-style-name', style)


    def get_repeated(self):
        """Get the number of times the column is repeated.

        Always None when using the table API.

        Return: int or None
        """
        repeated = self.get_attribute('table:number-columns-repeated')
        if repeated is None:
            return None
        return int(repeated)


    def set_repeated(self, repeated):
        """Set the numnber of times the column is repeated, or None to delete
        it.

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


    def get_stylename(self):
        return self.get_attribute('table:style-name')


    def set_stylename(self, style):
        self.set_attribute('table:style-name', style)



class odf_table(odf_element):
    #
    # Private API
    #

    def _translate_x(self, x):
        x = _alpha_to_digit(x)
        if x < 0:
            x = self.get_width() + x
        return x


    def _translate_y(self, y):
        # "3" (couting from 1) -> 2 (couting from 0)
        if isinstance(y, str):
            y = int(y) - 1
        if y < 0:
            y = self.get_height() + y
        return y


    def _translate_coordinates(self, coordinates):
        x, y = _get_cell_coordinates(coordinates)
        if x < 0:
            x = self.get_width() + x
        y = self._translate_y(y)
        return (x, y)


    def __update_width(self, row):
        """Synchronize the number of columns if the row is bigger.

        Append, don't insert, not to disturb the current layout.
        """
        diff = row.get_width() - self.get_width()
        if diff > 0:
            self.append_column(odf_create_column(repeated=diff))


    def __get_formatted_text_normal(self, context):
        result = []
        for row in self.traverse():
            for cell in row.traverse():
                value = get_value(cell, try_get_text=False)
                # None ?
                if value is None:
                    # Try with get_formatted_text on the elements
                    value = []
                    for element in cell.get_children():
                        value.append(element.get_formatted_text(context))
                    value = u''.join(value)
                else:
                    value = unicode(value)
                result.append(value)
                result.append(u'\n')
            result.append(u'\n')
        return u''.join(result)


    def __get_formatted_text_rst(self, context):
        # Strip the table => We must clone
        table = self.clone()
        table.rstrip(aggressive=True)

        # Fill the rows
        rows = []
        cols_nb = 0
        cols_size = {}
        for odf_row in table.traverse():
            row = []
            for i, cell in enumerate(odf_row.traverse()):
                value = get_value(cell, try_get_text=False)
                # None ?
                if value is None:
                    # Try with get_formatted_text on the elements
                    value = []
                    for element in cell.get_children():
                        value.append(element.get_formatted_text(context))
                    value = u''.join(value)
                else:
                    value = unicode(value)
                value = value.strip()
                # Strip the empty columns
                if value:
                    cols_nb = max(cols_nb, i + 1)
                # Compute the size of each columns
                cols_size[i] = max(cols_size.get(i, 0), len(value))
                # Append
                row.append(value)
            rows.append(row)

        # Nothing ?
        if cols_nb == 0:
            return u''

        # Prevent a crash with empty columns (by example with images)
        for col, size in cols_size.iteritems():
            if size == 0:
                cols_size[col] = 1

        # Update cols_size
        LINE_MAX = 100
        COL_MIN = 16

        free_size = LINE_MAX - (cols_nb - 1) * 3 - 4
        real_size = sum([ cols_size[i] for i in range(cols_nb) ])
        if real_size > free_size:
            factor = float(free_size) / real_size

            for i in range(cols_nb):
                old_size = cols_size[i]

                # The cell is already small
                if old_size <= COL_MIN:
                    continue

                new_size = int(factor * old_size)

                if new_size < COL_MIN:
                    new_size = COL_MIN
                cols_size[i] = new_size

        # Convert !
        result = [u'']
        # Construct the separated line
        line = [u'+']
        for i in range(cols_nb):
            line.append(u'-' * (cols_size[i] + 2))
            line.append(u'+')
        line = u''.join(line)

        # Add the lines
        result.append(line)
        for row in rows:
            # Wrap the row
            wrapped_row = []
            for i, value in enumerate(row[:cols_nb]):
                wrapped_value = []
                for part in value.split('\n'):
                    # Hack to handle correctly the lists or the directives
                    subsequent_indent = ''
                    part_lstripped = part.lstrip()
                    if (part_lstripped.startswith('-') or
                        part_lstripped.startswith('..')):
                        subsequent_indent = ' ' * (len(part) \
                                                   - len(part.lstrip()) \
                                                   + 2)
                    wrapped_part = wrap(part, width=cols_size[i],
                                        subsequent_indent=subsequent_indent)
                    if wrapped_part:
                        wrapped_value.extend(wrapped_part)
                    else:
                        wrapped_value.append('')
                wrapped_row.append(wrapped_value)

            # Append!
            for j in range(max([len(values) for values in wrapped_row ])):
                txt_row = [u'|']
                for i, values in enumerate(wrapped_row):
                    # An empty cell ?
                    if len(values) - 1 < j:
                        txt_row.append(u' ' * (cols_size[i] + 2))
                        txt_row.append(u'|')
                        continue

                    # Not empty
                    value = values[j]
                    txt_row.append(u' ')
                    txt_row.append(value)
                    txt_row.append(u' ' * (cols_size[i] - len(value) + 1))
                    txt_row.append(u'|')
                txt_row = u''.join(txt_row)
                result.append(txt_row)

            result.append(line)
        result.append(u'')
        result = u'\n'.join(result)

        return result

    #
    # Public API
    #


    def get_height(self):
        """Get the current height of the table.

        Return: int
        """
        rows = self._get_rows()
        repeated = self.xpath('table:table-row/@table:number-rows-repeated')
        unrepeated = len(rows) - len(repeated)
        return sum(int(r) for r in repeated) + unrepeated


    def get_width(self):
        """Get the current width of the table, measured on columns.

        Rows may have different widths, use the odf_table API to ensure width
        consistency.

        Return: int
        """
        # Columns are our reference for user expected width
        columns = self._get_columns()
        repeated = self.xpath(
                'table:table-column/@table:number-columns-repeated')
        unrepeated = len(columns) - len(repeated)
        return sum(int(r) for r in repeated) + unrepeated


    def get_size(self):
        """Shortcut to get the current width and height of the table.

        Return: (int, int)
        """
        return self.get_width(), self.get_height()


    def get_name(self):
        return self.get_attribute('table:name')


    def set_name(self, name):
        self.set_attribute('table:name', name)


    def get_protected(self):
        return self.get_attribute('table:protected') == 'true'


    def set_protected(self, protect):
        self.set_boolean_attribute('table:protected', protect)


    def get_displayed(self):
        return self.get_boolean_attribute('table:display') is True


    def set_displayed(self, display):
        self.set_boolean_attribute('table:display', display)


    def get_printable(self):
        printable = self.get_attribute('table:print')
        # Default value
        if printable is None:
            printable = 'true'
        return printable == 'true'


    def set_printable(self, printable):
        self.set_boolean_attribute('table:print', printable)


    def get_print_ranges(self):
        return self.get_attribute('table:print-ranges').split()


    def set_print_ranges(self, print_ranges):
        if isinstance(print_ranges, (tuple, list)):
            print_ranges = ' '.join(print_ranges)
        self.set_attribute('table:print-ranges', print_ranges)


    def get_stylename(self):
        return self.get_attribute('table:style-name')


    def set_stylename(self, style):
        self.set_attribute('table:style-name', style)


    def get_formatted_text(self, context):
        if context["rst_mode"]:
            return self.__get_formatted_text_rst(context)
        else:
            return self.__get_formatted_text_normal(context)


    def get_values(self):
        """Get a matrix of all Python values of the table.

        Return: list of lists
        """
        data = []
        width = self.get_width()
        for row in self.traverse():
            values = row.get_values()
            # Complement row to match column width
            values.extend([None] * (width - len(values)))
            data.append(values)
        return data


    def iter_values(self):
        """Iterate through lines of Python values of the table.

        Return: iterator of lists
        """
        width = self.get_width()
        for row in self.traverse():
            values = row.get_values()
            # Complement row to match column width
            values.extend([None] * (width - len(values)))
            yield values


    def set_values(self, values):
        """Set all Python values for the whole table.

        A list of lists is expected, with as many lists as rows, and as many
        items in each sublist as cells.

        Arguments:

            values -- list of lists
        """
        values = iter(values)
        for y, row in enumerate(self.traverse()):
            row.set_values(values.next())
            self.set_row(y, row)


    def rstrip(self, aggressive=False):
        """Remove *in-place* empty rows below and empty cells at the right of
        the table. Cells are empty if they contain no value or it evaluates
        to False, and no style.

        If aggressive is True, empty cells with style are removed too.

        Argument:

            aggressive -- bool
        """
        # Step 1: remove empty rows below the table
        for row in reversed(self._get_rows()):
            if row.is_empty(aggressive=aggressive):
                row.get_parent().delete(row)
            else:
                break
        # Step 2: rstrip remaining rows
        max_width = 0
        for row in self._get_rows():
            row.rstrip(aggressive=aggressive)
            # keep count of the biggest row
            max_width = max(max_width, row.get_width())
        # Step 3: trim columns to match max_width
        diff = self.get_width() - max_width
        if diff > 0:
            for column in reversed(self._get_columns()):
                repeated = column.get_repeated() or 1
                repeated = repeated - diff
                if repeated > 0:
                    column.set_repeated(repeated)
                    break
                else:
                    column.get_parent().delete(column)
                    diff = -repeated
                    if diff == 0:
                        break


    def is_empty(self, aggressive=False):
        """Return wether every cell in the table has no value or the value
        evaluates to False (empty string), and no style.

        If aggressive is True, empty cells with style are considered empty.

        Arguments:

            aggressive -- bool
        """
        for row in self._get_rows():
            if not row.is_empty(aggressive=aggressive):
                return False
        return True


    #
    # Rows
    #

    def _get_rows(self):
        return self.get_element_list('table:table-row')


    def traverse(self):
        """Yield as many row elements as expected rows in the table, i.e.
        expand repetitions by returning the same row as many times as
        necessary.

        Copies are returned, use ``set_row`` to push them back.
        """
        for row in self._get_rows():
            repeated = row.get_repeated() or 1
            for i in xrange(repeated):
                # Return a copy without the now obsolete repetition
                row = row.clone()
                row.set_repeated(None)
                yield row


    def get_row_list(self, style=None, content=None):
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
        for y, row in enumerate(self.traverse()):
            if content and not row.match(content):
                continue
            if style and style != row.get_stylename():
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
        y = self._translate_y(y)
        # Outside the defined table
        if y >= self.get_height():
            return odf_create_row()
        # Inside the defined table
        for h, row in enumerate(self.traverse()):
            if h == y:
                return row


    def set_row(self, y, row=None):
        """Replace the row at the given position with the new one. It must
        have the same number of cells. Repetion of the old row will be
        adjusted.

        Position start at 0. So cell A4 is on row 3.

        Arguments:

            y -- int

            row -- odf_row
        """
        if row is None:
            row = odf_create_row()
        y = self._translate_y(y)
        # Outside the defined table
        diff = y - self.get_height()
        if diff > 0:
            self.append_row(odf_create_row(repeated=diff))
            self.append_row(row.clone())
            return
        # Inside the defined table
        # Setting a repeated row accepted
        _set_element(y, row, self._get_rows(), odf_row.get_repeated,
                odf_row.set_repeated)


    def insert_row(self, y, row=None):
        """Insert the row before the given "y" position. It must have the
        same number of cells. If no row is given, an empty one is created.

        Position start at 0. So cell A4 is on row 3.

        Arguments:

            y -- int

            row -- odf_row
        """
        if row is None:
            row = odf_create_row()
        y = self._translate_y(y)
        # Outside the defined table
        diff = y - self.get_height()
        if diff > 0:
            self.append_row(odf_create_row(repeated=diff))
            self.append_row(row.clone())
            return row
        # Inside the defined table
        # Inserting a repeated row accepted
        _insert_element(y, row, self._get_rows(), odf_row.get_repeated,
                odf_row.set_repeated)
        # Update width if necessary
        self.__update_width(row)
        return row


    def append_row(self, row=None):
        """Append the row at the end of the table. If no row is given, an
        empty one is created.

        Position start at 0. So cell A4 is on row 3.

        Note the columns are automatically created when the first row is
        inserted in an empty table. So better insert a filled row.

        Arguments:

            row -- odf_row
        """
        if row is None:
            row = odf_create_row(self.get_width())
        # Appending a repeated row accepted
        # Do not insert next to the last row because it could be in a group
        self.append(row)
        # Initialize columns
        if not self._get_columns():
            repeated = row.get_width()
            self.insert(odf_create_column(repeated=repeated),
                    position=0)
        return row


    def delete_row(self, y):
        """Delete the row at the given "y" position.

        Position start at 0. So cell A4 is on row 3.

        Arguments:

            y -- int
        """
        y = self._translate_y(y)
        # Outside the defined table
        if y >= self.get_height():
            return
        # Inside the defined table
        _delete_element(y, self._get_rows(), odf_row.get_repeated,
                odf_row.set_repeated)


    def get_row_values(self, y):
        """Shortcut to get the list of Python values for the cells of the row
        at the given "y" position.

        Position start at 0. So cell A4 is on row 3.

        Arguments:

            y -- int
        """
        values = self.get_row(y).get_values()
        values.extend([None] * (self.get_width() - len(values)))
        return values


    def set_row_values(self, y, values):
        """Shortcut to set the values of all cells of the row at the given
        "y" position.

        Position start at 0. So cell A4 is on row 3.

        Arguments:

            y -- int

            values -- list of Python types
        """
        row = self.get_row(y)
        row.set_values(values)
        self.set_row(y, row)


    def is_row_empty(self, y, aggressive=False):
        """Return wether every cell in the row at the given "y" position has
        no value or the value evaluates to False (empty string), and no style.

        Position start at 0. So cell A4 is on row 3.

        If aggressive is True, empty cells with style are considered empty.

        Arguments:

            y -- int

            aggressive -- bool
        """
        return self.get_row(y).is_empty(aggressive=aggressive)


    #
    # Cells
    #

    def get_cell_list(self, style=None, content=None):
        """Get the list of cells matching the criteria. Each result is a
        tuple of (x, y, cell).

        Arguments:

            regex -- unicode

            style -- unicode

        Return: list of tuples
        """
        cells = []
        for y, row in enumerate(self.traverse()):
            for x, cell in row.get_cell_list(style=style, content=content):
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
        x, y = self._translate_coordinates(coordinates)
        # Outside the defined table
        if y >= self.get_height():
            return odf_create_cell()
        # Inside the defined table
        for h, row in enumerate(self.traverse()):
            if h == y:
                return row.get_cell(x)


    def get_value(self, coordinates):
        """Shortcut to get the Python value of the cell at the given
        coordinates.

        They are either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4".
        Arguments:

            coordinates -- (int, int) or str

        Return: Python type
        """
        return self.get_cell().get_value()


    def set_cell(self, coordinates, cell=None):
        """Replace a cell of the table at the given coordinates.

        They are either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4".

        Arguments:

            coordinates -- (int, int) or str

            cell -- odf_cell
        """
        if cell is None:
            cell = odf_create_cell()
        x, y = self._translate_coordinates(coordinates)
        # Outside the defined table
        diff = y - self.get_height()
        if diff > 0:
            self.append_row(odf_create_row(repeated=diff))
            row = odf_create_row()
            row.set_cell(x, cell.clone())
            self.append_row(row)
            return
        # Inside the defined table
        for h, row in enumerate(self.traverse()):
            if h == y:
                row.set_cell(x, cell)
                self.set_row(h, row)
                return


    def set_value(self, coordinates, value):
        """Set the Python value of the cell at the given coordinates.

        They are either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4".

        Arguments:

            coordinates -- (int, int) or str

            value -- Python type
        """
        self.set_cell(coordinates, odf_create_cell(value))


    def set_cell_image(self, coordinates, image_frame, type=None):
        """Do all the magic to display an image in the cell at the given
        coordinates.

        They are either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4".

        The frame element must contain the expected image position and
        dimensions.

        Image insertion depends on the document type, so the type must be
        provided or the table element must be already attached to a document.

        Arguments:

            coordinates -- (int, int) or str

            image_frame -- odf_frame including an image

            type -- 'spreadsheet' or 'text'
        """
        # Test document type
        if type is None:
            body = self.get_body()
            if body is None:
                raise ValueError, "document type not found"
            type = {'office:spreadsheet': 'spreadsheet',
                    'office:text': 'text'}.get(body.get_tag())
            if type is None:
                raise ValueError, "document type not supported for images"
        # We need the end address of the image
        x, y = self._translate_coordinates(coordinates)
        cell = self.get_cell((x, y))
        image_frame = image_frame.clone()
        # Remove any previous paragraph, frame, etc.
        for child in cell.get_children():
            cell.delete(child)
        # Now it all depends on the document type
        if type == 'spreadsheet':
            image_frame.set_frame_anchor_type(None)
            # The frame needs end coordinates
            width, height = image_frame.get_frame_size()
            image_frame.set_attribute('table:end-x', width)
            image_frame.set_attribute('table:end-y', height)
            # FIXME what happens when the address changes?
            address = u"%s.%s%s" % (self.get_name(),
                    _digit_to_alpha(x), y + 1)
            image_frame.set_attribute('table:end-cell-address', address)
            # The frame is directly in the cell
            cell.append(image_frame)
        elif type == 'text':
            # The frame must be in a paragraph
            cell.set_value(u"")
            paragraph = cell.get_element('text:p')
            paragraph.append(image_frame)
        self.set_cell(coordinates, cell)


    def insert_cell(self, coordinates, cell=None):
        """Insert the given cell at the given coordinates. If no cell is
        given, an empty one is created.

        Coordinates are either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4".

        Cells on the right are shifted. Other rows remain untouched.

        Arguments:

            coordinates -- (int, int) or str

            cell -- odf_cell
        """
        if cell is None:
            cell = odf_create_cell()
        x, y = self._translate_coordinates(coordinates)
        # Outside the defined table
        diff = y - self.get_height()
        if diff > 0:
            self.append_row(odf_create_row(repeated=diff))
            row = odf_create_row()
            row.set_cell(x, cell.clone())
            self.append_row(row)
            return cell
        # Inside the defined table
        # Repeated cells are accepted
        repeated = cell.get_repeated() or 1
        # Insert the cell
        for h, row in enumerate(self.traverse()):
            if h == y:
                row_width = row.get_width()
                if row_width <= x:
                    diff = row_width - x
                    if diff > 0:
                        row.append_cell(odf_create_cell(repeated=diff))
                    row.append_cell(cell)
                else:
                    row.insert_cell(x, cell)
                self.set_row(h, row)
                break
        # Update width if necessary
        # Don't insert: we are shifting a single row, not the
        # whole column; just append to match the width
        self.__update_width(row)
        return cell


    def append_cell(self, y, cell=None):
        """Append the given cell at the "y" coordinate. Repeated cells are
        accepted. If no cell is given, an empty one is created.

        Position start at 0. So cell A4 is on row 3.

        Other rows remain untouched.

        Arguments:

            y -- int

            cell -- odf_cell
        """
        if cell is None:
            cell = odf_create_cell()
        y = self._translate_y(y)
        # Outside the defined table
        diff = y - self.get_height()
        if diff > 0:
            self.append_row(odf_create_row(repeated=diff))
            row = odf_create_row()
            row.append_cell(cell.clone())
            self.append_row(row)
            return cell
        # Inside the defined table
        # Repeated cells are accepted
        repeated = cell.get_repeated() or 1
        # Append the cell
        for h, row in enumerate(self.traverse()):
            if h == y:
                row.append_cell(cell)
                self.set_row(h, row)
                break
        # Update width if necessary
        self.__update_width(row)
        return cell


    def delete_cell(self, coordinates):
        """Delete the cell at the given coordinates, so that next cells are
        shifted to the left.

        Coordinates are either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4".

        Use "set_value" for erasing value.

        Arguments:

            coordinates -- (int, int) or str
        """
        x, y = self._translate_coordinates(coordinates)
        # Outside the defined table
        if y >= self.get_height():
            return
        # Inside the defined table
        row = self.get_row(y)
        row.delete_cell(x)
        self.set_row(y, row)


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
            repeated = column.get_repeated() or 1
            for i in xrange(repeated):
                # Return a copy without the now obsolete repetition
                column = column.clone()
                column.set_repeated(None)
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
            if style and style != column.get_stylename():
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
        x = self._translate_x(x)
        # Outside the defined table
        if x >= self.get_width():
            return odf_create_column()
        # Inside the defined table
        for w, column in enumerate(self.traverse_columns()):
            if w == x:
                return column


    def set_column(self, x, column=None):
        """Replace the column at the given "x" position.

        ODF columns don't contain cells, only style information.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        Arguments:

            x -- int or str.isalpha()

            column -- odf_column
        """
        x = self._translate_x(x)
        if column is None:
            column = odf_create_column()
        # Outside the defined table
        diff = x - self.get_width()
        if diff > 0:
            self.append_column(odf_create_column(repeated=diff))
            self.append_column(column.clone())
            return
        # Inside the defined table
        _set_element(x, column, self._get_columns(),
                odf_column.get_repeated,
                odf_column.set_repeated)



    def insert_column(self, x, column=None):
        """Insert the column before the given "x" position. If no column is
        given, an empty one is created.

        ODF columns don't contain cells, only style information.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        Arguments:

            x -- int or str.isalpha()

            column -- odf_column
        """
        if column is None:
            column = odf_create_column()
        x = self._translate_x(x)
        # Outside the defined table
        diff = x - self.get_width()
        if diff > 0:
            self.append_column(odf_create_column(repeated=diff))
            self.append_column(column.clone())
            return column
        # Inside the defined table
        _insert_element(x, column, self._get_columns(),
                odf_column.get_repeated,
                odf_column.set_repeated)
        # Repetitions are accepted
        repeated = column.get_repeated() or 1
        # Update width on every row
        for row in self._get_rows():
            if row.get_width() > x:
                row.insert_cell(x, odf_create_cell(repeated=repeated))
            # Shorter rows don't need insert
            # Longer rows shouldn't exist!
        return column


    def append_column(self, column=None):
        """Append the column at the end of the table. If no column is given,
        an empty one is created.

        ODF columns don't contain cells, only style information.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        Arguments:

            column -- odf_column
        """
        if column is None:
            column = odf_create_column()
        last_column = self._get_columns()[-1]
        self.insert(column, position=self.index(last_column) + 1)
        # Repetitions are accepted
        repeated = column.get_repeated() or 1
        # No need to update row widths
        return column


    def delete_column(self, x):
        """Delete the column at the given position. ODF columns don't contain
        cells, only style information.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        Arguments:

            x -- int or str.isalpha()
        """
        x = self._translate_x(x)
        # Outside the defined table
        if x >= self.get_width():
            return
        # Inside the defined table
        _delete_element(x, self._get_columns(),
                odf_column.get_repeated,
                odf_column.set_repeated)
        # Update width
        width = self.get_width()
        for y, row in enumerate(self._get_rows()):
            if row.get_width() >= width:
                row.delete_cell(x)


    def get_column_cells(self, x):
        """Get the list of cells at the given position.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        Arguments:

            x -- int or str.isalpha()

        Return: list of odf_cell
        """
        x = self._translate_x(x)
        result = []
        for row in self._get_rows():
            cell = row.get_cell(x)
            repeated = row.get_repeated() or 1
            for i in xrange(repeated):
                result.append(cell.clone())
        return result


    def get_column_values(self, x):
        """Shortcut to get the list of Python values for the cells at the
        given position.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        Arguments:

            x -- int or str.isalpha()

        Return: list of Python types
        """
        return [cell.get_value() for cell in self.get_column_cells(x)]


    def set_column_cells(self, x, cells):
        """Set the list of cells at the given position.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        The list must have the same length than the table height.

        Arguments:

            x -- int or str.isalpha()

            cells -- list of odf_cell
        """
        height = self.get_height()
        if len(cells) != height:
            raise ValueError, "col mismatch: %s cells expected" % height
        cells = iter(cells)
        for y, row in enumerate(self.traverse()):
            row.set_cell(x, cells.next())
            self.set_row(y, row)


    def set_column_values(self, x, values):
        """Shortcut to set the list of Python values of cells at the given
        position.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        The list must have the same length than the table height.

        Arguments:

            x -- int or str.isalpha()

            values -- list of Python types
        """
        cells = [odf_create_cell(value) for value in values]
        self.set_column_cells(x, cells)


    def is_column_empty(self, x, aggressive=False):
        """Return wether every cell in the column at "x" position has no value
        or the value evaluates to False (empty string), and no style.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        If aggressive is True, empty cells with style are considered empty.

        Return: bool
        """
        for cell in self.get_column_cells(x):
            if cell.get_value() is not None:
                return False
            if not aggressive and cell.get_stylename() is not None:
                return False
        return True



    #
    # Utilities
    #

    def to_csv(self, path_or_file=None, delimiter=',', quotechar='"',
            lineterminator='\n', encoding='utf-8'):
        """
        Write the table as CSV in the file. If the file is a string, it is
        opened as a local path. Else a open file-like is expected; it will not
        be closed afterwards.

        Arguments:

            path_or_file -- str or file-like

            delimiter -- str

            quotechar -- str

            lineterminator -- str

            encoding -- str
        """
        close_after = False
        if path_or_file is None:
            file = StringIO()
        elif type(path_or_file) is str or type(path_or_file) is unicode:
            file = open(path_or_file, 'wb')
            close_after = True
        quoted = quotechar * 2
        for values in self.iter_values():
            line = []
            for value in values:
                if type(value) is unicode:
                    value = value.encode(encoding)
                if type(value) is str:
                    value = value.strip()
                value = '' if value is None else str(value)
                value = value.replace(quotechar, quoted)
                line.append(quotechar + value + quotechar)
            file.write(delimiter.join(line) + lineterminator)
        if path_or_file is None:
            return file.getvalue()
        if close_after:
            file.close()



def import_from_csv(path_or_file, name, style=None, delimiter=None,
        quotechar=None, lineterminator=None, encoding='utf-8'):
    """Convert the CSV file to an odf_table. If the file is a string, it is
    opened as a local path. Else a open file-like is expected; it will not be
    closed afterwards.

    CSV format can be autodetected to a certain limit, but encoding is
    important.

    Arguments:

      path_or_file -- str or file-like

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
    if type(path_or_file) is str:
        file = open(path_or_file, 'rb')
        data = file.read().splitlines(True)
        file.close()
    else:
        # Leave the file we were given open
        data = path_or_file.read().splitlines(True)
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
        # rstrip line
        while line and not line[-1].strip():
            line.pop()
        for value in line:
            cell = odf_create_cell(_get_python_value(value, encoding))
            row.append_cell(cell)
        table.append_row(row)
    return table



# Register
register_element_class('table:table-cell', odf_cell)
register_element_class('table:covered-table-cell', odf_cell)
register_element_class('table:table-row', odf_row)
register_element_class('table:table-column', odf_column)
register_element_class('table:table', odf_table)
