# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from xmlpart import register_element_class, odf_element


class odf_list(odf_element):
    """Specialised element for lists.
    """
    def insert_item(self, text, position):
        raise NotImplementedError


    def append_item(self, text):
        raise NotImplementedError



register_element_class('text:list', odf_list)
