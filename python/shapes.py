# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from element import odf_create_element


def _odf_create_shape(type, style=None, text_style=None, shape_id=None,
                     layer=None):
    """Create a shape element.

    Arguments:

        type -- str

        style -- unicode

        text_style -- unicode

        shape_id -- unicode

        layer -- str

    Return: odf_element
    """
    element = odf_create_element(type)
    if style:
        element.set_attribute('draw:style-name', style)
    if text_style:
        element.set_attribute('draw:text-style-name', text_style)
    if shape_id:
        element.set_attribute('draw:id', shape_id)
    if layer:
        element.set_attribute('draw:layer', layer)
    return element



def odf_create_line(style=None, text_style=None, shape_id=None, layer=None,
                    p1=None, p2=None):
    """Create a line shape.

    Arguments:

        style -- unicode

        text_style -- unicode

        shape_id -- unicode

        layer -- str

        p1 -- (str, str)

        p2 -- (str, str)

    Return: odf_element
    """
    type = '<draw:line/>'
    element = _odf_create_shape(type, style=style, text_style=text_style,
                                shape_id=shape_id, layer=layer)
    if p1:
        element.set_attribute('svg:x1', p1[0])
        element.set_attribute('svg:y1', p1[1])
    if p2:
        element.set_attribute('svg:x2', p2[0])
        element.set_attribute('svg:y2', p2[1])
    return element



def odf_create_rectangle(style=None, text_style=None, shape_id=None,
                         layer=None, size=('1cm', '1cm'), position=None):
    """Create a rectangle shape.

    Arguments:

        style -- unicode

        text_style -- unicode

        shape_id -- unicode

        layer -- str

        size -- (str, str)

        position -- (str, str)

    Return: odf_element
    """
    type = '<draw:rect/>'
    element = _odf_create_shape(type, style=style, text_style=text_style,
                                shape_id=shape_id, layer=layer)
    element.set_attribute('svg:width', size[0])
    element.set_attribute('svg:height', size[1])
    if position:
        element.set_attribute('svg:x', position[0])
        element.set_attribute('svg:y', position[1])
    return element



def odf_create_ellipse(style=None, text_style=None, shape_id=None,
                       layer=None, size=('1cm', '1cm'), position=None):
    """Create a ellipse shape.

    Arguments:

        style -- unicode

        text_style -- unicode

        shape_id -- unicode

        layer -- str

        size -- (str, str)

        position -- (str, str)

    Return: odf_element
    """
    type = '<draw:ellipse/>'
    element = _odf_create_shape(type, style=style, text_style=text_style,
                                shape_id=shape_id, layer=layer)
    element.set_attribute('svg:width', size[0])
    element.set_attribute('svg:height', size[1])
    if position:
        element.set_attribute('svg:x', position[0])
        element.set_attribute('svg:y', position[1])
    return element



def odf_create_connector(style=None, text_style=None, shape_id=None,
                         layer=None, connected_shapes=None, glue_points=None,
                         p1=None, p2=None):
    """Create a ellipse shape.

    Arguments:

        style -- unicode

        text_style -- unicode

        shape_id -- unicode

        layer -- str

        connected_shapes -- (shape, shape)

        glue_points -- (point, point)

        p1 -- (str, str)

        p2 -- (str, str)

    Return: odf_element
    """
    type = '<draw:connector/>'
    element = _odf_create_shape(type, style=style, text_style=text_style,
                                shape_id=shape_id, layer=layer)
    if connected_shapes:
        start_shape_id = connected_shapes[0].get_attribute('draw:id')
        end_shape_id = connected_shapes[1].get_attribute('draw:id')
        element.set_attribute('draw:start-shape', start_shape_id)
        element.set_attribute('draw:end-shape', end_shape_id)
    if glue_points:
        element.set_attribute('draw:start-glue-point', str(glue_points[0]))
        element.set_attribute('draw:end-glue-point', str(glue_points[1]))
    if p1:
        element.set_attribute('svg:x1', p1[0])
        element.set_attribute('svg:y1', p1[1])
    if p2:
        element.set_attribute('svg:x2', p2[0])
        element.set_attribute('svg:y2', p2[1])
    return element

