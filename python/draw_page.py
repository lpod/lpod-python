# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from xmlpart import register_element_class, odf_element, odf_create_element


def odf_create_draw_page(name, page_id=None, master_page=None,
                         page_layout=None, style=None):
    """This element is a container for content in a drawing or presentation
    document.

    Arguments:

        name -- unicode

        master_page -- str

        page_layout -- str

        page_id -- str

        style -- str

    Return: odf_element
    """
    element = odf_create_element('<draw:page/>')
    element.set_attribute(u'draw:name', name)
    if style:
        element.set_attribute('draw:style-name', style)
    if master_page:
        element.set_attribute('draw:master-page-name', master_page)
    if page_layout:
        element.set_attribute('presentation:presentation-page-layout-name',
                              page_layout)
    if page_id:
        element.set_attribute('draw:id', page_id)
    return element



class odf_draw_page(odf_element):
    """Specialised element for pages of presentation and drawing.
    """
    def get_page_name(self):
        return self.get_attribute('draw:name')


    def set_page_name(self, name):
        self.set_attribute('draw:name', name)



register_element_class('draw:page', odf_draw_page)
