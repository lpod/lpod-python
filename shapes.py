# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Hervé Cauwelier <herve@itaapy.com>
#          Romain Gauthier <romain@itaapy.com>
#
# This file is part of Lpod (see: http://lpod-project.org).
# Lpod is free software; you can redistribute it and/or modify it under
# the terms of either:
#
# a) the GNU General Public License as published by the Free Software
#    Foundation, either version 3 of the License, or (at your option)
#    any later version.
#    Lpod is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#    along with Lpod.  If not, see <http://www.gnu.org/licenses/>.
#
# b) the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
#

# Import from lpod
from element import odf_element, odf_create_element, register_element_class


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
        element.set_style(style)
    if text_style:
        element.set_text_style(text_style)
    if shape_id:
        element.set_id(shape_id)
    if layer:
        element.set_layer(layer)
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



class odf_shape(odf_element):

    def get_id(self):
        return self.get_attribute('draw:id')


    def set_id(self, name):
        return self.set_attribute('draw:id', name)


    def get_layer(self):
        return self.get_attribute('draw:layer')


    def set_layer(self, name):
        return self.set_attribute('draw:layer', name)


    def get_style(self):
        return self.get_attribute('draw:style-name')


    def set_style(self, name):
        return self.set_style_attribute('draw:style-name', name)


    def get_text_style(self):
        return self.get_attribute('draw:text-style-name')


    def set_text_style(self, name):
        return self.set_style_attribute('draw:text-style-name', name)


    def get_formatted_text(self, context):
        result = []
        for child in self.get_children():
            result.append(child.get_formatted_text(context))
        result.append(u"\n")
        return u"".join(result)



for name in ('draw:custom-shape', 'draw:line', 'draw:polyline',
        'draw:polygon', 'draw:regular-polygon', 'draw:path', 'draw:rect',
        'draw:ellipse', 'draw:circle', 'draw:connector'):
    register_element_class(name, odf_shape)
