# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
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
from image import odf_create_image
from element import odf_create_element, odf_element, register_element_class
from paragraph import odf_create_paragraph


def odf_create_frame(name=None, size=('1cm', '1cm'), anchor_type='paragraph',
                     page_number=None, position=None, style=None):
    """Create a frame element of the given size. If positioned by page, give
    the page number and the x, y position.

    Size is a 2-tuple (width, height) and position is a 2-tuple (left,
    top); both are strings including the unit, e.g. ('10cm', '15cm').

    Frames are not useful by themselves. You may consider calling
    odf_create_image_frame or odf_create_text_frame directly.

    Arguments:

        name -- unicode

        size -- (str, str)

        anchor_type -- 'page', 'frame', 'paragraph', 'char' or 'as-char'

        page -- int (when anchor_type == 'page')

        position -- (str, str)

        style -- unicode

    Return: odf_element
    """
    data = (u'<draw:frame svg:width="%s" svg:height="%s" '
            u'text:anchor-type="%s"/>')
    element = odf_create_element(data % (size[0], size[1], anchor_type))
    if name:
        element.set_attribute('draw:name', name)
    if page_number is not None:
        element.set_attribute('text:anchor-page-number', str(page_number))
    if position is not None:
        element.set_attribute('svg:x', position[0])
        element.set_attribute('svg:y', position[1])
    if style is not None:
        element.set_attribute('draw:style-name', style)
    return element



def odf_create_image_frame(uri, text=None, size=('1cm', '1cm'),
                           position=None, style=None):
    """Create a ready-to-use image, since it must be embedded in a
    frame. The optionnal text will appear above the image. Size is a 2-tuple
    (width, height) and position is a 2-tuple (left, top); both are strings
    including the unit, e.g. ('21cm', '29.7cm').

    Arguments:

        uri -- str

        text -- unicode

        size -- (str, str)

        position -- (str, str)

        style -- unicode

    Return: odf_element
    """
    frame = odf_create_frame(size=size, position=position, style=style)
    image = odf_create_image(uri)
    if text:
        image.set_text_content(text)
    frame.append_element(image)
    return frame



def odf_create_text_frame(text_or_element, size=('1cm', '1cm'),
                          position=None, style=None, text_style=None):
    """Create a ready-to-use image image, since it must be embedded in a
    frame. Size is a 2-tuple (width, height) and position is a 2-tuple (left,
    top); both are strings including the unit, e.g. ('21cm', '29.7cm'). Images
    are supposed to be embedded by default; if they remain outside the
    packaging, set link to True.

    Arguments:

        text_or_element -- unicode or odf_element

        size -- (str, str)

        position -- (str, str)

        style -- unicode

        text_style -- unicode

    Return: odf_element
    """
    frame = odf_create_frame(size=size, position=position, style=style)
    if text_style:
        frame.set_attribute('draw:text-style-name', text_style)
    text_box = odf_create_element('<draw:text-box/>')
    if not isinstance(text_or_element, (list, tuple)):
        text_or_element = [text_or_element]
    for item in text_or_element:
        if type(item) is unicode:
            item = odf_create_paragraph(item, style=text_style)
        text_box.append_element(item)
    frame.append_element(text_box)
    return frame



class odf_frame(odf_element):

    def get_size(self):
        get_attr = self.get_attribute
        return get_attr('svg:width'), get_attr('svg:height')


    def set_size(self, size):
        self.set_attribute('svg:width', size[0])
        self.set_attribute('svg:height', size[1])


    def get_position(self):
        get_attr = self.get_attribute
        return get_attr('svg:x'), get_attr('svg:y')


    def set_position(self, position):
        self.set_attribute('svg:x', position[0])
        self.set_attribute('svg:y', position[1])


    def get_formated_text(self, context):
        result = []
        for element in self.get_children():
            tag = element.get_tagname()
            if tag == 'draw:image':
                result.append(u'[Image %s]\n' %
                              element.get_attribute('xlink:href'))
            elif tag == 'draw:text-box':
                subresult = [u'  ']
                for element in element.get_children():
                    subresult.append(element.get_formated_text(context))
                subresult = u''.join(subresult)
                subresult = subresult.replace(u'\n', u'\n  ')
                subresult.rstrip(' ')
                result.append(subresult)
            else:
                result.append(element.get_formated_text(context))
        result.append(u'\n')
        return u''.join(result)



register_element_class('draw:frame', odf_frame)
