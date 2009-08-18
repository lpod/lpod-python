# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from element import odf_create_element


def odf_create_reference_mark(name):
    """
    Arguments:

        name -- unicode
    """
    return odf_create_element(u'<text:reference-mark text:name="%s"/>' %
                              name)



def odf_create_reference_mark_start(name):
    """
    Arguments:

        name -- unicode
    """
    return odf_create_element(u'<text:reference-mark-start text:name="%s"/>' %
                              name)



def odf_create_reference_mark_end(name):
    """
    Arguments:

        name -- unicode
    """
    return odf_create_element(u'<text:reference-mark-end text:name="%s"/>' %
                              name)
