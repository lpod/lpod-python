# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
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
from element import odf_create_element, odf_element, register_element_class
from image import odf_create_image
from paragraph import odf_create_paragraph
from style import odf_create_style
from utils import obsolete, isiterable


def odf_create_frame(name=None, draw_id=None, style=None, position=None,
        size=('1cm', '1cm'), z_index=0, presentation_class=None,
        anchor_type=None, page_number=None, layer=None,
        presentation_style=None):
    """Create a frame element of the given size. Position is relative to the
    context the frame is inserted in. If positioned by page, give the page
    number and the x, y position.

    Size is a (width, height) tuple and position is a (left, top) tuple; items
    are strings including the unit, e.g. ('10cm', '15cm').

    Frames are not useful by themselves. You should consider calling
    odf_create_image_frame or odf_create_text_frame directly.

    Arguments:

        name -- unicode

        draw_id -- unicode

        style -- unicode

        position -- (str, str)

        size -- (str, str)

        z_index -- int (default 0)

        presentation_class -- unicode

        anchor_type -- 'page', 'frame', 'paragraph', 'char' or 'as-char'

        page_number (anchor_type='page') -- int

        layer -- unicode

        presentation_style -- unicode

    Return: odf_frame
    """
    frame = odf_create_element('draw:frame')
    frame.set_size(size)
    frame.set_z_index(z_index)
    if name:
        frame.set_name(name)
    if page_number:
        frame.set_anchor_type('page', page_number=page_number)
    if anchor_type:
        frame.set_anchor_type(anchor_type)
    if position is not None:
        frame.set_position(position)
    if layer is not None:
        frame.set_layer(layer)
    if presentation_class is not None:
        frame.set_presentation_class(presentation_class)
    if style is not None:
        frame.set_style(style)
    if presentation_style is not None:
        frame.set_presentation_style(presentation_style)
    return frame



def odf_create_image_frame(url, text=None, name=None, draw_id=None,
        style=None, position=None, size=('1cm', '1cm'), z_index=0,
        presentation_class=None, anchor_type=None, page_number=None,
        layer=None, presentation_style=None):
    """Create a ready-to-use image, since it must be embedded in a
    frame.

    The optionnal text will appear above the image.

    Size is a (width, height) tuple and position is a (left, top) tuple;
    items are strings including the unit, e.g. ('21cm', '29.7cm').

    Arguments:

        url -- str

        text -- unicode

        name -- unicode

        draw_id -- unicode

        style -- unicode

        position -- (str, str)

        size -- (str, str)

        z_index -- int (default 0)

        presentation_class -- unicode

        anchor_type -- 'page', 'frame', 'paragraph', 'char' or 'as-char'

        page_number (anchor_type='page') -- int

        layer -- unicode

        presentation_style -- unicode

    Return: odf_frame
    """
    frame = odf_create_frame(name=name, draw_id=draw_id, style=style,
            position=position, size=size, z_index=z_index,
            presentation_class=presentation_class, anchor_type=anchor_type,
            page_number=page_number, layer=layer,
            presentation_style=presentation_style)
    image = frame.set_image(url)
    if text:
        image.set_text_content(text)
    return frame



def odf_create_text_frame(text_or_element=None, text_style=None, name=None,
        draw_id=None, style=None, position=None, size=('1cm', '1cm'),
        z_index=0, presentation_class=None, anchor_type=None,
        page_number=None, layer=None, presentation_style=None):
    """Create a ready-to-use text box, since it must be embedded in a frame.

    Size is a (width, height) tuple and position is a (left, top) tuple;
    items are strings including the unit, e.g. ('21cm', '29.7cm').

    Arguments:

        text_or_element -- unicode or odf_element

        text_style -- unicode

        name -- unicode

        draw_id -- unicode

        style -- unicode

        position -- (str, str)

        size -- (str, str)

        z_index -- int (default 0)

        presentation_class -- unicode

        anchor_type -- 'page', 'frame', 'paragraph', 'char' or 'as-char'

        page_number (anchor_type='page') -- int

        layer -- unicode

        presentation_style -- unicode

    Return: odf_frame
    """
    frame = odf_create_frame(name=name, draw_id=draw_id, style=style,
            position=position, size=size, z_index=z_index,
            presentation_class=presentation_class, anchor_type=anchor_type,
            page_number=page_number, layer=layer,
            presentation_style=presentation_style)
    frame.set_text_box(text_or_element=text_or_element,
            text_style=text_style)
    return frame



def odf_create_frame_position_style(name=u"FramePosition",
        horizontal_pos="from-left", vertical_pos="from-top",
        horizontal_rel="paragraph", vertical_rel="paragraph"):
    """Helper style for positioning frames in desktop applications that need
    it.

    Default arguments should be enough.

    Use the return value as the frame style or build a new graphic style with
    this style as the parent.
    """
    return odf_create_style('graphic', u"FramePositioning",
            **{'style:horizontal-pos': "from-left",
                'style:vertical-pos': "from-top",
                'style:horizontal-rel': "paragraph",
                'style:vertical-rel': "paragraph"})



