# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from xmlpart import register_element_class, odf_element


class odf_page(odf_element):
    """Specialised element for pages of a presentation.
    """
    # TODO rename the page
    pass



register_element_class('draw:page', odf_page)
