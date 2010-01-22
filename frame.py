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

    Size is a (width, height) tuple and position is a (left, top) tuple; items
    are strings including the unit, e.g. ('10cm', '15cm').

    Frames are not useful by themselves. You should consider calling
    odf_create_image_frame or odf_create_text_frame directly.

    Arguments:

        name -- unicode

        size -- (str, str)

        anchor_type -- 'page', 'frame', 'paragraph' (default), 'char'
                       or 'as-char'

        page_number -- int (when anchor_type == 'page')

        position -- (str, str)

        style -- unicode

    Return: odf_element
    """
    element = odf_create_element(u'<draw:frame/>')
    element.set_frame_size(size)
    element.set_frame_anchor_type(anchor_type, page_number=page_number)
    if name:
        element.set_attribute('draw:name', name)
    if position is not None:
        element.set_frame_position(position)
    if style is not None:
        element.set_attribute('draw:style-name', style)
    return element



def odf_create_image_frame(uri, text=None, size=('1cm', '1cm'),
        anchor_type='paragraph', page_number=None, position=None, style=None):
    """Create a ready-to-use image, since it must be embedded in a
    frame.

    The optionnal text will appear above the image.

    Size is a (width, height) tuple and position is a (left, top) tuple; items
    are strings including the unit, e.g. ('21cm', '29.7cm').

    Arguments:

        uri -- str

        text -- unicode

        size -- (str, str)

        anchor_type -- 'page', 'frame', 'paragraph', 'char' or 'as-char'

        page_number -- int (when anchor_type == 'page')

        position -- (str, str)

        style -- unicode

    Return: odf_element
    """
    frame = odf_create_frame(size=size, anchor_type=anchor_type,
            page_number=page_number, position=position, style=style)
    image = odf_create_image(uri)
    if text:
        image.set_text_content(text)
    frame.append_element(image)
    return frame



def odf_create_text_frame(text_or_element, size=('1cm', '1cm'),
        anchor_type='paragraph', page_number=None, position=None, style=None,
        text_style=None):
    """Create a ready-to-use text box, since it must be embedded in a frame.

    Size is a (width, height) tuple and position is a (left, top) tuple; items
    are strings including the unit, e.g. ('21cm', '29.7cm').

    Arguments:

        text_or_element -- unicode or odf_element

        size -- (str, str)

        anchor_type -- 'page', 'frame', 'paragraph', 'char' or 'as-char'

        page_number -- int (when anchor_type == 'page')

        position -- (str, str)

        style -- unicode

        text_style -- unicode

    Return: odf_element
    """
    frame = odf_create_frame(size=size, anchor_type=anchor_type,
            page_number=page_number, position=position, style=style)
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

    def get_frame_name(self):
        return self.get_attribute('draw:name')


    def set_frame_name(self, name):
        self.set_attribute('draw:name', name)


    def get_frame_size(self):
        """Get the size of the frame.

        Size is a (width, height) tuple with items including the unit,
        e.g. ('10cm', '15cm').


        Return: (str, str)
        """
        get_attr = self.get_attribute
        return get_attr('svg:width'), get_attr('svg:height')


    def set_frame_size(self, size):
        """Set the size of the frame.

        Size is a (width, height) tuple with items including the unit,
        e.g. ('10cm', '15cm'). The dimensions can be None.

        Arguments:

            size -- (str, str)
        """
        self.set_attribute('svg:width', size[0])
        self.set_attribute('svg:height', size[1])


    def get_frame_position(self):
        """Get the position of the frame relative to its anchor
        point.

        Position is a (left, top) tuple with items including the unit,
        e.g. ('10cm', '15cm').

        Return: (str, str)
        """
        get_attr = self.get_attribute
        return get_attr('svg:x'), get_attr('svg:y')


    def set_frame_position(self, position):
        """Set the position of the frame relative to its anchor
        point.

        Position is a (left, top) tuple with items including the unit,
        e.g. ('10cm', '15cm').

        Arguments:

            position -- (str, str)
        """
        self.set_attribute('svg:x', position[0])
        self.set_attribute('svg:y', position[1])


    def get_frame_anchor_type(self):
        """Get how the frame is attached to its environment.

        Return: 'page', 'frame', 'paragraph', 'char' or 'as-char'
        """
        return self.get_attribute('text:anchor-type')


    def set_frame_anchor_type(self, anchor_type, page_number=None):
        """Set how the frame is attached to its environment.

        When the type is 'page', you can give the number of the page where to
        attach.

        Arguments:

            anchor_type -- 'page', 'frame', 'paragraph', 'char' or 'as-char'

            page_number -- int (when anchor_type == 'page')
        """
        self.set_attribute('text:anchor-type', anchor_type)
        if anchor_type == 'page' and page_number:
            self.set_frame_page_number(page_number)


    def get_frame_page_number(self):
        """Get the number of the page where the frame is attached when the
        anchor type is 'page'.

        Return: int
        """
        page_number = self.get_attribute('text:anchor-page-number')
        if page_number is None:
            return None
        return int(page_number)


    def set_frame_page_number(self, page_number):
        """Set the number of the page where the frame is attached when the
        anchor type is 'page', or None to delete it

        Arguments:

            page_number -- int or None
        """
        if page_number is None:
            self.set_attribute('text:anchor-page-number', None)
        self.set_attribute('text:anchor-page-number', str(page_number))


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
