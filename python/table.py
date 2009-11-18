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
from re import search

# Import from lpod
from datatype import Boolean, Date, DateTime, Duration
from element import odf_create_element, register_element_class, odf_element
from utils import get_value, _set_value_and_type
from vfs import vfs


def _get_cell_coordinates(obj):
    # By (1, 2) ?
    if isinstance(obj, (list, tuple)):
        return tuple(obj)
    # Or by 'B3' notation ?
    if not isinstance(obj, (str, unicode)):
        raise ValueError, 'bad coordinates type: "%s"' % type(obj)
    lowered = obj.lower()
    # First "B"
    column = 0
    for i, c in enumerate(lowered):
        if not c.isalpha():
            break
        v = ord(c) - ord('a') + 1
        column = column * 26 + v
    if column == 0:
        raise ValueError, 'cell name "%s" is malformed' % obj
    # Then "3"
    try:
        line = int(lowered[i:])
    except ValueError:
        raise ValueError, 'cell name "%s" is malformed' % obj
    if line <= 0:
        raise ValueError, 'cell name "%s" is malformed' % obj
    # Indexes start at 0
    return column - 1, line - 1



def _get_python_value(data, encoding):
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



def _insert_elements(elements, target):
    # No elements => nothing to do
    if not elements:
        return

    # At least a element
    current_element = elements[0]
    current_element_serialized = current_element.serialize()
    repeat = 1
    for element in elements[1:]:
        element_serialized = element.serialize()
        if element_serialized == current_element_serialized:
            repeat += 1
        else:
            # Insert the current_element
            if repeat > 1:
                current_element.set_attribute('table:number-columns-repeated',
                                              str(repeat))
            target.append_element(current_element)

            # Current element is now this element
            current_element = element
            current_element_serialized = element_serialized
            repeat = 1

    # Insert the last elements
    if repeat > 1:
        current_element.set_attribute('table:number-columns-repeated',
                                     str(repeat))
    target.append_element(current_element)



def _is_odf_row_empty(odf_row):
    # XXX For the moment, a row is said empty when:
    # 1- It has only a cell
    # 2- This cell has no child
    cells = odf_row.get_element_list(
            'table:table-cell|table:covered-table-cell')
    if len(cells) == 0:
        return True
    elif len(cells) > 1:
        return False

    # If here we have only a cell
    cell = cells[0]
    if len(cell.get_element_list('*')) > 0:
        return False

    return True



