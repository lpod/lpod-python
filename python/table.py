# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from csv import reader, Sniffer

# Import from lpod
from utils import Boolean, Date, DateTime, Duration
from utils import get_value, _get_cell_coordinates, _set_value_and_type
from vfs import vfs
from xmlpart import odf_create_element, LAST_CHILD



def _get_python_value(data, encoding):
    data = unicode(data, encoding)

    # An int ?
    try:
        return int(data)
    except ValueError:
        pass

    # An float ?
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

    # XXX Try some other types ?

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
            target.insert_element(current_element, xmlposition=LAST_CHILD)

            # Current element is now this element
            current_element = element
            current_element_serialized = element_serialized
            repeat = 1

    # Insert the last elements
    if repeat > 1:
        current_element.set_attribute('table:number-columns-repeated',
                                     str(repeat))
    target.insert_element(current_element, xmlposition=LAST_CHILD)



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



# XXX useful?
def odf_create_cell(value=None, representation=None, cell_type=None,
                    currency=None):
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

    Return: odf_element
    """

    cell = odf_create_element('<table:table-cell/>')
    representation = _set_value_and_type(cell, value=value,
                                         representation=representation,
                                         value_type=cell_type,
                                         currency=currency)
    if representation is not None:
        cell.set_text_content(representation)
    return cell



# XXX useful?
def odf_create_row(width=None):
    """Create a row element, optionally filled with "width" number of cells.

    Arguments:

        width -- int

    Return: odf_element
    """
    row = odf_create_element('<table:table-row/>')
    if width is not None:
        for i in xrange(width):
            cell = odf_create_cell(u"")
            row.insert_element(cell, LAST_CHILD)
    return row



# XXX useful?
def odf_create_column(style=None):
    """Create a column element of the optionally given style.

    Arguments:

        style -- unicode

    Return: odf_element
    """
    element = odf_create_element('<table:table-column/>')
    if style:
        element.set_attribute('table:style-name', style)
    return element



def odf_create_table(name, width=None, height=None, style=None):
    """Create a table element, optionally prefilled with "width" columns and
    "height" rows, and of the optionally given style.

    Arguments:

        name -- unicode

        width -- int

        height -- int

        style -- unicode

    Return: odf_element
    """
    name = name
    element = odf_create_element(u'<table:table table:name="%s"/>' % name)
    if width is not None or height is not None:
        width = width if width is not None else 1
        height = height if height is not None else 1
        for i in xrange(height):
            row = odf_create_row(width)
            element.insert_element(row, LAST_CHILD)
    if style:
        element.set_attribute('table:style-name', style)
    return element



class odf_table(object):

    def __init__(self, name=None, style=None, data=None, odf_element=None):
        """Create an odf_table object.

        We have two manners to create a new odf_table:

        1) With 'python' data: we must fill name, style and data. data must
           be  a matrix (a list of list) of python objects.
        2) With an odf_element

        name -- unicode

        style -- string

        data -- list / tuple of list / tuple

        odf_element -- odf_element
        """

        # Attributes of table:table
        self.__table_attributes = {}

        # List of odf_element
        self.__columns = []

        # List of dict {'attributes': {}, 'cells': []}
        self.__rows = []

        # Load the state
        if name is not None and style is not None and data is not None:
            self.__load_state_from_list(name, style, data)
        elif odf_element is not None:
            self.__load_state_from_odf_element(odf_element)
        else:
            raise ValueError, 'unexpected arguments'


    #
    # Private API
    #

    def __load_state_from_list(self, name, style, data):

        # 1) table attributes
        self.__table_attributes['table:name'] = name.encode('utf-8')
        self.__table_attributes['table:style-name'] = style

        # Nothing ??
        if len(data) == 0:
            self.__columns = []
            self.__rows = []
            return

        # 2) The columns
        columns_number = len(data[0])
        # XXX style=?
        self.__columns = [ odf_create_column('Standard')
                           for i in range(columns_number) ]

        # 3) The rows
        rows = self.__rows = []
        for row_data in data:
            cells = []

            # The columns number must be constant
            if len(row_data) != columns_number:
                raise ValueError, 'the columns number must be constant'

            # Append
            for cell_data in row_data:
                cells.append(odf_create_cell(cell_data))

            # In table
            rows.append({'attributes': {},
                         'cells': cells})


    def __load_state_from_odf_element(self, odf_element):

        # 1) table attributes
        self.__table_attributes = odf_element.get_attributes()

        # 2) The columns
        columns = self.__columns = []
        for column in odf_element.get_element_list('table:table-column'):
            # Delete the table:number-columns-repeated attribute
            repeat = column.get_attribute('table:number-columns-repeated')
            if repeat is not None:
                column.del_attribute('table:number-columns-repeated')
                repeat = int(repeat)
                for i in range(repeat):
                    columns.append(column.clone())
            else:
                columns.append(column)

        # 3) The rows
        rows = self.__rows = []
        empty_rows = []
        for row  in odf_element.get_element_list('table:table-row'):

            # An empty row ?
            if _is_odf_row_empty(row):
                empty_rows.append(row)
                continue

            # We must append the last empty rows
            for empty_row in empty_rows:
                _append_odf_row(empty_row, rows)
                empty_rows = []

            # And we append this new row
            _append_odf_row(row, rows)


    def __get_odf_row(self, row):
        attributes = row['attributes']
        cells = row['cells']

        # Create the node
        odf_row = odf_create_row()
        for key, value in attributes.iteritems():
            odf_row.set_attribute(key, value)

        # Add the cells
        _insert_elements(cells, odf_row)

        return odf_row


    def __insert_rows(self, table):
        rows = self.__rows

        # No rows => nothing to do
        if not rows:
            return

        # At least a row
        current_row = self.__get_odf_row(rows[0])
        current_row_serialized = current_row.serialize()
        repeat = 1
        for row in rows[1:]:
            row = self.__get_odf_row(row)
            row_serialized = row.serialize()
            if row_serialized == current_row_serialized:
                repeat += 1
            else:
                # Insert the current_row
                if repeat > 1:
                    current_row.set_attribute('table:number-rows-repeated',
                                              str(repeat))
                table.insert_element(current_row, xmlposition=LAST_CHILD)

                # Current row is now this row
                current_row = row
                current_row_serialized = row_serialized
                repeat = 1

        # Insert the last rows
        if repeat > 1:
            current_row.set_attribute('table:number-rows-repeated',
                                      str(repeat))
        table.insert_element(current_row, xmlposition=LAST_CHILD)


    #
    # Public API
    #

    # FIXME rename to "to_odf_element()"
    def get_odf_element(self):

        # 1) Create the table:table
        table = odf_create_element('<table:table/>')
        for key, value in self.__table_attributes.iteritems():
            table.set_attribute(key, value)

        # 2) Add the columns
        _insert_elements(self.__columns, table)

        # 3) The rows
        self.__insert_rows(table)

        return table


    def get_formated_text(self, context):
        result = []
        for row in self.__rows:
            for cell in row['cells']:
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
    # Cells
    #

    def get_cell(self, coordinates):
        x, y = _get_cell_coordinates(coordinates)
        return self.__rows[y - 1]['cells'][x - 1]


    def set_cell(self, coordinates, odf_cell):
        # XXX auto-adjust the table size ?
        x, y = _get_cell_coordinates(coordinates)
        self.__rows[y - 1]['cells'][x - 1] = odf_cell


    def get_cell_list(self, regex=None, style=None):
        # TODO return list of coordinates
        raise NotImplementedError


    def get_size(self):
        return len(self.__columns), len(self.__rows)


    def get_name(self):
        return self.__table_attributes['table:name']


    #
    # Rows
    #

    def get_row_list(self, regex=None, style=None):
        # TODO return list of row numbers (the 3 of (0, 3),
        # not the letter '4' of 'A4')
        raise NotImplementedError


    # XXX Add a cells argument ??
    def add_row(self, number=1, position=None):
        """Insert number rows before the row 'position' (append if None)
        """
        rows = self.__rows
        row_size = len(self.__columns)

        if position is not None:
            position -= 1
            for i in range(number):
                rows.insert(position,
                            {'attributes': {},
                             'cells': [ odf_create_cell()
                                        for i in range(row_size) ]})
        else:
            for i in range(number):
                rows.append({'attributes': {},
                             'cells': [ odf_create_cell()
                                        for i in range(row_size) ]})


    #
    # Columns
    #

    def get_column_list(self, regex=None, style=None):
        # TODO return list of column numbers (the 0 of (0, 3),
        # not the letter 'A' of 'A4')
        raise NotImplementedError


    # XXX Add a cells argument ??
    def add_column(self, number=1, position=None):
        """Insert number columns before the column 'position' (append if None)
        """
        columns = self.__columns
        rows = self.__rows

        if position is not None:
            position -= 1
            for i in range(number):

                # Append an empty column info
                # XXX Style = ?
                columns.insert(position, odf_create_column('Standard'))

                # And now, insert empty cells
                for row in rows:
                    cells = row['cells']
                    cells.insert(position, odf_create_cell())
        else:
            for i in range(number):

                # Append an empty column info
                # XXX Style = ?
                columns.append(odf_create_column('Standard'))

                # And now, insert empty cells
                for row in rows:
                    cells = row['cells']
                    cells.append(odf_create_cell())


    def export_to_csv(self, target, delimiter=';', quotechar='"',
                      lineterminator='\n', encoding='utf-8'):
        """target must support the write method
        """

        for row in self.__rows:
            current_row = []
            for cell in row['cells']:

                # Get value
                value = get_value(cell)
                if type(value) is unicode:
                    value = value.encode(encoding)
                if type(value) is str:
                    value = value.strip()
                value = '' if value is None else str(value)

                # Quote
                value = value.replace(quotechar, '\\' + quotechar)
                value = '%s%s%s' % (quotechar, value, quotechar)

                # Append !
                current_row.append(value)

            target.write(delimiter.join(current_row))
            target.write(lineterminator)



def import_from_csv(fileobj, name, style, delimiter=None, quotechar=None,
                    lineterminator=None, encoding='utf-8'):
    """Convert the CSV fileobj to a odf_table.

    Arguments:

      fileobj -- a file object or an URI

      name -- unicode

      style -- string

      delimiter -- string

      quotechar -- string

      lineterminator -- string

      encoding -- string
    """

    # Load the data
    # XXX We load the entire file, this can be a problem with a very big file
    if isinstance(fileobj, str):
        fileobj = vfs.open(fileobj)
    data = fileobj.read().splitlines(True)

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
    rows = [ [ _get_python_value(value, encoding) for value in line]
             for line in csv ]

    return odf_table(name=name, style=style, data=rows)

