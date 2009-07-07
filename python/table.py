# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from copy import deepcopy

# Import from lpod
from xmlpart import odf_create_element, LAST_CHILD
from document import odf_create_cell, odf_create_column, odf_create_row



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
                    columns.append(deepcopy(column))
            else:
                columns.append(column)

        # 3) The rows
        rows = self.__rows = []
        for row  in odf_element.get_element_list('table:table-row'):

            # Delete the table:number-rows-repeated
            row_repeat = row.get_attribute('table:number-rows-repeated')
            if row_repeat is not None:
                row_repeat = int(repeat)
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
                        cells.append(deepcopy(cell))
                else:
                    cells.append(cell)

            # Append the rows
            for i in range(row_repeat):
                rows.append({'attributes': row.get_attributes(),
                             'cells': deepcopy(cells)})


    #
    # Public API
    #

    def get_odf_element(self):

        # 1) Create the table:table
        table = odf_create_element('<table:table/>')
        for key, value in self.__table_attributes.iteritems():
            table.set_attribute(key, value)

        # 2) Add the columns
        # XXX use repeat!
        for column in self.__columns:
            table.insert_element(column, xmlposition=LAST_CHILD)

        # 3) The rows
        # XXX use repeat!
        for row in self.__rows:

            attributes = row['attributes']
            cells = row['cells']

            # Create the node
            odf_row = odf_create_row()
            for key, value in attributes:
                odf_row.set_attribute(key, value)

            # Add the cell
            # XXX use repeat!
            for cell in cells:
                odf_row.insert_element(cell, xmlposition=LAST_CHILD)

            table.insert_element(odf_row, xmlposition=LAST_CHILD)

        return table