def _append_odf_row(odf_row, rows):
    # Delete the table:number-rows-repeated
    row_repeat = odf_row.get_attribute('table:number-rows-repeated')
    if row_repeat is not None:
        row_repeat = int(row_repeat)
        odf_row.del_attribute('table:number-rows-repeated')
    else:
        row_repeat = 1

    # The cells
    cells = []
    for cell in odf_row.get_element_list(
                    'table:table-cell|table:covered-table-cell'):
        repeat = cell.get_attribute('table:number-columns-repeated')
        if repeat is not None:
            cell.del_attribute('table:number-columns-repeated')
            repeat = int(repeat)
            for i in range(repeat):
                cells.append(cell.clone())
        else:
            cells.append(cell)

    # Append the rows
    if row_repeat > 1:
        for i in range(row_repeat):
            rows.append({'attributes': odf_row.get_attributes(),
                         'cells': [ cell.clone() for cell in cells ]})
    else:
        rows.append({'attributes': odf_row.get_attributes(),
                     'cells': cells})



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

    Return: odf_element
    """

    cell = odf_create_element('<table:table-cell/>')
    representation = _set_value_and_type(cell, value=value,
                                         representation=representation,
                                         value_type=cell_type,
                                         currency=currency)
    if representation is not None:
        cell.set_text_content(representation)
    if style is not None:
        cell.set_attribute('table:style-name', style)
    return cell



def odf_create_row(width=None): # TODO style?
    """Create a row element, optionally filled with "width" number of cells.

    Rows contain cells, their number determine the number of columns.

    You don't generally have to create rows by hand, use the odf_table API.

    Arguments:

        width -- int

    Return: odf_element
    """
    row = odf_create_element('<table:table-row/>')
    if width is not None:
        for i in xrange(width):
            cell = odf_create_cell(u"")
            row.append_element(cell)
    return row



def odf_create_row_group(height=None, width=None):
    """Create a group of rows, optionnaly filled with "height" number of rows,
    of "width" cells each.

    Row group bear style information applied to a series of rows.

    Arguments:

        height -- int

    Return odf_element
    """
    row_group = odf_create_row_group('<table:table-row-group')
    if height is not None:
        for i in xrange(height):
            row = odf_create_row(width)
            row_group.append_element(row)
    return row_group



def odf_create_column_group(style=None, default_cell_style=None,
        repeated=None):
    """Create a column group element of the optionally given style. Cell style
    can be set for the whole column. If the properties apply to several
    columns, give the number of repeated columns.

    Columns don't contain cells, just style information.

    You don't generally have to create columns by hand, use the odf_table API.

    Arguments:

        style -- unicode

        default_cell_style -- unicode

        repeated -- int

    Return: odf_element
    """
    element = odf_create_element('<table:table-column/>')
    if style:
        element.set_attribute('table:style-name', style)
    if default_cell_style:
        element.set_attribute('table:default-cell-style-name',
                default_cell_style)
    if repeated:
        element.set_attribute('table:number-columns-repeated', str(repeated))
    return element



def odf_create_table(name, width=None, height=None, protected=False,
                     protection_key=None, display=True, printable=True,
                     print_ranges=None, style=None):
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

    You can access and modify the XML tree manuall, but you probably want to
    use the API to access and alter cells. It will save you from handling
    repetitions and the same number of cells for each row.

    If you modify both the 

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

    Return: odf_element
    """
    element = odf_create_element(u'<table:table table:name="%s"/>' % name)
    if protected:
        if protection_key is None:
            raise ValueError, "missing protection key"
        element.set_attribute('table:protected', 'true')
    if not display:
        element.set_attribute('table:display', 'false')
    if not printable:
        element.set_attribute('table:print', 'false')
    if print_ranges:
        if isinstance(print_ranges, (tuple, list)):
            print_ranges = ' '.join(print_ranges)
        element.set_attribute('table:print-ranges', print_ranges)
    if style:
        element.set_attribute('table:style-name', style)
    # Prefill the table
    if width is not None or height is not None:
        width = width or 1
        height = height or 1
        # Column groups for style information
        columns = odf_create_column_group(repeated=width)
        element.append_element(columns)
        # TODO Use repeat for compacity (and row group?)
        for i in xrange(height):
            row = odf_create_row(width)
            element.append_element(row)
    return element



