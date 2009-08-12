# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from xmlpart import odf_create_element


def odf_create_span(text=None, style=None):
    """Create a span element of the given style containing the optional
    given text.

    Arguments:

        style -- unicode

        text -- unicode

    Return: odf_element
    """
    element = odf_create_element('<text:span/>')
    if text:
        element.set_text(text)
    if style:
        element.set_attribute('text:style-name', style)
    return element
