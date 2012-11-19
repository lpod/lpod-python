# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2012 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          Romain Gauthier <romain@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>
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
from bisect import bisect_left, insort
import string

# Import from lpod
from datatype import Boolean, Date, DateTime, Duration
from element import odf_create_element, register_element_class, odf_element
from element import _xpath_compile
from utils import get_value, _set_value_and_type, isiterable   #, obsolete



_xpath_row = _xpath_compile('table:table-row')
_xpath_row_idx = _xpath_compile('(table:table-row)[$idx]')
_xpath_column = _xpath_compile('table:table-column')
_xpath_column_idx = _xpath_compile('(table:table-column)[$idx]')
_xpath_cell = _xpath_compile('(table:table-cell|table:covered-table-cell)')
_xpath_cell_idx = _xpath_compile('(table:table-cell|table:covered-table-cell)[$idx]')



def _table_name_check(name):
    if not isinstance(name, basestring):
        raise ValueError, "String required."
    name = name.strip()
    if not name :
        raise ValueError, "Empty name not allowed."
    for character in ('\n', '/', '\\', "'") :
        if character in name:
            raise ValueError, 'Character %s not allowed.' % character
    return name


_forbidden_in_named_range = [x for x in string.printable if x not in
                            string.letters and x not in
                            string.digits and x !='_']


def _alpha_to_digit(alpha):
    """Translates A to 0, B to 1, etc. So "AB" is value 27.
    """
    if type(alpha) is int:
        return alpha
    if not alpha.isalpha():
        raise ValueError, 'column name "%s" is malformed' % str(alpha)
    column = 0
    for c in alpha.lower():
        v = ord(c) - ord('a') + 1
        column = column * 26 + v
    return column - 1



def _digit_to_alpha(digit):
    if type(digit) is str and digit.isalpha():
        return digit
    if not type(digit) is int:
        raise ValueError, 'column number "%s" is invalid' % str(digit)
    digit += 1
    column = ''
    while digit:
        column = chr(65 + ((digit - 1) % 26)) + column
        digit = (digit - 1) / 26
    return column



def _coordinates_to_alpha_area(coord):
        # assuming : either (x,y) or (x,y,z,t), with positive values
        if isinstance(coord, basestring):
            # either A1 or A1:B2, returns A1:A1 if needed
            parts = coord.strip().split(':')
            if len(parts) == 1:
                start = end = parts[0]
            else:
                start = parts[0]
                end = parts[1]
        elif isiterable(coord):
            if len(coord) == 2:
                x = coord[0]
                y = coord[1]
                z = x
                t = y
            else:
            # should be 4 int
                x, y, z, t = coord
            start = _digit_to_alpha(x) + "%s" % (y+1)
            end = _digit_to_alpha(z) + "%s" % (t+1)
        else:
            raise ValueError
        crange = start + ':' + end
        return (start, end, crange)



def _increment(x, step):
    while x < 0:
        if step == 0:
            return 0
        x += step
    return x



def _convert_coordinates(obj):
    """Translates "D3" to (3, 2) or return (1, 2) untouched.
    Translates "A1:B3" to (0,0,1,2)
    """
    # By (1, 2) ?
    if isiterable(obj):
        return tuple(obj)
    # Or by 'B3' notation ?
    if not isinstance(obj, basestring):
        raise ValueError, 'bad coordinates type: "%s"' % type(obj)
    coordinates = []
    for coord in [x.strip() for x in obj.split(':', 1)]:
        # First "A"
        alpha = ''
        for c in coord:
            if c.isalpha():
                alpha += c
            else:
                break
        try:
            column = _alpha_to_digit(alpha)
        except ValueError:
            #raise ValueError, 'coordinates "%s" malformed' % obj
            # maybe '1:4' table row coordinates
            column = None
        coordinates.append(column)
        # Then "1"
        try:
            line = int(coord[len(alpha):]) - 1
        except ValueError:
            #raise ValueError, 'coordinates "%s" malformed' % obj
            # maybe 'A:C' row coordinates
            line = None
        if line and line <= 0:
            raise ValueError, 'coordinates "%s" malformed' % obj
        coordinates.append(line)
    return tuple(coordinates)



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



def _set_item_in_vault(position, item, vault, vault_scheme, vault_map_name, clone=True):
    """Set the item (cell, row) in its vault (row, table), updating the
       cache map.
    """
    try:
        vault_map = getattr(vault, vault_map_name)
    except:
        raise ValueError
    odf_idx = _find_odf_idx(vault_map, position)
    repeated = item.get_repeated() or 1
    current_cache = vault_map[odf_idx]
    cache = vault._indexes[vault_map_name]
    if odf_idx in cache:
        current_item = cache[odf_idx]
    else:
        current_item = vault._get_element_idx2(vault_scheme, odf_idx)
    vault._indexes[vault_map_name] = {}
    target_idx = vault.index(current_item)
    if odf_idx > 0:
        before_cache = vault_map[odf_idx - 1]
    else:
        before_cache = -1
    current_pos = before_cache + 1
    current_repeated = current_cache - before_cache
    repeated_before = position - current_pos
    repeated_after = current_repeated - repeated_before - repeated
    if repeated_before >= 1:
        #Update repetition
        current_item._set_repeated(repeated_before)
        target_idx += 1
    else:
        # Replacing the first occurence
        vault.delete(current_item)
    # Insert new element
    if clone:
        new_item = item.clone()
    else:
        new_item = item
    vault.insert(new_item, position = target_idx)
    # Insert the remaining repetitions
    if repeated_after >= 1:
        after_item = current_item.clone()
        after_item._set_repeated(repeated_after)
        vault.insert(after_item, position = target_idx + 1)
    # setting a repeated item !
    if repeated_after < 0:
        # deleting some overlapped items
        deleting = repeated_after
        while deleting < 0:
            delete_item = vault._get_element_idx2(vault_scheme, target_idx + 1)
            if delete_item is None:
                break
            is_repeated = delete_item.get_repeated() or 1
            is_repeated += deleting
            if is_repeated > 1:
                delete_item._set_repeated(is_repeated)
            else:
                vault.delete(delete_item)
            deleting = is_repeated
    # update cache
    # remove existing
    idx = odf_idx
    map = _erase_map_once(vault_map, idx)
    # add before if any:
    if repeated_before >= 1:
        map = _insert_map_once(map, idx, repeated_before)
        idx += 1
    # add our slot
    map = _insert_map_once(map, idx, repeated)
    # add after if any::
    if repeated_after >= 1:
        idx += 1
        map = _insert_map_once(map, idx, repeated_after)
    if repeated_after < 0:
        idx += 1
        while repeated_after < 0:
            if idx < len(map):
                map = _erase_map_once(map, idx)
            repeated_after += 1
    setattr(vault, vault_map_name, map)
    return new_item



def _insert_item_in_vault(position, item, vault, vault_scheme, vault_map_name):
    try:
        vault_map = getattr(vault, vault_map_name)
    except:
        raise ValueError
    odf_idx = _find_odf_idx(vault_map, position)
    repeated = item.get_repeated() or 1
    current_cache = vault_map[odf_idx]
    cache = vault._indexes[vault_map_name]
    if odf_idx in cache:
        current_item = cache[odf_idx]
    else:
        current_item = vault._get_element_idx2(vault_scheme, odf_idx)
    vault._indexes[vault_map_name] = {}
    target_idx = vault.index(current_item)
    if odf_idx > 0:
        before_cache = vault_map[odf_idx - 1]
    else:
        before_cache = -1
    current_pos = before_cache + 1
    current_repeated = current_cache - before_cache
    repeated_before = position - current_pos
    repeated_after = current_repeated - repeated_before
    new_item = item.clone()
    if repeated_before >= 1:
        current_item._set_repeated(repeated_before)
        vault.insert(new_item, position = target_idx + 1)
        after_item = current_item.clone()
        after_item._set_repeated(repeated_after)
        vault.insert(after_item, position = target_idx + 2)
    else:
        # only insert new cell
        vault.insert(new_item, position = target_idx)
    # update cache
    if repeated_before >= 1:
        map = _erase_map_once(vault_map, odf_idx)
        map = _insert_map_once(map, odf_idx, repeated_before)
        map = _insert_map_once(map, odf_idx + 1, repeated)
        setattr(vault, vault_map_name, _insert_map_once(map, odf_idx + 2, repeated_after))
    else:
        setattr(vault, vault_map_name, _insert_map_once(vault_map, odf_idx, repeated))
    return new_item



def _delete_item_in_vault(position, vault, vault_scheme, vault_map_name):
    try:
        vault_map = getattr(vault, vault_map_name)
    except:
        raise ValueError
    odf_idx = _find_odf_idx(vault_map, position)
    current_cache = vault_map[odf_idx]
    cache = vault._indexes[vault_map_name]
    if odf_idx in cache:
        current_item = cache[odf_idx]
    else:
        current_item = vault._get_element_idx2(vault_scheme, odf_idx)
    vault._indexes[vault_map_name] = {}
    if odf_idx > 0:
        before_cache = vault_map[odf_idx - 1]
    else:
        before_cache = -1
    current_pos = before_cache + 1
    current_repeated = current_cache - before_cache
    new_repeated = current_repeated - 1
    if new_repeated >= 1:
        current_item._set_repeated(new_repeated)
        setattr(vault, vault_map_name, vault_map[:odf_idx] + [(x - 1) for x in vault_map[odf_idx:]] )
    else:
        # actual erase
        vault.delete(current_item)
        setattr(vault, vault_map_name, vault_map[:odf_idx] + [(x - 1) for x in vault_map[odf_idx + 1:]] )



def _insert_map_once(map, odf_idx, repeated):
    """Add an item (cell or row) to the map

            map  --  cache map

            odf_idx  --  index in ODF XML

            repeated  --  repeated value of item, 1 or more

        odf_idx is NOT position (col or row), neither raw XML position, but ODF index
    """
    repeated = repeated or 1
    if odf_idx > len(map):
        raise IndexError
    if odf_idx > 0 :
        before = map[odf_idx - 1]
    else:
        before = -1
    juska = before + repeated # aka max position value for item
    if odf_idx == len(map):
        insort(map, juska)
        return map
    new_map = map[:odf_idx]
    new_map.append(juska)
    new_map.extend([(x + repeated) for x in map[odf_idx:]])
    return new_map



def _erase_map_once(map, odf_idx):
    """Remove an item (cell or row) from the map

            map  --  cache map

            odf_idx  --  index in ODF XML
    """
    if odf_idx >= len(map):
        raise IndexError
    if odf_idx > 0 :
        before = map[odf_idx - 1]
    else:
        before = -1
    current = map[odf_idx]
    repeated = current - before
    map = map[:odf_idx] + [(x - repeated) for x in map[odf_idx + 1:]]
    return map



