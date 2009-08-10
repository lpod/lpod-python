# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from xmlpart import register_element_class, odf_element
from document import odf_create_list_item


class odf_list(odf_element):
    """Specialised element for lists.
    """
    def insert_item(self, text_or_element, position):
        item = odf_create_list_item(text_or_element)
        self.insert_element(item, position=position)


    def append_item(self, text_or_element):
        item = odf_create_list_item(text_or_element)
        self.append_element(item)




register_element_class('text:list', odf_list)
