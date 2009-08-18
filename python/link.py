# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from element import odf_create_element


def odf_create_link(href, name=None, title=None, target_frame=None,
                    style=None, visited_style=None):
    """Return a text:a odf_element.

    Arguments:

        href -- string (an URI)

        name -- unicode

        title -- unicode

        target_name -- '_self', '_blank', '_parent', '_top'

        style -- string

        visited_style -- string
    """
    element = odf_create_element('<text:a xlink:href="%s"/>' % href)
    if name is not None:
        element.set_attribute('office:name', name)
    if title is not None:
        element.set_attribute('office:title', title)
    if target_frame is not None:
        element.set_attribute('office:target-frame-name', target_frame)
        if target_frame == '_blank':
            element.set_attribute('xlink:show', 'new')
        else:
            element.set_attribute('xlink:show', 'replace')
    if style is not None:
        element.set_attribute('text:style-name', style)
    if visited_style is not None:
        element.set_attribute('text:visited-style-name', visited_style)
    return element