def _make_cache_map(idx_repeated_seq):
    """Build the initial cache map of the table.
    """
    map = []
    for odf_idx, repeated in idx_repeated_seq:
        map = _insert_map_once(map, odf_idx, repeated)
    return map



def _find_odf_idx(map, position):
    """Find odf_idx in the map from the position (col or row).
    """
    odf_idx = bisect_left(map, position)
    if odf_idx < len(map):
        return odf_idx
    return None



def odf_create_cell(value=None, text=None, cell_type=None, currency=None,
        formula=None, repeated=None, style=None):
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
            currency=currency, formula=formula)
    if repeated and repeated > 1:
        element.set_repeated(repeated)
    if style is not None:
        element.set_style(style)
    return element



def odf_create_row(width=None, repeated=None, style=None, cache=None):
    """Create a row element, optionally filled with "width" number of cells.

    Rows contain cells, their number determine the number of columns.

    You don't generally have to create rows by hand, use the odf_table API.

    Arguments:

        width -- int

        repeated -- int

        style -- unicode

    Return: odf_row
    """
    element = odf_create_element('table:table-row', cache)
    if width is not None:
        for i in xrange(width):
            element.append(odf_create_cell())
    if repeated:
        element.set_repeated(repeated)
    if style is not None:
        element.set_style(style)
    element._compute_row_cache()
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
            row = odf_create_row(width=width)
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
        element.set_style(style)
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
    element = odf_create_element('table:table', ([], []))
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
        element.set_style(style)
    # Prefill the table
    if width is not None or height is not None:
        width = width or 1
        height = height or 1
        # Column groups for style information
        columns = odf_create_column(repeated=width)
        element._append(columns)
        for i in xrange(height):
            row = odf_create_row(width)
            element._append(row)
    element._compute_table_cache()
    return element



def odf_create_named_range(name, crange, table_name, usage=None):
    """Create a Named Range element. 'name' must contains only letters, digits
    and '_', and must not be like a coordinate as 'A1'. 'table_name' must be
    a correct table name (no "'" or "/" in it).

    Arguments:

        name -- str, name of the named range

        crange -- str or tuple of int, cell or area coordinate

        table_name -- str, name of the table

        uage -- None or 'print-range', 'filter', 'repeat-column', 'repeat-row'
    """
    element = odf_create_element('table:named-range')
    element.set_name(name)
    element.table_name = _table_name_check(table_name)
    element.set_range(crange)
    element.set_usage(usage)
    return element



class odf_cell(odf_element):
    """Class for the table cell element.
    """

    def __init__(self, native_element):
        odf_element.__init__(self, native_element)
        self.y = None
        self.x = None


    def clone(self):
        clone = odf_element.clone(self)
        clone.y = self.y
        clone.x = self.x
        return clone


    def get_value(self, get_type=False):
        """Get the Python value that represent the cell.

        Possible return types are unicode, int, Decimal, datetime,
        timedelta.
        If get_type is True, returns a tuple (value, ODF type of value)

        Return: Python type or tuple (python type, string)
        """
        return get_value(self, get_type=get_type)


    def set_value(self, value, text=None, cell_type=None, currency=None,
            formula=None):
        """Set the cell state from the Python value type.

        Text is how the cell is displayed. Cell type is guessed,
        unless provided.

        For monetary values, provide the name of the currency.

        Arguments:

            value -- Python type

            text -- unicode

            cell_type -- 'boolean', 'float', 'date', 'string', 'time',
                        'currency' or 'percentage'

            currency -- unicode
        """
        text = _set_value_and_type(self, value=value, text=text,
                value_type=cell_type, currency=currency)
        if text is not None:
            self.set_text_content(text)
        if formula is not None:
            self.set_formula(formula)

    #set_cell_value = obsolete('set_cell_value', set_value)


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


    def _set_repeated(self, repeated):
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

    def set_repeated(self, repeated):
        """Set the numnber of times the cell is repeated, or None to delete
        it.

        Arguments:

            repeated -- int or None
        """
        self._set_repeated(repeated)
        # update cache
        child = self
        while True:
            # look for odf_row, parent may be group of rows
            upper = child.get_parent()
            if not upper:
                # lonely cell
                return
            # parent may be group of rows, not table
            if isinstance(upper, odf_row):
                break
            child = upper
        # fixme : need to optimize this
        if isinstance(upper, odf_row):
            upper._compute_row_cache()


    def get_style(self):
        """Get the style of the cell itself.

        Return: unicode
        """
        return self.get_attribute('table:style-name')


    def set_style(self, style):
        """Set the style of the cell itself.

        Arguments:

            style -- unicode
        """
        self.set_style_attribute('table:style-name', style)

    #set_cell_style = obsolete('set_cell_style', set_style)


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


    def set_text(self, text):
        return self.set_text_content(text)


    def is_empty(self, aggressive=False):
        if self.get_value() is not None or self.get_children():
            return False
        if not aggressive and self.get_style() is not None:
            return False
        return True


    def _is_spanned(self):
        if self.get_tag() == 'table:covered-table-cell':
            return True
        if self.get_attribute('table:number-columns-spanned') is not None:
            return True
        if self.get_attribute('table:number-rows-spanned') is not None:
            return True
        return False



