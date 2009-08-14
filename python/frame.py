# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from image import odf_create_image
from xmlpart import odf_create_element, odf_element, register_element_class


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
                          position=None, style=None):
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

    Return: odf_element
    """
    frame = odf_create_frame(size=size, position=position, style=style)
    text_box = odf_create_element('<draw:text-box/>')
    if type(text_or_element) is unicode:
        text_box.set_text_content(text_or_element)
    else:
        text_box.append_element(text_or_element)
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



register_element_class('draw:frame', odf_frame)