class odf_frame(odf_element):

    def get_name(self):
        return self.get_attribute('draw:name')


    def set_name(self, name):
        return self.set_attribute('draw:name', name)


    def get_id(self):
        return self.get_attribute('draw:id')


    def set_id(self, frame_id):
        return self.set_attribute('draw:id', frame_id)


    def get_style(self):
        return self.get_attribute('draw:style-name')


    def set_style(self, name):
        return self.set_style_attribute('draw:style-name', name)


    def get_position(self):
        """Get the position of the frame relative to its anchor
        point.

        Position is a (left, top) tuple with items including the unit,
        e.g. ('10cm', '15cm').

        Return: (str, str)
        """
        get_attr = self.get_attribute
        return get_attr('svg:x'), get_attr('svg:y')


    def set_position(self, position):
        """Set the position of the frame relative to its anchor
        point.

        Position is a (left, top) tuple with items including the unit,
        e.g. ('10cm', '15cm').

        Arguments:

            position -- (str, str)
        """
        self.set_attribute('svg:x', str(position[0]))
        self.set_attribute('svg:y', str(position[1]))


    def get_size(self):
        """Get the size of the frame.

        Size is a (width, height) tuple with items including the unit,
        e.g. ('10cm', '15cm').


        Return: (str, str)
        """
        get_attr = self.get_attribute
        return get_attr('svg:width'), get_attr('svg:height')


    def set_size(self, size):
        """Set the size of the frame.

        Size is a (width, height) tuple with items including the unit,
        e.g. ('10cm', '15cm'). The dimensions can be None.

        Arguments:

            size -- (str, str)
        """
        self.set_attribute('svg:width', str(size[0]))
        self.set_attribute('svg:height', str(size[1]))


    def get_z_index(self):
        z_index = self.get_attribute('draw:z-index')
        if z_index is None:
            return None
        return int(z_index)


    def set_z_index(self, z_index):
        if z_index is None:
            self.set_attribute('draw:z-index', z_index)
        return self.set_attribute('draw:z-index', str(z_index))


    def get_anchor_type(self):
        """Get how the frame is attached to its environment.

        Return: 'page', 'frame', 'paragraph', 'char' or 'as-char'
        """
        return self.get_attribute('text:anchor-type')


    def set_anchor_type(self, anchor_type, page_number=None):
        """Set how the frame is attached to its environment.

        When the type is 'page', you can give the number of the page where to
        attach.

        Arguments:

            anchor_type -- 'page', 'frame', 'paragraph', 'char' or 'as-char'

            page_number -- int (when anchor_type == 'page')
        """
        self.set_attribute('text:anchor-type', anchor_type)
        if anchor_type == 'page' and page_number:
            self.set_page_number(page_number)

    set_frame_anchor_type = obsolete('set_frame_anchor_type', set_anchor_type)


    def get_page_number(self):
        """Get the number of the page where the frame is attached when the
        anchor type is 'page'.

        Return: int
        """
        page_number = self.get_attribute('text:anchor-page-number')
        if page_number is None:
            return None
        return int(page_number)


    def set_page_number(self, page_number):
        """Set the number of the page where the frame is attached when the
        anchor type is 'page', or None to delete it

        Arguments:

            page_number -- int or None
        """
        if page_number is None:
            self.set_attribute('text:anchor-page-number', None)
        self.set_attribute('text:anchor-page-number', str(page_number))


    def get_layer(self):
        return self.get_attribute('draw:layer')


    def set_layer(self, layer):
        return self.set_attribute('draw:layer', layer)


    def get_text_content(self):
        text_box = self.get_element('draw:text-box')
        if text_box is None:
            return None
        return text_box.get_text_content()


    def set_text_content(self, text_or_element):
        text_box = self.get_element('draw:text-box')
        if text_box is None:
            text_box = odf_create_element('draw:text-box')
            self.append(text_box)
        if isinstance(text_or_element, odf_element):
            text_box.clear()
            return text_box.append(text_or_element)
        return text_box.set_text_content(text_or_element)


    def get_presentation_class(self):
        return self.get_attribute('presentation:class')


    def set_presentation_class(self, presentation_class):
        return self.set_attribute('presentation:class', presentation_class)


    def get_presentation_style(self):
        return self.get_attribute('presentation:style-name')


    def set_presentation_style(self, name):
        return self.set_style_attribute('presentation:style-name', name)


    def get_image(self):
        return self.get_element('draw:image')


    def set_image(self, url_or_element, text=None):
        image = self.get_image()
        if image is None:
            if isinstance(url_or_element, odf_element):
                image = url_or_element
                self.append(image)
            else:
                image = odf_create_image(url_or_element)
                self.append(image)
        else:
            if isinstance(url_or_element, odf_element):
                image.delete()
                image = url_or_element
                self.append(image)
            else:
                image.set_url(url_or_element)
        return image


    def get_text_box(self):
        return self.get_element('draw:text-box')


    def set_text_box(self, text_or_element=None, text_style=None):
        text_box = self.get_text_box()
        if text_box is None:
            text_box = odf_create_element('draw:text-box')
            self.append(text_box)
        else:
            text_box.clear()
        if not isiterable(text_or_element):
            text_or_element = [text_or_element]
        for item in text_or_element:
            if isinstance(item, unicode):
                item = odf_create_paragraph(item, style=text_style)
            text_box.append(item)
        return text_box


    def get_formatted_text(self, context):
        result = []
        for element in self.get_children():
            tag = element.get_tag()
            if tag == 'draw:image':
                if context['rst_mode']:
                    filename = element.get_attribute('xlink:href')
                    if context['no_img_level']:
                        context['img_counter'] += 1
                        ref = u'|img%d|' % context['img_counter']
                        result.append(ref)
                        context['images'].append( (ref, filename) )
                    else:
                        result.append(u'\n.. image:: %s\n' % filename)
                else:
                    result.append(u'[Image %s]\n' %
                                  element.get_attribute('xlink:href'))
            elif tag == 'draw:text-box':
                subresult = [u'  ']
                for element in element.get_children():
                    subresult.append(element.get_formatted_text(context))
                subresult = u''.join(subresult)
                subresult = subresult.replace(u'\n', u'\n  ')
                subresult.rstrip(' ')
                result.append(subresult)
            else:
                result.append(element.get_formatted_text(context))
        result.append(u'\n')
        return u''.join(result)



register_element_class('draw:frame', odf_frame)
