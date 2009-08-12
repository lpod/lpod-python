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



def odf_create_imageframe(uri, size, position=None, style=None):
    """Create a ready-to-use image image, since it must be embedded in a
    frame. Size is a 2-tuple (width, height) and position is a 2-tuple (left,
    top); both are strings including the unit, e.g. ('21cm', '29.7cm'). Images
    are supposed to be embedded by default; if they remain outside the
    packaging, set link to True.

    Arguments:

        uri -- str

        size -- (str, str)

        position -- (str, str)

        style -- unicode

    Return: odf_element
    """
    raise NotImplementedError
