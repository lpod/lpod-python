# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from paragraph import odf_paragraph
from element import register_element_class, odf_create_element


def odf_create_heading(level, text=None, restart_numbering=False,
                       start_value=None, style=None):
    """Create a heading element of the given style and level, containing the
    optional given text.

    Level count begins at 1.

    Arguments:

        level -- int

        text -- unicode

        restart_numbering -- bool

        start_value -- int

        style -- unicode

    Return: odf_element
    """
    data = '<text:h text:outline-level="%d"/>'
    element = odf_create_element(data % level)
    if text:
        element.set_text(text)
    if restart_numbering:
        element.set_attribute('text:restart-numbering', 'true')
    if start_value:
        element.set_attribute('text:start-value', start_value)
    if style:
        element.set_attribute('text:style-name', style)
    return element



class odf_heading(odf_paragraph):
    """Specialised element for headings, which themselves are Specialised
    paragraphs.
    """
    # TODO change numbering options
    pass



register_element_class('text:h', odf_heading)
