# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from element import odf_create_element


def odf_create_bookmark(name):
    """
    Arguments:

        name -- unicode
    """
    return odf_create_element(u'<text:bookmark text:name="%s"/>' %
                              name)



def odf_create_bookmark_start(name):
    """
    Arguments:

        name -- unicode
    """
    return odf_create_element(u'<text:bookmark-start text:name="%s"/>' %
                              name)



def odf_create_bookmark_end(name):
    """
    Arguments:

        name -- unicode
    """
    return odf_create_element(u'<text:bookmark-end text:name="%s"/>' %
                              name)
