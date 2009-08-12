# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library

# Import from lpod
from xmlpart import odf_create_element


def odf_create_section(style=None):
    """Create a section element of the given style.

    Arguments:

        style -- unicode

    Return: odf_element
    """
    element = odf_create_element('<text:section/>')
    if style:
        element.set_attribute('text:style-name', style)
    return element