class odf_row(odf_element):

    # Private API
    def __init__(self, native_element, cache=None):
        odf_element.__init__(self, native_element, cache)
        self.y = None
        # parse the whole table for repeated cells, if cache not already provided
        if not hasattr(self, '_rmap'):
            self._compute_row_cache()
            if not hasattr(self, '_tmap'):
                self._tmap = []
                self._cmap = []
        if not hasattr(self, '_indexes'):
            self._indexes={}
            self._indexes['_rmap'] = {}


    _append = odf_element.append


    def _get_cells(self):
        return self.get_elements(_xpath_cell)


    def _translate_x_from_any(self, x):
        if isinstance(x, basestring):
            x, _ = _convert_coordinates(x)
        if x and x < 0:
            return _increment(x, self.get_width())
        return x


    def _translate_row_coordinates(self, coord):
        xyzt = _convert_coordinates(coord)
        if len(xyzt) == 2:
            x, z = xyzt
        else:
            x, _, z, __ = xyzt
        if x and x < 0:
            x = _increment(x, self.get_width())
        if z and z < 0:
            z = _increment(z, self.get_width())
        return (x, z)


    def _compute_row_cache(self):
        idx_repeated_seq = self.elements_repeated_sequence(_xpath_cell, 'table:number-columns-repeated')
        self._rmap = _make_cache_map(idx_repeated_seq)


    # Public API

    def clone(self):
        clone = odf_element.clone(self)
        clone.y = self.y
        return clone


    def get_repeated(self):
        """Get the number of times the row is repeated.

        Always None when using the table API.

        Return: int or None
        """
        repeated = self.get_attribute('table:number-rows-repeated')
        if repeated is None:
            return None
        return int(repeated)


    def _set_repeated(self, repeated):
        """Set the numnber of times the row is repeated, or None to delete
        it. Without changing cache.

        Arguments:

            repeated -- int
        """
        if repeated is None or repeated < 2:
            try:
                self.del_attribute('table:number-rows-repeated')
            except KeyError:
                pass
            return
        self.set_attribute('table:number-rows-repeated', str(repeated))

    def set_repeated(self, repeated):
        """Set the numnber of times the row is repeated, or None to delete
        it and update cache map.

        Arguments:

            repeated -- int or None
        """
        self._set_repeated(repeated)
        # update cache
        current = self
        while True:
            # look for odf_table, parent may be group of rows
            upper = current.get_parent()
            if not upper:
                # lonely row
                return
            # parent may be group of rows, not table
            if isinstance(upper, odf_table):
                break
            current = upper
        # fixme : need to optimize this
        if isinstance(upper, odf_table):
            upper._compute_table_cache()
            if hasattr(self, '_tmap'):
                del self._tmap[:]
                self._tmap.extend(upper._tmap)
            else:
                self._tmap = upper._tmap


    def get_style(self):
        """Get the style of the row itself.

        Return: unicode
        """
        return self.get_attribute('table:style-name')


    def set_style(self, style):
        """Set the style of the row itself.

        Arguments:

            style -- unicode
        """
        self.set_style_attribute('table:style-name', style)

    #set_row_style = obsolete('set_row_style', set_style)


    def get_width(self):
        """Get the number of expected cells in the row, i.e. addition
        repetitions.

        Return: int
        """
        try:
            w = self._rmap[-1] + 1
        except:
            w = 0
        return w


    def traverse(self, start=None, end=None):
        """Yield as many cell elements as expected cells in the row, i.e.
        expand repetitions by returning the same cell as many times as
        necessary.

            Arguments:

                start -- int

                end -- int

        Copies are returned, use ``set_cell`` to push them back.
        """
        idx = -1
        before = -1
        x = 0
        if start is None and end is None:
            for juska in self._rmap:
                idx += 1
                if idx in self._indexes['_rmap']:
                    cell = self._indexes['_rmap'][idx]
                else:
                    cell = self._get_element_idx2(_xpath_cell_idx, idx)
                    self._indexes['_rmap'][idx] = cell
                repeated = juska - before
                before = juska
                for i in xrange(repeated or 1):
                    # Return a copy without the now obsolete repetition
                    if cell is None:
                        cell = odf_create_cell()
                    else:
                        cell = cell.clone()
                        if repeated > 1:
                            cell.set_repeated(None)
                    cell.y = self.y
                    cell.x = x
                    x += 1
                    yield cell
        else:
            if start is None:
                start = 0
            start = max(0, start)
            if end is None:
                try:
                    end = self._rmap[-1]
                except:
                    end = -1
            start_map = _find_odf_idx(self._rmap, start)
            if start_map is None:
                return
            if start_map > 0:
                before = self._rmap[start_map - 1]
            idx = start_map - 1
            before = start - 1
            x = start
            for juska in self._rmap[start_map:]:
                idx += 1
                if idx in self._indexes['_rmap']:
                    cell = self._indexes['_rmap'][idx]
                else:
                    cell = self._get_element_idx2(_xpath_cell_idx, idx)
                    self._indexes['_rmap'][idx] = cell
                repeated = juska - before
                before = juska
                for i in xrange(repeated or 1):
                    if x <= end:
                        if cell is None:
                            cell = odf_create_cell()
                        else:
                            cell = cell.clone()
                            if repeated > 1 or (x == start and start > 0):
                                cell.set_repeated(None)
                        cell.y = self.y
                        cell.x = x
                        x += 1
                        yield cell


    def get_cells(self, coord=None, style=None, content=None,
                  cell_type=None):
        """Get the list of cells matching the criteria.

        Filter by cell_type, with cell_type 'all' will retrieve cells of any
        type, aka non empty cells.

        Filter by coordinates will retrieve the amount of cells defined by
        'coord', minus the other filters.

        Arguments:

            coord -- str or tuple of int : coordinates

            cell_type -- 'boolean', 'float', 'date', 'string', 'time',
                         'currency', 'percentage' or 'all'

            content -- regex, unicode

            style -- unicode

        Return: list of tuples
        """
        # fixme : not clones ?
        if coord:
            x, z = self._translate_row_coordinates(coord)
        else:
            x = None
            z = None
        if cell_type:
            cell_type = cell_type.lower().strip()
        cells = []
        for cell in self.traverse(start = x, end = z):
            # Filter the cells by cell_type
            if cell_type:
                ctype = cell.get_type()
                if not ctype or not (ctype == cell_type or cell_type == 'all'):
                    continue
            # Filter the cells with the regex
            if content and not cell.match(content):
                continue
            # Filter the cells with the style
            if style and style != cell.get_style():
                continue
            cells.append(cell)
        return cells

    #get_cell_list = obsolete('get_cell_list', get_cells)


    def _get_cell2(self, x, clone=True):
        if x >= self.get_width():
            return odf_create_cell()
        if clone:
            return self._get_cell2_base(x).clone()
        else:
            return self._get_cell2_base(x).clone()

    def _get_cell2_base(self, x):
        idx = _find_odf_idx(self._rmap, x)
        if idx is not None:
            if idx in self._indexes['_rmap']:
                cell = self._indexes['_rmap'][idx]
            else:
                cell = self._get_element_idx2(_xpath_cell_idx, idx)
                self._indexes['_rmap'][idx] = cell
            return cell
        return None

    def get_cell(self, x, clone=True):
        """Get the cell at position "x" starting from 0. Alphabetical
        positions like "D" are accepted.

        A  copy is returned, use ``set_cell`` to push it back.

        Arguments:

            x -- int or str

        Return: odf_cell
        """
        x = self._translate_x_from_any(x)
        cell = self._get_cell2(x, clone=clone)
        cell.y = self.y
        cell.x = x
        return cell


    def get_value(self, x, get_type=False):
        """Shortcut to get the value of the cell at position "x".
        If get_type is True, returns the tuples (value, ODF type).

        If the cell is empty, returns None or (None, None)

        See ``get_cell`` and ``odf_cell.get_value``.
        """
        if get_type:
            x = self._translate_x_from_any(x)
            cell = self._get_cell2_base(x)
            if cell is None:
                return (None, None)
            return cell.get_value(get_type=get_type)
        else:
            x = self._translate_x_from_any(x)
            cell = self._get_cell2_base(x)
            if cell is None:
                return None
            return cell.get_value()


    def set_cell(self, x, cell=None, clone=True, _get_repeat=False):
        """Push the cell back in the row at position "x" starting from 0.
        Alphabetical positions like "D" are accepted.

        Arguments:

            x -- int or str

        returns the cell with x and y updated
        """
        if cell is None:
            cell = odf_create_cell()
            repeated = 1
            clone = False
        else:
            repeated = cell.get_repeated() or 1
        x = self._translate_x_from_any(x)
        # Outside the defined row
        diff = x - self.get_width()
        if diff == 0:
            cell_back = self.append_cell(cell, _repeated=repeated, clone=clone)
        elif diff > 0:
            self.append_cell(odf_create_cell(repeated=diff), _repeated=diff, clone=False)
            cell_back = self.append_cell(cell, _repeated=repeated, clone=clone)
        else:
            # Inside the defined row
            _set_item_in_vault(x, cell, self, _xpath_cell_idx, '_rmap', clone=clone)
            cell.x = x
            cell.y = self.y
            cell_back = cell
        if _get_repeat:
            return repeated
        else:
            return cell_back


    def set_value(self, x, value, style=None, cell_type=None, currency=None):
        """Shortcut to set the value of the cell at position "x".

        Arguments:

            x -- int or str

            value -- Python type

            cell_type -- 'boolean', 'currency', 'date', 'float', 'percentage',
                     'string' or 'time'

            currency -- three-letter str

            style -- unicode

        See ``get_cell`` and ``odf_cell.get_value``.
        """
        self.set_cell(x, odf_create_cell(value, style=style,
                        cell_type=cell_type, currency=currency), clone=False)


    def insert_cell(self, x, cell=None, clone=True):
        """Insert the given cell at position "x" starting from 0. If no cell
        is given, an empty one is created.

        Alphabetical positions like "D" are accepted.

        Do not use when working on a table, use ``odf_table.insert_cell``.

        Arguments:

            x -- int or str

            cell -- odf_cell

        returns the cell with x and y updated
        """
        if cell is None:
            cell = odf_create_cell()
        x = self._translate_x_from_any(x)
        # Outside the defined row
        diff = x - self.get_width()
        if diff < 0:
            _insert_item_in_vault(x, cell, self, _xpath_cell_idx, '_rmap')
            cell.x = x
            cell.y = self.y
            cell_back = cell
        elif diff == 0:
            cell_back = self.append_cell(cell, clone=clone)
        else:
            self.append_cell(odf_create_cell(repeated=diff), _repeated=diff, clone=False)
            cell_back = self.append_cell(cell, clone=clone)
        return cell_back


    def extend_cells(self, cells=[]):
        self.extend(cells)
        self._compute_row_cache()


    def append_cell(self, cell=None, clone=True, _repeated=None):
        """Append the given cell at the end of the row. Repeated cells are
        accepted. If no cell is given, an empty one is created.

        Do not use when working on a table, use ``odf_table.append_cell``.

        Arguments:

            cell -- odf_cell

            _repeated -- (optional), repeated value of the row

        returns the cell with x and y updated
        """
        if cell is None:
            cell = odf_create_cell()
            clone = False
        if clone:
            cell = cell.clone()
        self._append(cell)
        if _repeated is None:
            _repeated = cell.get_repeated() or 1
        self._rmap = _insert_map_once(self._rmap, len(self._rmap), _repeated)
        cell.x = self.get_width() - 1
        cell.y = self.y
        return cell

    # fix for unit test and typos
    append = append_cell


    def delete_cell(self, x):
        """Delete the cell at the given position "x" starting from 0.
        Alphabetical positions like "D" are accepted.

        Cells on the right will be shifted to the left. In a table, other
        rows remain unaffected.

        Arguments:

            x -- int or str
        """
        x = self._translate_x_from_any(x)
        if x >= self.get_width():
            return
        _delete_item_in_vault(x, self, _xpath_cell_idx, '_rmap')


    def get_values(self, coord=None, cell_type=None,
                   complete=False, get_type=False):
        """Shortcut to get the cell values in this row.

        Filter by cell_type, with cell_type 'all' will retrieve cells of any
        type, aka non empty cells.
        If cell_type is used and complete is True, missing values are
        replaced by None.
        If cell_type is None, complete is always True : with no cell type
        queried, get_values() returns None for each empty cell, the length
        of the list is equal to the length of the row (depending on
        coordinates use).

        If get_type is True, returns a tuple (value, ODF type of value), or
        (None, None) for empty cells if complete is True.

        Filter by coordinates will retrieve the amount of cells defined by
        coordinates with None for empty cells, except when using cell_type.


        Arguments:

            coord -- str or tuple of int : coordinates in row

            cell_type -- 'boolean', 'float', 'date', 'string', 'time',
                         'currency', 'percentage' or 'all'

            complete -- boolean

            get_type -- boolean

        Return: list of Python types, or list of tuples.
        """
        if coord:
            x, z = self._translate_row_coordinates(coord)
        else:
            x = None
            z = None
        if cell_type:
            cell_type = cell_type.lower().strip()
            values = []
            for cell in self.traverse(start = x, end = z):
                # Filter the cells by cell_type
                ctype = cell.get_type()
                if not ctype or not (ctype == cell_type or cell_type == 'all'):
                    if complete:
                        if get_type:
                            values.append((None, None))
                        else:
                            values.append(None)
                    continue
                values.append(cell.get_value(get_type = get_type))
            return values
        else:
            return [ cell.get_value(get_type = get_type)
                                for cell in self.traverse(start = x, end = z) ]


    def set_cells(self, cells=[], start=0, clone=True):
        """Set the cells in the row, from the 'start' column.
        This method does not clear the row, use row.clear() before to start
        with an empty row.

        Arguments:

            values -- list of Python types

            start -- int or str

            cells -- list of cells
        """
        if start is None:
            start = 0
        else:
            start = self._translate_x_from_any(start)
        if start == 0 and clone == False and (len(cells) >= self.get_width()):
            self.clear()
            self.extend_cells(cells)
        else:
            x = start
            for cell in cells:
                repeat = self.set_cell(x, cell, clone=clone, _get_repeat=True)
                x += repeat


    def set_values(self, values, start=0, style=None, cell_type=None,
                   currency=None):
        """Shortcut to set the value of cells in the row, from the 'start'
        column vith values.
        This method does not clear the row, use row.clear() before to start
        with an empty row.

        Arguments:

            values -- list of Python types

            start -- int or str

            cell_type -- 'boolean', 'float', 'date', 'string', 'time',
                         'currency' or 'percentage'

            currency -- three-letter str

            style -- cell style
        """
        # fixme : if values n, n+ are same, use repeat
        if start is None:
            start = 0
        else:
            start = self._translate_x_from_any(start)
        if start == 0 and (len(values) >= self.get_width()):
            self.clear()
            cells = ([odf_create_cell(value, style=style,
                    cell_type=cell_type, currency=currency)
                    for value in values])
            self.extend_cells(cells)
        else:
            x = start
            for value in values:
                self.set_cell(x, odf_create_cell(value, style=style,
                        cell_type=cell_type, currency=currency), clone=False)
                x += 1


    def rstrip(self, aggressive=False):
        """Remove *in-place* empty cells at the right of the row. An empty
        cell has no value but can have style. If "aggressive" is True, style
        is ignored.

        Arguments:

            aggressive -- bool
        """
        for cell in reversed(self._get_cells()):
            if not cell.is_empty(aggressive=aggressive):
                break
            self.delete(cell)
        self._compute_row_cache()
        self._indexes['_rmap'] = {}


    def is_empty(self, aggressive=False):
        """Return whether every cell in the row has no value or the value
        evaluates to False (empty string), and no style.

        If aggressive is True, empty cells with style are considered empty.

        Arguments:

            aggressive -- bool

        Return: bool
        """
        for cell in self._get_cells():
            if not cell.is_empty(aggressive=aggressive):
                return False
        return True



