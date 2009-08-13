# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from xmlpart import odf_create_element


def odf_create_image(uri):
    """Create an image element showing the image at the given URI.

    Warning: image elements must be stored in a frame.

    Arguments:

        uri -- str

    Return: odf_element
    """
    return odf_create_element('<draw:image xlink:href="%s"/>' % uri)
