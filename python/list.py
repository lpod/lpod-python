# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from xmlpart import register_element_class, odf_element
from xmlpart import FIRST_CHILD, LAST_CHILD, NEXT_SIBLING, PREV_SIBLING
from document import odf_create_list_item


class odf_list(odf_element):
    """Specialised element for lists.
    """
    def insert_item(self, text_or_element, position):
        item = odf_create_list_item(text_or_element)
        prev_sibling = self.get_children()
        if not prev_sibling:
            self.append_element(item)
            return
        prev_sibling = prev_sibling[0]
        # XXX Can we improve this ?
        if position < 0:
            while position < 0:
                sibling = prev_sibling.get_prev_sibling()
                if sibling is not None:
                    prev_sibling = sibling
                position += 1
        else:
            while position > 0:
                sibling = prev_sibling.get_next_sibling()
                if sibling is not None:
                    prev_sibling = sibling
                position -= 1
        prev_sibling.insert_element(item, NEXT_SIBLING)


    def append_item(self, text_or_element):
        item = odf_create_list_item(text_or_element)
        self.append_element(item)




register_element_class('text:list', odf_list)