class odf_table(odf_element):

    # Internal representation is a list of lists, modified cells are stored,
    # others are marked as None
    __state = []
    __width = 0
    __heigt = 0

    #
    # Private API
    #

    def __init__(self, native_element):
        super(self).__init__(native_element)
        width, height = (0, 0)
        # Determine the height from the number of rows
        rows = self.xpath('table:table-row')
        repeated = self.xpath('table:table-row/@table:number-rows-repeated')
        unrepeated = len(rows) - len(repeated)
        height = sum(int(r) for r in repeated) + unrepeated
        # Determine the width from the first row
        row = rows[0]
        cells = row.xpath('table:table-cell')
        repeated = row.xpath('(table:table-cell|table:covered-table-cell)/'
                '@table:number-columns-repeated')
        unrepeated = len(cells) - len(repeated)
        width = sum(int(r) for r in repeated) + unrepeated
        print "width", width, "height", height
        self.__width = width
        self.__heigt = height


    def __get_cell(self, x, y):
        if x >= self.__width or y >= self.__height:
            raise ValueError, "cell outside of table"
        # In the internal structure
        try:
            cell = self.__state[y][x]
        except KeyError:
            cell = None
        else:
            return cell
        w, h = 0, 0
        for row in self.get_element_list('table:table-row'):
            h += row.get_attribute('table:number-rows-repeated') or 1
            if y < h:
                for cell in row.get_element_list(
                        '(<table:table-cell|table:covered-table-cell)'):
                    w += (cell.get_attribute('table:number-columns-repeated')
                            or 1)
                    if x < w:
                        cell.del_attribute('table:number-columns-repeated')
                        return cell
        raise ValueError


    def __set_cell(self, x, y, cell):
        state = self.__state
        height = len(state)
        width = len(state[0]) if h else 0
        if y + 1 > height:
            state.extend([[None] * width for h in xrange(y - height + 1)])
            self.__height = y + 1
        if x + 1 > width:
            for row in state:
                row.extend([None] * (x - width + 1))
            self.__width = x + 1
        state[y][x] = cell


    def __expand_cells(self, row):
        for cell in row.get_element_list(
                '(<table:table-cell|table:covered-table-cell)'):
            repeated = (cell.get_attribute('table:number-columns-repeated')
                    or 1)
            cell.del_attribute('table:number-columns-repeated')
            for i in xrange(repeated):
                yield cell


    #
    # Public API
    #

    def get_size(self):
        return self.__width, self.__height


    def get_table_name(self):
        return self.get_attribute('table:name')


    def synchronize(self):
        """Report the modifications to the XML tree.
        """
        raise NotImplementedError


    def get_formated_text(self, context):
        result = []
        for row in self.traverse_rows():
            for cell in row.get_children():
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
        """Return as many row elements as real rows, i.e. expand repetitions.

        Modified cells are returned in place of original cells from the XML
        tree.
        """
        state = self.__state
        y = 0
        for row in self.get_element_list('table:table-row'):
            repeated = row.get_attribute('table:number-rows-repeated') or 1
            row.del_attribute('table:number-rows-repeated')
            for x, original_cell in enumerate(self.__expand_cells(row)):
                try:
                    cell = state[y][x]
                except KeyError:
                    cell = None
                if cell is None:
                    cell = original_cell
                row.append_element(cell)
            for i in xrange(repeated):
                yield row.clone()
            y += repeated


    def get_row_list(self, regex=None, style=None):
        """Return the list of  rows matching the criteria. Each result is a
        tuple of (y, cell).

        Arguments:

            regex -- unicode

            style -- unicode

        Return: list of tuples
        """
        rows = []
        for y, row in enumerate(self.traverse_rows()):
            # Filter the cells with the regex
            if regex and not row.match(regex):
                continue
            # Filter the cells with the style
            if style and row.get_attribute('table:style-name') != style:
                continue
            rows.append((y, row))
        return rows


    def set_row(self, y, row):
        raise NotImplementedError


    # XXX Add a cells argument ??
    def add_row(self, number=1, position=None):
        """Insert number rows before the row at the given position. Append by
        default.

        Positions start at 0.
        """
        raise NotImplementedError


    #
    # Cells
    #

    def get_cell(self, coordinates):
        x, y = _get_cell_coordinates(coordinates)
        return self.__get_cell(x, y)


    def set_cell(self, coordinates, cell):
        x, y = _get_cell_coordinates(coordinates)
        return self.__set_cell(x, y, cell)


    def get_cell_list(self, regex=None, style=None):
        """Return the list of cells matching the criteria. Each result is a
        tuple of (x, y, cell).

        Arguments:

            regex -- unicode

            style -- unicode

        Return: list of tuples
        """
        cells = []
        state = self.__state
        for y, row in enumerate(self.traverse_rows()):
            for x, cell in enumerate(row.get_children()):
                # Filter the cells with the regex
                if regex and not cell.match(regex):
                    continue
                # Filter the cells with the style
                if style and cell.get_attribute('table:style-name') != style:
                        continue
                cells.append((x, y, cell))
        # Return the coordinates and element
        return cells


    #
    # Columns
    #

    def get_column_list(self, regex=None, style=None):
        raise NotImplementedError


    # XXX Add a cells argument ??
    def add_column(self, number=1, position=None):
        """Insert number columns before the column at the given position.
        Append by default.

        Positions start at 0.
        """
        raise NotImplementedError


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
        state = self.__state
        for row in self.traverse_rows():
            current_row = []
            for cell in row.get_children():
                # Get value
                value = get_value(cell)
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
    # XXX We load the entire file, this can be a problem with a very big file
    if type(file) is str:
        file = vfs.open(file)
        data = file.read().splitlines(True)
        file.close()
    else:
        # Leave the file we were given open
        data = file.read().splitlines(True)
    # Sniff the dialect
    sample = ''.join(data[:10])
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
    state = [ [ _get_python_value(value, encoding) for value in line]
             for line in csv ]
    table = odf_table(name=name, style=style)
    table.__state = state
    table.__height = len(state)
    table.__width = len(state[0])



# Register
register_element_class('table:table', odf_table)
