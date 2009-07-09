# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from document import odf_create_cell, odf_create_column, odf_create_row
from utils import _get_cell_coordinates
from xmlpart import odf_create_element, LAST_CHILD



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



class odf_table:

    def __init__(self, name=None, style=None, data=None, odf_element=None):
        """Create an odf_table object.

        We have two manners to create a new odf_table:
        1) With 'python' data: we must fill name, style and data. data must
           be  a matrix (a list of list) of python objects.
        2) With odf_element

        name -- string
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
        self.__table_attributes['table:name'] = name
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
        for row  in odf_element.get_element_list('table:table-row'):

            # Delete the table:number-rows-repeated
            row_repeat = row.get_attribute('table:number-rows-repeated')
            if row_repeat is not None:
                row_repeat = int(row_repeat)
                row.del_attribute('table:number-rows-repeated')
            else:
                row_repeat = 1

            # The cells
            cells = []
            for cell in row.get_element_list('table:table-cell'):
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
                    rows.append({'attributes': row.get_attributes(),
                                 'cells': [ cell.clone() for cell in cells ]})
            else:
                rows.append({'attributes': row.get_attributes(),
                             'cells': cells})



    def __get_odf_row(self, row):
        attributes = row['attributes']
        cells = row['cells']

        # Create the node
        odf_row = odf_create_row()
        for key, value in attributes:
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


    def get_cell(self, coordinates):
        x, y = _get_cell_coordinates(coordinates)
        return self.__rows[y - 1]['cells'][x - 1]


    def set_cell(self, coordinates, odf_cell):
        # XXX auto-adjust the table size ?
        x, y = _get_cell_coordinates(coordinates)
        self.__rows[y - 1]['cells'][x - 1] = odf_cell

