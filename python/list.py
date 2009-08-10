# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from xmlpart import register_element_class, odf_element
from document import odf_create_list_item


class odf_list(odf_element):
    """Specialised element for lists.
    """

    def insert_item(self, item, position):
        # Check if the item is already a list-item
        tag_name = item.get_name() if isinstance(item, odf_element) else None
        if tag_name != 'text:list-item':
            item = odf_create_list_item(item)
        self.insert_element(item, position=position)


    def append_item(self, item):
        # Check if the item is already a list-item
        tag_name = item.get_name() if isinstance(item, odf_element) else None
        if tag_name != 'text:list-item':
            item = odf_create_list_item(item)
        self.append_element(item)



register_element_class('text:list', odf_list)
