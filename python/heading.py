# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from xmlpart import register_element_class
from paragraph import odf_paragraph


class odf_heading(odf_paragraph):
    """Specialised element for headings, which themselves are Specialised
    paragraphs.
    """
    # TODO change numbering options
    pass



register_element_class('text:h', odf_heading)