class odf_row_group(odf_element):
    """Class to group rows with common properties.
    """
    # TODO
    pass



class odf_column(odf_element):

    def __init__(self, native_element, cache=None):
        odf_element.__init__(self, native_element, cache)
        self.x = None


    def clone(self):
        clone = odf_element.clone(self)
        clone.x = self.x
        return clone


    def get_default_cell_style(self):
        return self.get_attribute('table:default-cell-style-name')


    def set_default_cell_style(self, style):
        self.set_style_attribute('table:default-cell-style-name', style)


    def get_repeated(self):
        """Get the number of times the column is repeated.

        Always None when using the table API.

        Return: int or None
        """
        repeated = self.get_attribute('table:number-columns-repeated')
        if repeated is None:
            return None
        return int(repeated)


    def _set_repeated(self, repeated):
        """Set the numnber of times the column is repeated, or None to delete
        it. Without changing cache.

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

    def set_repeated(self, repeated):
        """Set the numnber of times the column is repeated, or None to delete
        it and update cache map.

        Arguments:

            repeated -- int or None
        """
        self._set_repeated(repeated)
        # update cache
        current = self
        while True:
            # look for odf_table, parent may be group of rows
            upper = current.get_parent()
            if not upper:
                # lonely column
                return
            # parent may be group of rows, not table
            if isinstance(upper, odf_table):
                break
            current = upper
        # fixme : need to optimize this
        if isinstance(upper, odf_table):
            upper._compute_table_cache()
            if hasattr(self, '_cmap'):
                del self._cmap[:]
                self._cmap.extend(upper._cmap)
            else:
                self._cmap = upper._cmap


    def get_style(self):
        """Get the style of the column itself.

        Return: unicode
        """
        return self.get_attribute('table:style-name')


    def set_style(self, style):
        """Set the style of the column itself.

        Arguments:

            style -- unicode
        """
        self.set_style_attribute('table:style-name', style)



class odf_table(odf_element):
    #
    # Private API
    #
    def __init__(self, native_element, cache=None):
        odf_element.__init__(self, native_element, cache)
        # parse the whole table for repeated rows, if cache not already provided
        if cache is None:
            self._compute_table_cache()
        self._indexes={}
        self._indexes['_cmap'] = {}
        self._indexes['_tmap'] = {}


    _append = odf_element.append


    def _translate_x_from_any(self, x):
        if isinstance(x, basestring):
            x, _ = _convert_coordinates(x)
        if x and x < 0:
            return _increment(x, self.get_width())
        return x


    def _translate_y_from_any(self, y):
        # "3" (couting from 1) -> 2 (couting from 0)
        if isinstance(y, basestring):
            _, y = _convert_coordinates(y)
        if y and y < 0:
            return _increment(y, self.get_height())
        return y


    def _translate_table_coordinates(self, coord):
        height = self.get_height()
        width = self.get_width()
        if isiterable(coord):
            # assuming we got int values
            if len(coord) == 1:
                # It is a row
                y = coord[0]
                if y and y < 0:
                    y = _increment(y, height)
                return (None, y, None, y)
            if len(coord) == 2:
                # It is a row range, not a cell, because context is table
                y = coord[0]
                if y and y < 0:
                    y = _increment(y, height)
                t = coord[1]
                if t and t < 0:
                    t = _increment(t, height)
                return (None, y, None, t)
            # should be 4 int
            x, y, z, t = coord
            if x and x < 0:
                x = _increment(x, width)
            if y and y < 0:
                y = _increment(y, height)
            if z and z < 0:
                z = _increment(z, width)
            if t and t < 0:
                t = _increment(t, height)
            return (x, y, z, t)

        coord = _convert_coordinates(coord)
        if len(coord) == 2:
            x, y = coord
            if x and x < 0:
                x = _increment(x, width)
            if y and y < 0:
                y = _increment(y, height)
            # extent to an area :
            return (x, y, x, y)
        x, y, z, t = coord
        if x and x < 0:
            x = _increment(x, width)
        if y and y < 0:
            y = _increment(y, height)
        if z and z < 0:
            z = _increment(z, width)
        if t and t < 0:
            t = _increment(t, height)
        return (x, y, z, t)


    def _translate_column_coordinates(self, coord):
        height = self.get_height()
        width = self.get_width()
        if isiterable(coord):
            # assuming we got int values
            if len(coord) == 1:
                # It is a column
                x = coord[0]
                if x and x < 0:
                    x = _increment(x, width)
                return (x, None, x, None)
            if len(coord) == 2:
                # It is a column range, not a cell, because context is table
                x = coord[0]
                if x and x < 0:
                    x = _increment(y, width)
                t = coord[1]
                if z and z < 0:
                    z = _increment(t, width)
                return (x, None, z, None)
            # should be 4 int
            x, y, z, t = coord
            if x and x < 0:
                x = _increment(x, width)
            if y and y < 0:
                y = _increment(y, height)
            if z and z < 0:
                z = _increment(z, width)
            if t and t < 0:
                t = _increment(t, height)
            return (x, y, z, t)

        coord = _convert_coordinates(coord)
        if len(coord) == 2:
            x, y = coord
            if x and x < 0:
                x = _increment(x, width)
            if y and y < 0:
                y = _increment(y, height)
            # extent to an area :
            return (x, y, x, y)
        x, y, z, t = coord
        if x and x < 0:
            x = _increment(x, width)
        if y and y < 0:
            y = _increment(y, height)
        if z and z < 0:
            z = _increment(z, width)
        if t and t < 0:
            t = _increment(t, height)
        return (x, y, z, t)


    def _translate_cell_coordinates(self, coord):
        # we want an x,y result
        coord = _convert_coordinates(coord)
        if len(coord) == 2:
            x, y = coord
        # If we got an area, take the first cell
        elif len(coord) == 4:
            x, y, z, t = coord
        else:
            raise ValueError, "ValueError %s" % str(coord)
        if x and x < 0:
            x = _increment(x, self.get_width())
        if y and y < 0:
            y = _increment(y, self.get_height())
        return (x, y)


    def _compute_table_cache(self):
        idx_repeated_seq = self.elements_repeated_sequence(_xpath_row, 'table:number-rows-repeated')
        self._tmap = _make_cache_map(idx_repeated_seq)
        idx_repeated_seq = self.elements_repeated_sequence(_xpath_column, 'table:number-columns-repeated')
        self._cmap = _make_cache_map(idx_repeated_seq)


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
        context['no_img_level'] += 1
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
                # Compute the size of each columns (at least 2)
                cols_size[i] = max(cols_size.get(i, 2), len(value))
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
        # Construct the first/last line
        line = []
        for i in range(cols_nb):
            line.append(u'=' * cols_size[i])
            line.append(u' ')
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
            for j in range(max([1]+[len(values) for values in wrapped_row ])):
                txt_row = []
                for i in range(cols_nb):
                    values = wrapped_row[i] if i < len(wrapped_row) else []

                    # An empty cell ?
                    if len(values) - 1 < j or not values[j]:
                        if i == 0 and j == 0:
                            txt_row.append(u'..')
                            txt_row.append(u' ' * (cols_size[i] - 1))
                        else:
                            txt_row.append(u' ' * (cols_size[i] + 1))
                        continue

                    # Not empty
                    value = values[j]
                    txt_row.append(value)
                    txt_row.append(u' ' * (cols_size[i] - len(value) + 1))
                txt_row = u''.join(txt_row)
                result.append(txt_row)

        result.append(line)
        result.append(u'')
        result.append(u'')
        result = u'\n'.join(result)

        context['no_img_level'] -= 1
        return result

    #
    # Public API
    #

    def append(self, something):
        """Dispatch .append() call to append_row() or append_column().
        """
        if type(something) == odf_row:
            return self.append_row(something)
        elif type(something) == odf_column:
            return self.append_column(something)
        else:
            # probably still an error
            return self._append(something)


    def get_height(self):
        """Get the current height of the table.

        Return: int
        """
        try:
            h = self._tmap[-1] + 1
        except:
            h = 0
        return h


    #get_table_height = obsolete('get_table_height', get_height)


    def get_width(self):
        """Get the current width of the table, measured on columns.

        Rows may have different widths, use the odf_table API to ensure width
        consistency.

        Return: int
        """
        # Columns are our reference for user expected width

        try:
            w = self._cmap[-1] + 1
        except:
            w = 0

        #columns = self._get_columns()
        #repeated = self.xpath(
        #        'table:table-column/@table:number-columns-repeated')
        #unrepeated = len(columns) - len(repeated)
        #ws = sum(int(r) for r in repeated) + unrepeated
        #if w != ws:
        #    print "WARNING   ws", ws, "w", w

        return w

    #get_table_width = obsolete('get_table_width', get_width)


    def get_size(self):
        """Shortcut to get the current width and height of the table.

        Return: (int, int)
        """
        return self.get_width(), self.get_height()


    def get_name(self):
        """Return the name of the table.
        """
        return self.get_attribute('table:name')


    def set_name(self, name):
        """Set the name of the table. Name can't be empty and can't have the
        character "'" or '/'.
        """
        name = _table_name_check(name)
        # first, update named ranges
        # fixme : delete name ranges when deleting table, too.
        nrs = self.get_named_ranges(table_name = self.get_name())
        for nr in nrs:
            nr.set_table_name(name)
        self.set_attribute('table:name', name)


    def get_protected(self):
        return self.get_attribute('table:protected')


    def set_protected(self, protect):
        self.set_attribute('table:protected', protect)


    def get_displayed(self):
        return self.get_attribute('table:display')


    def set_displayed(self, display):
        self.set_attribute('table:display', display)


    def get_printable(self):
        printable = self.get_attribute('table:print')
        # Default value
        if printable is None:
            return True
        return printable


    def set_printable(self, printable):
        self.set_attribute('table:print', printable)


    def get_print_ranges(self):
        return self.get_attribute('table:print-ranges').split()


    def set_print_ranges(self, print_ranges):
        if isiterable(print_ranges):
            print_ranges = ' '.join(print_ranges)
        self.set_attribute('table:print-ranges', print_ranges)


    def get_style(self):
        return self.get_attribute('table:style-name')


    def set_style(self, style):
        self.set_style_attribute('table:style-name', style)

    #set_table_style = obsolete('set_table_style', set_style)


    def get_formatted_text(self, context):
        if context["rst_mode"]:
            return self.__get_formatted_text_rst(context)
        else:
            return self.__get_formatted_text_normal(context)


    def get_values(self, coord=None, cell_type=None, complete=True,
                   get_type=False, flat=False):
        """Get a matrix of values of the table.

        Filter by coordinates will parse the area defined by the coordinates.

        If 'cell_type' is used and 'complete' is True (default), missing values
        are replaced by None.
        Filter by ' cell_type = "all" ' will retrieve cells of any
        type, aka non empty cells.

        If 'cell_type' is None, complete is always True : with no cell type
        queried, get_values() returns None for each empty cell, the length
        each lists is equal to the width of the table.

        If get_type is True, returns tuples (value, ODF type of value), or
        (None, None) for empty cells with complete True.

        If flat is True, the methods return a single list of all the values.
        By default, flat is False.

        Arguments:

            coord -- str or tuple of int : coordinates of area

            cell_type -- 'boolean', 'float', 'date', 'string', 'time',
                         'currency', 'percentage' or 'all'

            complete -- boolean

            get_type -- boolean

        Return: list of lists of Python types
        """
        if coord:
            x, y, z, t = self._translate_table_coordinates(coord)
        else:
            x = y = z = t = None
        data = []
        for row in self.traverse(start = y, end = t):
            if z is None:
                width = self.get_width()
            else:
                width = min(z + 1, self.get_width())
            if x is not None:
                width -= x
            values = row.get_values((x, z), cell_type=cell_type,
                                            complete=complete,
                                                get_type=get_type)
            # complete row to match request width
            if complete:
                if get_type:
                    values.extend([(None, None)] * (width - len(values)))
                else:
                    values.extend([None] * (width - len(values)))
            if flat:
                data.extend(values)
            else:
                data.append(values)
        return data


    def iter_values(self, coord=None, cell_type=None, complete=True,
                    get_type=False):
        """Iterate through lines of Python values of the table.

        Filter by coordinates will parse the area defined by the coordinates.

        cell_type, complete, grt_type : see get_values()



        Arguments:

            coord -- str or tuple of int : coordinates of area

            cell_type -- 'boolean', 'float', 'date', 'string', 'time',
                         'currency', 'percentage' or 'all'

            complete -- boolean

            get_type -- boolean

        Return: iterator of lists
        """
        if coord:
            x, y, z, t = self._translate_table_coordinates(coord)
        else:
            x = y = z = t = None
        for row in self.traverse(start = y, end = t):
            if z is None:
                width = self.get_width()
            else:
                width = min(z + 1, self.get_width())
            if x is not None:
                width -= x
            values = row.get_values((x, z), cell_type=cell_type,
                                            complete=complete,
                                                get_type=get_type)
            # complete row to match column width
            if complete:
                if get_type:
                    values.extend([(None, None)] * (width - len(values)))
                else:
                    values.extend([None] * (width - len(values)))
            yield values


    def set_values(self, values, coord=None, style=None, cell_type=None,
                   currency=None):
        """set the value of cells in the table, from the 'coord' position
        with values.

        'coord' is the coordinate of the upper left cell to be modified by
        values. If 'coord' is None, default to the position (0,0) ("A1").
        If 'coord' is an area (e.g. "A2:B5"), the upper left position of this
        area is used as coordinate.

        The table is *not* cleared before the operation, to reset the table
        before setting values, use table.clear().

        A list of lists is expected, with as many lists as rows, and as many
        items in each sublist as cells to be setted. None values in the list
        will create empty cells with no cell type (but eventually a style).

        Arguments:

            coord -- tuple or str

            values -- list of lists of python types

            cell_type -- 'boolean', 'currency', 'date', 'float', 'percentage',
                         'string' or 'time'

            currency -- three-letter str

            style -- unicode
        """
        if coord:
            x, y = self._translate_cell_coordinates(coord)
        else:
            x = y = 0
        if y is None:
            y = 0
        y -= 1
        for row_values in values:
            y += 1
            if not row_values:
                continue
            row = self.get_row(y, clone=True)
            repeated =  row.get_repeated or 1
            if repeated >= 2:
                row.set_repeated(None)
            row.set_values(row_values, start=x, cell_type=cell_type,
                           currency=currency, style=style)
            self.set_row(y, row, clone=False)
            self.__update_width(row)

    #set_table_values = obsolete('set_table_values', set_values)


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
        # raz cache of rows
        self._indexes['_tmap'] = {}
        # Step 3: trim columns to match max_width
        columns = self._get_columns()
        repeated_cols = self.xpath(
                    'table:table-column/@table:number-columns-repeated')
        unrepeated = len(columns) - len(repeated_cols)
        column_width = sum(int(r) for r in repeated_cols) + unrepeated
        diff = column_width - max_width
        if diff > 0:
            for column in reversed(columns):
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
        # raz cache of columns
        self._indexes['_cmap'] = {}
        self._compute_table_cache()

    #rstrip_table = obsolete('rstrip_table', rstrip)


    def transpose(self, coord=None):
        """Swap *in-place* rows and columns of the table.

        If 'coord' is not None, apply transpose only to the area defined by the
        coordinates. Beware, if area is not square, some cells mays be over
        written during the process.

        Arguments:

            coord -- str or tuple of int : coordinates of area

            start -- int or str
        """
        data = []
        if coord is None:
            for row in self.traverse():
                data.append([cell for cell in row.traverse()])
            transposed_data = map(None, *data)
            self.clear()
            new_rows = []
            for row_cells in transposed_data:
                if not isiterable(row_cells):
                    row_cells = (row_cells,)
                row = odf_create_row()
                row.extend_cells(row_cells)
                self.append_row(row, clone=False)
            self._compute_table_cache()
        else:
            x, y, z, t = self._translate_table_coordinates(coord)
            if x is None:
                x = 0
            else:
                x = min(x, self.get_width() - 1)
            if z is None:
                z = self.get_width() - 1
            else:
                z = min(z, self.get_width() - 1)
            if y is None:
                y = 0
            else:
                y = min(y, self.get_height() - 1)
            if t is None:
                t = self.get_height() - 1
            else:
                t = min(t, self.get_height() - 1)
            for row in self.traverse(start=y, end=t):
                data.append([cell for cell in row.traverse(start=x, end=z)])
            transposed_data = map(None, *data)
            # clear locally
            w = z - x + 1
            h = t -y + 1
            if w != h:
                nones = [[None] * w for i in range(h)]
                self.set_values(nones, coord=(x,y,z,t))
            # put transposed
            for idx, row_cells in enumerate(transposed_data):
                if not isiterable(row_cells):
                    row_cells = (row_cells,)
                    transposed_data[idx] = row_cells
            self.set_cells(transposed_data, (x, y, x + h - 1, y + w -1))
            self._compute_table_cache()


    def is_empty(self, aggressive=False):
        """Return whether every cell in the table has no value or the value
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
        return self.get_elements(_xpath_row)


    def traverse(self, start=None, end=None):
        """Yield as many row elements as expected rows in the table, i.e.
        expand repetitions by returning the same row as many times as
        necessary.

            Arguments:

                start -- int

                end -- int

        Copies are returned, use ``set_row`` to push them back.
        """
        idx = -1
        before = -1
        y = 0
        if start is None and end is None:
            for juska in self._tmap:
                idx += 1
                if idx in self._indexes['_tmap']:
                    row = self._indexes['_tmap'][idx]
                else:
                    row = self._get_element_idx2(_xpath_row_idx, idx)
                    self._indexes['_tmap'][idx] = row
                repeated = juska - before
                before = juska
                for i in xrange(repeated or 1):
                    # Return a copy without the now obsolete repetition
                    row = row.clone()
                    row.y = y
                    y += 1
                    if repeated > 1:
                        row.set_repeated(None)
                    yield row
        else:
            if start is None:
                start = 0
            start = max(0, start)
            if end is None:
                try:
                    end = self._tmap[-1]
                except:
                    end = -1
            start_map = _find_odf_idx(self._tmap, start)
            if start_map is None:
                return
            if start_map > 0:
                before = self._tmap[start_map - 1]
            idx = start_map - 1
            before = start - 1
            y = start
            for juska in self._tmap[start_map:]:
                idx += 1
                if idx in self._indexes['_tmap']:
                    row = self._indexes['_tmap'][idx]
                else:
                    row = self._get_element_idx2(_xpath_row_idx, idx)
                    self._indexes['_tmap'][idx] = row
                repeated = juska - before
                before = juska
                for i in xrange(repeated or 1):
                    if y <= end:
                        row = row.clone()
                        row.y = y
                        y += 1
                        if repeated > 1 or (y == start and start > 0):
                            row.set_repeated(None)
                        yield row


    def get_rows(self, coord=None, style=None, content=None):
        """Get the list of rows matching the criteria.

        Filter by coordinates will parse the area defined by the coordinates.

        Arguments:

            coord -- str or tuple of int : coordinates of rows

            content -- regex, unicode

            style -- unicode

        Return: list of rows
        """
        if coord:
            x, y, z, t = self._translate_table_coordinates(coord)
        else:
            x = y = z = t = None
        # fixme : not clones ?
        if not content and not style:
            return [row for row in self.traverse(start=y, end=t)]
        rows = []
        for row in self.traverse(start=y, end=t):
            if content and not row.match(content):
                continue
            if style and style != row.get_style():
                continue
            rows.append(row)
        return rows

    #get_row_list = obsolete('get_row_list', get_rows)


    def _get_row2(self, y, clone = True, create = True):
        if y >= self.get_height():
            if create:
                return odf_create_row()
            else:
                return None
        if clone:
            return self._get_row2_base(y).clone()
        else:
            return self._get_row2_base(y)

    def _get_row2_base(self, y):
        idx = _find_odf_idx(self._tmap, y)
        if idx is not None:
            if idx in self._indexes['_tmap']:
                row = self._indexes['_tmap'][idx]
            else:
                row = self._get_element_idx2(_xpath_row_idx, idx)
                self._indexes['_tmap'][idx] = row
            return row
        return None

    def get_row(self, y, clone = True, create = True):
        """Get the row at the given "y" position.

        Position start at 0. So cell A4 is on row 3.

        A copy is returned, use ``set_cell`` to push it back.

        Arguments:

            y -- int or str

        Return: odf_row
        """
        # fixme : keep repeat ? maybe an option to functions : "raw=False"
        y = self._translate_y_from_any(y)
        row = self._get_row2(y, clone = clone, create = create)
        row.y = y
        return row


    def set_row(self, y, row = None, clone = True):
        """Replace the row at the given position with the new one. Repetions of
        the old row will be adjusted.

        If row is None, a new empty row is created.

        Position start at 0. So cell A4 is on row 3.

        Arguments:

            y -- int

            row -- odf_row

        returns the row, with updated row.y
        """
        if row is None:
            row = odf_create_row()
            repeated = 1
            clone = False
        else:
            repeated = row.get_repeated() or 1
        y = self._translate_y_from_any(y)
        row.y = y
        # Outside the defined table ?
        diff = y - self.get_height()
        if diff == 0:
            row_back = self.append_row(row, _repeated = repeated, clone=clone)
        elif diff > 0:
            self.append_row(odf_create_row(repeated = diff), _repeated=diff, clone=clone)
            row_back = self.append_row(row, _repeated=repeated, clone=clone)
        else:
            # Inside the defined table
            row_back = _set_item_in_vault(y, row, self, _xpath_row_idx, '_tmap', clone=clone)
        #print self.serialize(True)
        # Update width if necessary
        self.__update_width(row_back)
        return row_back


    def insert_row(self, y, row=None, clone=True):
        """Insert the row before the given "y" position. If no row is given,
        an empty one is created.

        Position start at 0. So cell A4 is on row 3.

        If row is None, a new empty row is created.

        Arguments:

            y -- int or str

            row -- odf_row

        returns the row, with updated row.y
        """
        if row is None:
            row = odf_create_row()
            clone = False
        y = self._translate_y_from_any(y)
        diff = y - self.get_height()
        if diff < 0:
            row_back = _insert_item_in_vault(y, row, self, _xpath_row_idx, '_tmap')
        elif diff == 0:
            row_back = self.append_row(row, clone=clone)
        else:
            self.append_row(odf_create_row(repeated=diff), _repeated=diff, clone=False)
            row_back = self.append_row(row, clone=clone)
        row_back.y = y
        # Update width if necessary
        self.__update_width(row_back)
        return row_back


    def extend_rows(self, rows=[]):
        """Append a list of rows at the end of the table.

        Arguments:

            rows -- list of odf_row

        """
        self.extend(rows)
        self._compute_table_cache()
        # Update width if necessary
        width = self.get_width()
        for row in self.traverse():
            if row.get_width() > width:
                width = row.get_width()
        diff = width - self.get_width()
        if diff > 0:
            self.append_column(odf_create_column(repeated=diff))


    def append_row(self, row=None, clone=True, _repeated=None):
        """Append the row at the end of the table. If no row is given, an
        empty one is created.

        Position start at 0. So cell A4 is on row 3.

        Note the columns are automatically created when the first row is
        inserted in an empty table. So better insert a filled row.

        Arguments:

            row -- odf_row

            _repeated -- (optional), repeated value of the row

        returns the row, with updated row.y
        """
        if row is None:
            row = odf_create_row()
            _repeated = 1
        elif clone:
            row = row.clone()
        # Appending a repeated row accepted
        # Do not insert next to the last row because it could be in a group
        self._append(row)
        if _repeated is None:
            _repeated = row.get_repeated() or 1
        self._tmap = _insert_map_once(self._tmap, len(self._tmap), _repeated)
        row.y = self.get_height() - 1
        # Initialize columns
        if not self._get_columns():
            repeated = row.get_width()
            self.insert(odf_create_column(repeated=repeated),
                    position=0)
            self._compute_table_cache()
        # Update width if necessary
        self.__update_width(row)
        return row


    def delete_row(self, y):
        """Delete the row at the given "y" position.

        Position start at 0. So cell A4 is on row 3.

        Arguments:

            y -- int or str
        """
        y = self._translate_y_from_any(y)
        # Outside the defined table
        if y >= self.get_height():
            return
        # Inside the defined table
        _delete_item_in_vault(y, self, _xpath_row_idx, '_tmap')


    def get_row_values(self, y, cell_type=None, complete=True,
                       get_type=False):
        """Shortcut to get the list of Python values for the cells of the row
        at the given "y" position.

        Position start at 0. So cell A4 is on row 3.

        Filter by cell_type, with cell_type 'all' will retrieve cells of any
        type, aka non empty cells.
        If cell_type and complete is True, replace missing values by None.

        If get_type is True, returns a tuple (value, ODF type of value)

        Arguments:

            y -- int, str

            cell_type -- 'boolean', 'float', 'date', 'string', 'time',
                         'currency', 'percentage' or 'all'

            complete -- boolean

            get_type -- boolean

        Return: list of lists of Python types
        """
        values = self.get_row(y, clone=False).get_values(cell_type=cell_type,
                                    complete=complete, get_type=get_type)
        # complete row to match column width
        if complete:
            if get_type:
                values.extend([(None, None)] * (self.get_width() - len(values)))
            else:
                values.extend([None] * (self.get_width() - len(values)))
        return values


    def set_row_values(self, y, values, cell_type=None, currency=None,
                       style=None):
        """Shortcut to set the values of *all* cells of the row at the given
        "y" position.

        Position start at 0. So cell A4 is on row 3.

        Arguments:

            y -- int or str

            values -- list of Python types

            cell_type -- 'boolean', 'currency', 'date', 'float', 'percentage',
                         'string' or 'time'

            currency -- three-letter str

            style -- unicode

        returns the row, with updated row.y
        """
        row = odf_create_row() # needed if clones rows
        row.set_values(values, style=style, cell_type=cell_type,
                       currency=currency)
        return self.set_row(y, row) # needed if clones rows


    def set_row_cells(self, y, cells=[]):
        """Shortcut to set *all* the cells of the row at the given
        "y" position.

        Position start at 0. So cell A4 is on row 3.

        Arguments:

            y -- int or str

            cells -- list of Python types

            style -- unicode

        returns the row, with updated row.y
        """
        row = odf_create_row() # needed if clones rows
        row.extend_cells(cells)
        return self.set_row(y, row) # needed if clones rows


    def is_row_empty(self, y, aggressive=False):
        """Return wether every cell in the row at the given "y" position has
        no value or the value evaluates to False (empty string), and no style.

        Position start at 0. So cell A4 is on row 3.

        If aggressive is True, empty cells with style are considered empty.

        Arguments:

            y -- int or str

            aggressive -- bool
        """
        return self.get_row(y, clone=False).is_empty(aggressive=aggressive)


    #
    # Cells
    #

    def get_cells(self, coord=None, cell_type=None, style=None,
                  content=None, flat=False):
        """Get the cells matching the criteria. If 'coord' is None,
        parse the whole table, else parse the area defined by 'coord'.

        Filter by  cell_type = "all"  will retrieve cells of any
        type, aka non empty cells.

        If flat is True (default is False), the method return a single list
        of all the values, else a list of lists of cells.

        if cell_type, style and content are None, get_cells() will return
        the exact number of cells of the area, including empty cells.

        Arguments:

            coordinates -- str or tuple of int : coordinates of area

            cell_type -- 'boolean', 'float', 'date', 'string', 'time',
                         'currency', 'percentage' or 'all'

            content -- regex, unicode

            style -- unicode

            flat -- boolean

        Return: list of tuples
        """
        if coord:
            x, y, z, t = self._translate_table_coordinates(coord)
        else:
            x = y = z = t = None
        cells = []
        for row in self.traverse(start = y, end = t):
            row_cells = row.get_cells(coord = (x, z), cell_type=cell_type,
                                            style=style, content=content)
            if flat:
                cells.extend(row_cells)
            else:
                cells.append(row_cells)
        return cells

    #get_cell_list = obsolete('get_cell_list', get_cells)


    def get_cell(self, coord, clone=True):
        """Get the cell at the given coordinates.

        They are either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4".

        A copy is returned, use ``set_cell`` to push it back.

        Arguments:

            coord -- (int, int) or str

        Return: odf_cell
        """
        x, y = self._translate_cell_coordinates(coord)
        # Outside the defined table
        if y >= self.get_height():
            cell = odf_create_cell()
        else:
            # Inside the defined table
            cell = self._get_row2_base(y).get_cell(x, clone=clone)
        cell.x = x
        cell.y = y
        return cell


    def get_value(self, coord, get_type=False):
        """Shortcut to get the Python value of the cell at the given
        coordinates.

        If get_type is True, returns the tuples (value, ODF type)

        coord is either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4". If an Area is given, the upper
        left position is used as coord.

        Arguments:

            coord -- (int, int) or str : coordinate

        Return: Python type
        """
        x, y = self._translate_cell_coordinates(coord)
        # Outside the defined table
        if y >= self.get_height():
            if get_type:
                return (None, None)
            else:
                return None
        else:
            # Inside the defined table
            cell = self._get_row2_base(y)._get_cell2_base(x)
            if cell is None:
                if get_type:
                    return (None, None)
                else:
                    return None
            return cell.get_value(get_type=get_type)


    def set_cell(self, coord, cell=None, clone=True):
        """Replace a cell of the table at the given coordinates.

        They are either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4".

        Arguments:

            coord -- (int, int) or str : coordinate

            cell -- odf_cell

        return the cell, with x and y updated
        """
        if cell is None:
            cell = odf_create_cell()
            clone = False
        x, y = self._translate_cell_coordinates(coord)
        cell.x = x
        cell.y = y
        if y >= self.get_height():
            row = odf_create_row()
            cell_back = row.set_cell(x, cell, clone=clone)
            self.set_row(y, row, clone=False)
        else:
            row = self._get_row2_base(y)
            row.y = y
            repeated = row.get_repeated() or 1
            if repeated > 1:
                row = row.clone()
                row.set_repeated(None)
                cell_back = row.set_cell(x, cell, clone=clone)
                self.set_row(y, row, clone=False)
            else:
                cell_back = row.set_cell(x, cell, clone=clone)
                # Update width if necessary, since we don't use set_row
                self.__update_width(row)
        return cell_back


    def set_cells(self, cells, coord=None, clone=True):
        """set the cells in the table, from the 'coord' position.

        'coord' is the coordinate of the upper left cell to be modified by
        values. If 'coord' is None, default to the position (0,0) ("A1").
        If 'coord' is an area (e.g. "A2:B5"), the upper left position of this
        area is used as coordinate.

        The table is *not* cleared before the operation, to reset the table
        before setting cells, use table.clear().

        A list of lists is expected, with as many lists as rows to be set, and
        as many cell in each sublist as cells to be setted in the row.

        Arguments:

            cells -- cell object

            coord -- tuple or str

            values -- list of lists of python types

        """
        if coord:
            x, y = self._translate_cell_coordinates(coord)
        else:
            x = y = 0
        if y is None:
            y = 0
        y -= 1
        for row_cells in cells:
            y += 1
            if not row_cells:
                continue
            row = self.get_row(y, clone=True)
            repeated =  row.get_repeated or 1
            if repeated >= 2:
                row.set_repeated(None)
            row.set_cells(row_cells, start=x, clone=clone)
            self.set_row(y, row, clone=False)
            self.__update_width(row)


    def set_value(self, coord, value, cell_type=None, currency=None,
                  style=None):
        """Set the Python value of the cell at the given coordinates.

        They are either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4".

        Arguments:

            coord -- (int, int) or str

            value -- Python type

            cell_type -- 'boolean', 'currency', 'date', 'float', 'percentage',
                     'string' or 'time'

            currency -- three-letter str

            style -- unicode

        """
        self.set_cell(coord, odf_create_cell(value, cell_type=cell_type,
                                currency=currency, style=style), clone=False)


    def set_cell_image(self, coord, image_frame, type=None):
        """Do all the magic to display an image in the cell at the given
        coordinates.

        They are either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4".

        The frame element must contain the expected image position and
        dimensions.

        Image insertion depends on the document type, so the type must be
        provided or the table element must be already attached to a document.

        Arguments:

            coord -- (int, int) or str

            image_frame -- odf_frame including an image

            type -- 'spreadsheet' or 'text'
        """
        # Test document type
        if type is None:
            body = self.get_document_body()
            if body is None:
                raise ValueError, "document type not found"
            type = {'office:spreadsheet': 'spreadsheet',
                    'office:text': 'text'}.get(body.get_tag())
            if type is None:
                raise ValueError, "document type not supported for images"
        # We need the end address of the image
        x, y = self._translate_cell_coordinates(coord)
        cell = self.get_cell((x, y))
        image_frame = image_frame.clone()
        # Remove any previous paragraph, frame, etc.
        for child in cell.get_children():
            cell.delete(child)
        # Now it all depends on the document type
        if type == 'spreadsheet':
            image_frame.set_frame_anchor_type(None)
            # The frame needs end coordinates
            width, height = image_frame.get_size()
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
        self.set_cell(coord, cell)


    def insert_cell(self, coord, cell=None, clone=True):
        """Insert the given cell at the given coordinates. If no cell is
        given, an empty one is created.

        Coordinates are either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4".

        Cells on the right are shifted. Other rows remain untouched.

        Arguments:

            coord -- (int, int) or str

            cell -- odf_cell

        returns the cell with x and y updated
        """
        if cell is None:
            cell = odf_create_cell()
            clone = False
        if clone:
            cell = cell.clone()
        x, y = self._translate_cell_coordinates(coord)
        row = self._get_row2(y, clone=True)
        row.y = y
        row.set_repeated(None)
        cell_back = row.insert_cell(x, cell, clone=False)
        self.set_row(y, row, clone=False)
        # Update width if necessary
        self.__update_width(row)
        return cell_back


    def append_cell(self, y, cell=None, clone=True):
        """Append the given cell at the "y" coordinate. Repeated cells are
        accepted. If no cell is given, an empty one is created.

        Position start at 0. So cell A4 is on row 3.

        Other rows remain untouched.

        Arguments:

            y -- int

            cell -- odf_cell

        returns the cell with x and y updated
        """
        if cell is None:
            cell = odf_create_cell()
            clone = False
        if clone:
            cell = cell.clone()
        y = self._translate_y_from_any(y)
        row = self._get_row2(y)
        row.y = y
        cell_back = row.append_cell(cell, clone=False)
        self.set_row(y, row)
        # Update width if necessary
        self.__update_width(row)
        return cell_back


    def delete_cell(self, coord):
        """Delete the cell at the given coordinates, so that next cells are
        shifted to the left.

        Coordinates are either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4".

        Use "set_value" for erasing value.

        Arguments:

            coord -- (int, int) or str
        """
        x, y = self._translate_cell_coordinates(coord)
        # Outside the defined table
        if y >= self.get_height():
            return
        # Inside the defined table
        row = self._get_row2_base(y)
        row.delete_cell(x)
        #self.set_row(y, row)


    #
    # Columns
    #

    def _get_columns(self):
        return self.get_elements(_xpath_column)


    def get_columns_width(self):
        return self.get_width()


    def traverse_columns(self, start=None, end=None):
        """Yield as many column elements as expected columns in the table,
        i.e. expand repetitions by returning the same column as many times as
        necessary.

            Arguments:

                start -- int

                end -- int

        Copies are returned, use ``set_column`` to push them back.
        """
        idx = -1
        before = -1
        x = 0
        if start is None and end is None:
            for juska in self._cmap:
                idx += 1
                if idx in self._indexes['_cmap']:
                    column = self._indexes['_cmap'][idx]
                else:
                    column = self._get_element_idx2(_xpath_column_idx, idx)
                    self._indexes['_cmap'][idx] = column
                repeated = juska - before
                before = juska
                for i in xrange(repeated or 1):
                    # Return a copy without the now obsolete repetition
                    column = column.clone()
                    column.x = x
                    x += 1
                    if repeated > 1:
                        column.set_repeated(None)
                    yield column
        else:
            if start is None:
                start = 0
            start = max(0, start)
            if end is None:
                try:
                    end = self._cmap[-1]
                except:
                    end = -1
            start_map = _find_odf_idx(self._cmap, start)
            if start_map is None:
                return
            if start_map > 0:
                before = self._cmap[start_map - 1]
            idx = start_map - 1
            before = start - 1
            x = start
            for juska in self._cmap[start_map:]:
                idx += 1
                if idx in self._indexes['_cmap']:
                    column = self._indexes['_cmap'][idx]
                else:
                    column = self._get_element_idx2(_xpath_column_idx, idx)
                    self._indexes['_cmap'][idx] = column
                repeated = juska - before
                before = juska
                for i in xrange(repeated or 1):
                    if x <= end:
                        column = column.clone()
                        column.x = x
                        x += 1
                        if repeated > 1 or (x == start and start > 0):
                            column.set_repeated(None)
                        yield column


    def get_columns(self, coord=None, style=None):
        """Get the list of columns matching the criteria. Each result is a
        tuple of (x, column).

        Arguments:

            coord -- str or tuple of int : coordinates of columns

            style -- unicode

        Return: list of columns
        """
        if coord:
            x, y, z, t = self._translate_column_coordinates(coord)
        else:
            x = y = z = t = None
        if not style:
            return [column for column in self.traverse_columns(start=x, end=t)]
        columns = []
        for column in self.traverse_columns(start=x, end=t):
            if style != column.get_style():
                continue
            columns.append(column)
        return columns

    #get_column_list = obsolete('get_column_list', get_columns)


    def _get_column2(self, x):
        # Outside the defined table
        if x >= self.get_width():
            return odf_create_column()
        # Inside the defined table
        odf_idx = _find_odf_idx(self._cmap, x)
        if odf_idx is not None:
            column = self._get_element_idx2(_xpath_column_idx, odf_idx)
            # fixme : no clone here => change doc and unit tests
            return column.clone()
            #return row
        return None

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
        x = self._translate_x_from_any(x)
        column = self._get_column2(x)
        column.x = x
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
        x = self._translate_x_from_any(x)
        if column is None:
            column = odf_create_column()
            repeated = 1
        else:
            repeated = column.get_repeated() or 1
        column.x = x
        # Outside the defined table ?
        diff = x - self.get_width()
        if diff == 0:
            column_back = self.append_column(column, _repeated = repeated)
        elif diff > 0:
            self.append_column(odf_create_column(repeated = diff), _repeated = diff)
            column_back = self.append_column(column, _repeated = repeated)
        else:
            # Inside the defined table
            column_back = _set_item_in_vault(x, column, self, _xpath_column_idx, '_cmap')
        return column_back


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
        x = self._translate_x_from_any(x)
        diff = x - self.get_width()
        if diff < 0:
            column_back = _insert_item_in_vault(x, column, self, _xpath_column_idx, '_cmap')
        elif diff == 0:
            column_back = self.append_column(column.clone())
        else:
            self.append_column(odf_create_column(repeated=diff), _repeated = diff)
            column_back = self.append_column(column.clone())
        column_back.x = x
        # Repetitions are accepted
        repeated = column.get_repeated() or 1
        # Update width on every row
        for row in self._get_rows():
            if row.get_width() > x:
                row.insert_cell(x, odf_create_cell(repeated=repeated))
            # Shorter rows don't need insert
            # Longer rows shouldn't exist!
        return column_back


    def append_column(self, column=None, _repeated=None):
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
        else:
            column = column.clone()
        if len(self._cmap) == 0:
            position = 0
        else:
            odf_idx = len(self._cmap) - 1
            last_column = self._get_element_idx2(_xpath_column_idx, odf_idx)
            position = self.index(last_column) + 1
        column.x = self.get_width()
        self.insert(column, position = position)
        # Repetitions are accepted
        if _repeated is None:
            _repeated = column.get_repeated() or 1
        self._cmap = _insert_map_once(self._cmap, len(self._cmap), _repeated)
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
        x = self._translate_x_from_any(x)
        # Outside the defined table
        if x >= self.get_width():
            return
        # Inside the defined table
        _delete_item_in_vault(x, self, _xpath_column_idx, '_cmap')
        # Update width
        width = self.get_width()
        for row in self._get_rows():
            if row.get_width() >= width:
                row.delete_cell(x)


    def get_column_cells(self, x, style=None, content=None, cell_type=None,
                         complete=False):
        """Get the list of cells at the given position.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        Filter by cell_type, with cell_type 'all' will retrieve cells of any
        type, aka non empty cells.

        If complete is True, replace missing values by None.

        Arguments:

            x -- int or str.isalpha()

            cell_type -- 'boolean', 'float', 'date', 'string', 'time',
                         'currency', 'percentage' or 'all'

            content -- regex, unicode

            style -- unicode

            complete -- boolean

        Return: list of odf_cell
        """
        x = self._translate_x_from_any(x)
        if cell_type:
            cell_type = cell_type.lower().strip()
        cells = []
        if not style and not content and not cell_type:
            for row in self.traverse():
                cells.append(row.get_cell(x, clone=True))
            return cells
        for row in self.traverse():
            cell = row.get_cell(x, clone=True)
        # Filter the cells by cell_type
            if cell_type:
                ctype = cell.get_type()
                if not ctype or not (ctype == cell_type or cell_type == 'all'):
                    if complete:
                        cells.append(None)
                    continue
            # Filter the cells with the regex
            if content and not cell.match(content):
                if complete:
                    cells.append(None)
                continue
            # Filter the cells with the style
            if style and style != cell.get_style():
                if complete:
                    cells.append(None)
                continue
            cells.append(cell)
        return cells


    def get_column_values(self, x, cell_type=None, complete=True,
                          get_type=False):
        """Shortcut to get the list of Python values for the cells at the
        given position.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        Filter by cell_type, with cell_type 'all' will retrieve cells of any
        type, aka non empty cells.
        If cell_type and complete is True, replace missing values by None.

        If get_type is True, returns a tuple (value, ODF type of value)

        Arguments:

            x -- int or str.isalpha()

            cell_type -- 'boolean', 'float', 'date', 'string', 'time',
                         'currency', 'percentage' or 'all'

            complete -- boolean

            get_type -- boolean

        Return: list of Python types
        """
        cells = self.get_column_cells(x, style=None, content=None,
                                    cell_type=cell_type, complete=complete)
        values = []
        for cell in cells:
            if cell is None:
                if complete:
                    if get_type:
                        values.append((None, None))
                    else:
                        values.append(None)
                continue
            if cell_type:
                ctype = cell.get_type()
                if not ctype or not (ctype == cell_type or cell_type == 'all'):
                    if complete:
                        if get_type:
                            values.append((None, None))
                        else:
                            values.append(None)
                    continue
            values.append(cell.get_value(get_type=get_type))
        return values


    def set_column_cells(self, x, cells):
        """Shortcut to set the list of cells at the given position.

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


    def set_column_values(self, x, values, cell_type=None, currency=None,
                       style=None):
        """Shortcut to set the list of Python values of cells at the given
        position.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        The list must have the same length than the table height.

        Arguments:

            x -- int or str.isalpha()

            values -- list of Python types

            cell_type -- 'boolean', 'currency', 'date', 'float', 'percentage',
                         'string' or 'time'

            currency -- three-letter str

            style -- unicode
        """
        cells = [odf_create_cell(value, cell_type=cell_type, currency=currency,
                                 style=style) for value in values]
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
            if not cell.is_empty(aggressive=aggressive):
                return False
        return True


    #
    # Named Range
    #


    def get_named_ranges(self, table_name=None):
        """Returns the list of available Name Ranges of the spreadsheet. If
        table_name is provided, limits the search to these tables.
        Beware : named ranges are stored at the body level, thus do not call
        this method on a cloned table.

        Arguments:

            table_names -- str or list of str, names of tables

        Return : list of odf_table_range
        """
        body = self.get_document_body()
        if not body:
            return []
        all_named_ranges = body.get_named_ranges()
        if not table_name:
            return all_named_ranges
        filter = []
        if isinstance(table_name, basestring):
            filter.append(table_name)
        elif isiterable(table_name):
            filter.extend(table_name)
        else:
            raise ValueError, "table_name must be string or Iterable, not %s" % type(table_name)
        return [nr for nr in all_named_ranges if nr.table_name in filter]


    def get_named_range(self, name):
        """Returns the Name Ranges of the specified name. If
        table_name is provided, limits the search to these tables.
        Beware : named ranges are stored at the body level, thus do not call
        this method on a cloned table.

        Arguments:

            name -- str, name of the named range object

        Return : odf_named_range
        """
        body = self.get_document_body()
        if not body:
            raise ValueError, "Table is not inside a document"
        return body.get_named_range(name)


    def set_named_range(self, name, crange, table_name=None, usage=None):
        """Create a Named Range element and insert it in the document.
        Beware : named ranges are stored at the body level, thus do not call
        this method on a cloned table.

        Arguments:

            name -- str, name of the named range

            crange -- str or tuple of int, cell or area coordinate

            table_name -- str, name of the table

            uage -- None or 'print-range', 'filter', 'repeat-column', 'repeat-row'
        """
        body = self.get_document_body()
        if not body:
            raise ValueError, "Table is not inside a document"
        if not name:
            raise ValueError, "Name required."
        if table_name is None:
            table_name = self.get_name()
        named_range = odf_create_named_range(name, crange, table_name, usage)
        body.append_named_range(named_range)


    def delete_named_range(self, name):
        """Delete the Named Range of specified name from the spreadsheet.
        Beware : named ranges are stored at the body level, thus do not call
        this method on a cloned table.

        Arguments:

            name -- str
        """
        name = name.strip()
        if not name:
            raise ValueError, "Name required."
        body = self.get_document_body()
        if not body:
            raise ValueError, "Table is not inside a document."
        body.delete_named_range(name)


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
        # In-memory
        if path_or_file is None:
            file = StringIO()
        # Path
        elif type(path_or_file) is str or type(path_or_file) is unicode:
            file = open(path_or_file, 'wb')
            close_after = True
        # Open file
        else:
            file = path_or_file
        quoted = quotechar * 2
        for values in self.iter_values():
            line = []
            for value in values:
                # Also testing lxml.etree._ElementUnicodeResult
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



class odf_named_range(odf_element):
    """ODF Named Range. Identifies inside the spreadsheet a range of cells of a
    table by a name and the name of the table.

    Name Ranges have the following attributes:

        name -- name of the named range

        table_name -- name of the table

        start -- first cell of the named range, tuple (x, y)

        end -- last cell of the named range, tuple (x, y)

        crange -- range of the named range, tuple (x, y, z, t)

        usage -- None or str, usage of the named range.
    """
    def __init__(self, native_element):
        odf_element.__init__(self, native_element)
        self.name = self.get_attribute('table:name')
        self.usage = self.get_attribute('table:range-usable-as')
        cell_range_address = self.get_attribute('table:cell-range-address')
        if not cell_range_address:
            self.table_name = None
            self.start = None
            self.end = None
            self.crange = None
            return
        name_range = cell_range_address.replace('$', '')
        name, crange = name_range.split('.', 1)
        if name.startswith("'") and name.endswith("'"):
            name = name[1:-1]
        self.table_name = name
        crange = crange.replace('.', '')
        self._set_range(crange)


    def set_usage(self, usage=None):
        """Set the usage of the Named Range. Usage can be None (default) or one
        of :
            'print-range'
            'filter'
            'repeat-column'
            'repeat-row'

        Arguments:

            usage -- None or str
        """
        if usage is not None:
            usage=usage.strip().lower()
            if usage not in ('print-range', 'filter', 'repeat-column',
                             'repeat-row') :
                usage = None
        if usage is None:
            try:
                self.del_attribute('table:range-usable-as')
            except KeyError:
                pass
            self.usage = None
        else:
            self.set_attribute('table:range-usable-as', usage)
            self.usage = usage


    def set_name(self, name):
        """Set the name of the Named Range. The name is mandatory, if a Named
        Range of the same name exists, it will be replaced. Name must contains
        only alphanumerics characters and '_', and can not be of a cell
        coordinates form like 'AB12'.

        Arguments:

            name -- str
        """
        name = name.strip()
        if not name:
            raise ValueError, "Name required."
        for x in name:
            if x in _forbidden_in_named_range:
                raise ValueError, "Character forbidden '%s' " % x
        step = ''
        for x in name:
            if x in string.letters and step in ('', 'A'):
                step = 'A'
                continue
            elif step in ('A', 'A1') and x in string.digits:
                step = 'A1'
                continue
            else:
                step = ''
                break
        if step == 'A1':
            raise ValueError, "Name of the type 'ABC123' is not allowed."
        try:
            body = self.get_document_body()
            named_range = body.get_named_range(name)
            if named_range:
                named_range.delete()
        except:
            pass    # we are not on an inserted in a document.
        self.name = name
        self.set_attribute('table:name', name)


    def set_table_name(self, name):
        """Set the name of the table of the Named Range. The name is mandatory.

        Arguments:

            name -- str
        """
        self.table_name = _table_name_check(name)
        self._update_attributes()


    def _set_range(self, coord):
        digits = _convert_coordinates(coord)
        if len(digits) == 4:
            x, y, z, t = digits
        else:
            x, y = digits
            z, t = digits
        self.start = x, y
        self.end = z, t
        self.crange = x, y, z, t


    def set_range(self, crange):
        """Set the range of the named range. Range can be either one cell
        (like 'A1') or an area ('A1:B2'). It can be provided as an alpha numeric
        value like "A1:B2' or a tuple like (0, 0, 1, 1) or (0, 0).

        Arguments:

            crange -- str or tuple of int, cell or area coordinate
        """
        self._set_range(crange)
        self._update_attributes()


    def _update_attributes(self):
        self.set_attribute('table:base-cell-address',
                           self._make_base_cell_address() )
        self.set_attribute('table:cell-range-address',
                           self._make_cell_range_address() )


    def _make_base_cell_address(self):
        # assuming we got table_name and range
        if ' ' in self.table_name:
            name = "'%s'" % self.table_name
        else:
            name = self.table_name
        return '$%s.$%s$%s' % (name,
                                _digit_to_alpha(self.start[0]),
                                self.start[1] + 1 )


    def _make_cell_range_address(self):
        # assuming we got table_name and range
        if ' ' in self.table_name:
            name = "'%s'" % self.table_name
        else:
            name = self.table_name
        if self.start == self.end:
            return self._make_base_cell_address()
        return '$%s.$%s$%s:.$%s$%s' % (name,
                                    _digit_to_alpha(self.start[0]),
                                    self.start[1] + 1,
                                    _digit_to_alpha(self.end[0]),
                                    self.end[1] + 1)


    def get_values(self, cell_type=None, complete=True,
                   get_type=False, flat=False):
        """Shortcut to retrieve the values of the cells of the named range. See
        table.get_values() for the arguments description and return format.
        """
        body = self.get_document_body()
        if not body:
            raise ValueError, "Table is not inside a document."
        table = body.get_table(name = self.table_name)
        return table.get_values(self.crange, cell_type, complete,
                   get_type, flat)


    def get_value(self, get_type=False):
        """Shortcut to retrieve the value of the first cell of the named range.
        See table.get_value() for the arguments description and return format.
        """
        body = self.get_document_body()
        if not body:
            raise ValueError, "Table is not inside a document."
        table = body.get_table(name = self.table_name)
        return table.get_value(self.start, get_type)


    def set_values(self, values, style=None, cell_type=None,
                   currency=None):
        """Shortcut to set the values of the cells of the named range.
        See table.set_values() for the arguments description.
        """
        body = self.get_document_body()
        if not body:
            raise ValueError, "Table is not inside a document."
        table = body.get_table(name = self.table_name)
        return table.set_values(values, coord=self.crange, style=style,
                   cell_type=cell_type, currency=currency)


    def set_value(self, value, cell_type=None, currency=None,
                  style=None):
        """Shortcut to set the value of the first cell of the named range.
        See table.set_value() for the arguments description.
        """
        body = self.get_document_body()
        if not body:
            raise ValueError, "Table is not inside a document."
        table = body.get_table(name = self.table_name)
        return table.set_value(coord=self.start, value=value,
                               cell_type=cell_type,
                               currency=currency, style=style)



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
            row.append_cell(cell, clone=False)
        table.append_row(row, clone=False)
    return table



# Register
register_element_class('table:table-cell', odf_cell)
register_element_class('table:covered-table-cell', odf_cell)
register_element_class('table:table-row', odf_row, caching=True)
register_element_class('table:table-column', odf_column)
register_element_class('table:table', odf_table, caching=True)
register_element_class('table:named-range', odf_named_range)
