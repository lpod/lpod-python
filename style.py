# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2012 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Hervé Cauwelier <herve@itaapy.com>
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
from datatype import Boolean
from element import register_element_class, odf_create_element, odf_element
from image import odf_image
from utils import _get_style_tagname, _expand_properties, _merge_dicts
from utils import _get_element, obsolete, isiterable


# from CSS3 color map
COLORMAP = {
    'indigo': (75, 0, 130),
    'gold': (255, 215, 0),
    'firebrick': (178, 34, 34),
    'indianred': (205, 92, 92),
    'yellow': (255, 255, 0),
    'darkolivegreen': (85, 107, 47),
    'darkseagreen': (143, 188, 143),
    'slategrey': (112, 128, 144),
    'darkslategrey': (47, 79, 79),
    'mediumvioletred': (199, 21, 133),
    'mediumorchid': (186, 85, 211),
    'chartreuse': (127, 255, 0),
    'mediumslateblue': (123, 104, 238),
    'black': (0, 0, 0),
    'springgreen': (0, 255, 127),
    'crimson': (220, 20, 60),
    'lightsalmon': (255, 160, 122),
    'brown': (165, 42, 42),
    'turquoise': (64, 224, 208),
    'olivedrab': (107, 142, 35),
    'lightcyan': (224, 255, 255),
    'cyan': (0, 255, 255),
    'silver': (192, 192, 192),
    'skyblue': (135, 206, 235),
    'gray': (128, 128, 128),
    'darkturquoise': (0, 206, 209),
    'goldenrod': (218, 165, 32),
    'darkgreen': (0, 100, 0),
    'darkviolet': (148, 0, 211),
    'darkgray': (169, 169, 169),
    'lightpink': (255, 182, 193),
    'teal': (0, 128, 128),
    'darkmagenta': (139, 0, 139),
    'lightgoldenrodyellow': (250, 250, 210),
    'lavender': (230, 230, 250),
    'yellowgreen': (154, 205, 50),
    'thistle': (216, 191, 216),
    'violet': (238, 130, 238),
    'navy': (0, 0, 128),
    'dimgrey': (105, 105, 105),
    'orchid': (218, 112, 214),
    'blue': (0, 0, 255),
    'ghostwhite': (248, 248, 255),
    'honeydew': (240, 255, 240),
    'cornflowerblue': (100, 149, 237),
    'darkblue': (0, 0, 139),
    'darkkhaki': (189, 183, 107),
    'mediumpurple': (147, 112, 216),
    'cornsilk': (255, 248, 220),
    'red': (255, 0, 0),
    'bisque': (255, 228, 196),
    'slategray': (112, 128, 144),
    'darkcyan': (0, 139, 139),
    'khaki': (240, 230, 140),
    'wheat': (245, 222, 179),
    'deepskyblue': (0, 191, 255),
    'darkred': (139, 0, 0),
    'steelblue': (70, 130, 180),
    'aliceblue': (240, 248, 255),
    'lightslategrey': (119, 136, 153),
    'gainsboro': (220, 220, 220),
    'mediumturquoise': (72, 209, 204),
    'floralwhite': (255, 250, 240),
    'plum': (221, 160, 221),
    'purple': (128, 0, 128),
    'lightgrey': (211, 211, 211),
    'burlywood': (222, 184, 135),
    'darksalmon': (233, 150, 122),
    'beige': (245, 245, 220),
    'azure': (240, 255, 255),
    'lightsteelblue': (176, 196, 222),
    'oldlace': (253, 245, 230),
    'greenyellow': (173, 255, 47),
    'royalblue': (65, 105, 225),
    'lightseagreen': (32, 178, 170),
    'sienna': (160, 82, 45),
    'lightcoral': (240, 128, 128),
    'orangered': (255, 69, 0),
    'navajowhite': (255, 222, 173),
    'lime': (0, 255, 0),
    'palegreen': (152, 251, 152),
    'mistyrose': (255, 228, 225),
    'seashell': (255, 245, 238),
    'mediumspringgreen': (0, 250, 154),
    'fuchsia': (255, 0, 255),
    'papayawhip': (255, 239, 213),
    'blanchedalmond': (255, 235, 205),
    'peru': (205, 133, 63),
    'aquamarine': (127, 255, 212),
    'white': (255, 255, 255),
    'darkslategray': (47, 79, 79),
    'lightgray': (211, 211, 211),
    'ivory': (255, 255, 240),
    'dodgerblue': (30, 144, 255),
    'lawngreen': (124, 252, 0),
    'chocolate': (210, 105, 30),
    'orange': (255, 165, 0),
    'forestgreen': (34, 139, 34),
    'darkgrey': (169, 169, 169),
    'olive': (128, 128, 0),
    'mintcream': (245, 255, 250),
    'antiquewhite': (250, 235, 215),
    'darkorange': (255, 140, 0),
    'cadetblue': (95, 158, 160),
    'moccasin': (255, 228, 181),
    'limegreen': (50, 205, 50),
    'saddlebrown': (139, 69, 19),
    'grey': (128, 128, 128),
    'darkslateblue': (72, 61, 139),
    'lightskyblue': (135, 206, 250),
    'deeppink': (255, 20, 147),
    'coral': (255, 127, 80),
    'aqua': (0, 255, 255),
    'darkgoldenrod': (184, 134, 11),
    'maroon': (128, 0, 0),
    'sandybrown': (244, 164, 96),
    'tan': (210, 180, 140),
    'magenta': (255, 0, 255),
    'rosybrown': (188, 143, 143),
    'pink': (255, 192, 203),
    'lightblue': (173, 216, 230),
    'palevioletred': (216, 112, 147),
    'mediumseagreen': (60, 179, 113),
    'slateblue': (106, 90, 205),
    'dimgray': (105, 105, 105),
    'powderblue': (176, 224, 230),
    'seagreen': (46, 139, 87),
    'snow': (255, 250, 250),
    'mediumblue': (0, 0, 205),
    'midnightblue': (25, 25, 112),
    'paleturquoise': (175, 238, 238),
    'palegoldenrod': (238, 232, 170),
    'whitesmoke': (245, 245, 245),
    'darkorchid': (153, 50, 204),
    'salmon': (250, 128, 114),
    'lightslategray': (119, 136, 153),
    'lemonchiffon': (255, 250, 205),
    'lightgreen': (144, 238, 144),
    'tomato': (255, 99, 71),
    'hotpink': (255, 105, 180),
    'lightyellow': (255, 255, 224),
    'lavenderblush': (255, 240, 245),
    'linen': (250, 240, 230),
    'mediumaquamarine': (102, 205, 170),
    'green': (0, 128, 0),
    'blueviolet': (138, 43, 226),
    'peachpuff': (255, 218, 185)
}



def hex2rgb(color):
    """Turns a "#RRGGBB" hexadecimal color representation into a (R, G, B)
    tuple.
    Arguments:

        color: str

    Return: tuple
    """
    code = color[1:]
    if not (len(color) == 7 and color[0] == '#' and code.isalnum()):
        raise ValueError, '"%s" is not a valid color' % color
    red = int(code[:2], 16)
    green = int(code[2:4], 16)
    blue = int(code[4:6], 16)
    return (red, green, blue)



def rgb2hex(color):
    """Turns a color name or a (R, G, B) color tuple into a "#RRGGBB"
    hexadecimal representation.
    Arguments:

        color -- str or tuple

    Return: str

    Examples::

        >>> rgb2hex('yellow')
        '#FFFF00'
        >>> rgb2hex((238, 130, 238))
        '#EE82EE'
    """
    if type(color) is str:
        try:
            code = COLORMAP[color.lower()]
        except KeyError:
            raise KeyError, 'color "%s" is unknown' % color
    elif type(color) is tuple:
        if len(color) != 3:
            raise ValueError, "color must be a 3-tuple"
        code = color
    else:
        raise TypeError, "invalid color"
    for channel in code:
        if channel < 0 or channel > 255:
            raise ValueError, "color code must be between 0 and 255"
    return '#%02X%02X%02X' % code



def __make_color_string(color=None):
    color_default = "#000000"
    if color is None:
        color_string = color_default
    elif isinstance(color, (str, unicode)):
        if isinstance(color, unicode):
            color = color.encode("utf-8")
        color = color.strip()
        if not color:
            color = color_default
        elif color.startswith("#"):
            color_string = color
        else:
            color_string = rgb2hex(color)
    elif isinstance(color, tuple):
        color_string = rgb2hex(color)
    else:
        raise ValueError, "Color must be None for default or color string, or RGB tuple"
    return color_string



def make_table_cell_border_string(thick=None, line=None, color=None):
    """Returns a string for style:table-cell-properties fo:border,
    with default : "0.06pt solid #000000"

        thick -- str or float
        line -- str
        color -- str or rgb 3-tuple, str is 'black', 'grey', ... or '#012345'

    Returns : str
    """
    thick_default = "0.06pt"
    line_default = "solid"
    if thick is None:
        thick_string = thick_default
    elif isinstance(thick, (str, unicode)):
        if isinstance(thick, unicode):
            thick = thick.encode("utf-8")
        thick = thick.strip()
        if thick:
            thick_string = thick
        else:
            thick_string = thick_default
    elif isinstance(thick, float):
        thick_string = "%.2fpt" % thick
    elif isinstance(thick, int):
        thick_string = "%.2fpt" % (thick / 100.0)
    else:
        raise ValueError, "Thickness must be None for default or float value (pt)"
    if line is None:
        line_string = line_default
    elif isinstance(line, (str, unicode)):
        if isinstance(line, unicode):
            line = line.encode("utf-8")
        line = line.strip()
        if line:
            line_string = line
        else:
            line_string = line_default
    else:
        raise ValueError, "Line style must be None for default or string"
    color_string = __make_color_string(color)
    border = " ".join((thick_string, line_string, color_string))
    return border



def odf_create_table_cell_style(border=None, border_top=None,
                                border_bottom=None,
                                border_left=None, border_right=None,
                                background_color=None, shadow=None,
                                color=None):
                                #parent='Standard'):
    if border is not None:
        border_bottom = border_top = border_left = border_right = None
    if (border is None and border_bottom is None and border_top is None
        and border_left is None and border_right is None):
        border = make_table_cell_border_string()    # default border
    if color:
        color_string = __make_color_string(color)
    if background_color:
        bgcolor_string = __make_color_string(background_color)
    else:
        bgcolor_string = None
    cell_style = odf_create_style('table-cell', area='table-cell',
                                  border=border, border_top=border_top,
                                  border_bottom=border_bottom,
                                  border_left=border_left,
                                  border_right=border_right,
                                  background_color=bgcolor_string,
                                  shadow=shadow)
    if color:
        cell_style.set_properties(area='text', color=color_string)
    return cell_style



def odf_create_style(family, name=None, display_name=None, parent=None,
        # Where properties apply
        area=None,
        # For family 'text':
        color=None, background_color=None, italic=False, bold=False,
        # For family 'paragraph'
        master_page=None,
        # For family 'master-page'
        page_layout=None, next_style=None,
        # For family 'table-cell'
        data_style=None, border=None, border_top=None, border_right=None,
        border_bottom=None, border_left=None, shadow=None,
        # For family 'table-row'
        height=None, use_optimal_height=None,
        # For family 'table-column'
        width=None, break_before=None, break_after=None,
        # For family 'graphic'
        min_height=None,
        # For family 'font-face'
        font_name=None, font_family=None, font_family_generic=None,
        font_pitch=u"variable",
        # Every other property
        **kw):
    """Create a style of the given family. The name is not mandatory at this
    point but will become required when inserting in a document as a common
    style.

    The display name is the name the user sees in an office application.

    The parent is the name of the style this style will inherit from.

    To set properties, pass them as keyword arguments. The area properties
    apply to is optional and defaults to the family.

    Arguments:

        family -- 'paragraph', 'text', 'section', 'table', 'table-column',
                  'table-row', 'table-cell', 'table-page', 'chart',
                  'drawing-page', 'graphic', 'presentation',
                  'control', 'ruby', 'list', 'number', 'page-layout'
                  'font-face', or 'master-page'

        name -- unicode

        display_name -- unicode

        parent -- unicode

        area -- str

    'text' Properties:

        italic -- bool

        bold -- bool

    'paragraph' Properties:

        master_page -- unicode

    'master-page' Properties:

        page_layout -- unicode

        next_style -- unicode

    'table-cell' Properties:

        border, border_top, border_right, border_bottom, border_left -- str,
        e.g. "0.002cm solid #000000" or 'none'

        shadow -- str, e.g. "#808080 0.176cm 0.176cm"

    'table-row' Properties:

        height -- str, e.g. '5cm'

        use_optimal_height -- bool

    'table-column' Properties:

        width -- str, e.g. '5cm'

        break_before -- 'page', 'column' or 'auto'

        break_after -- 'page', 'column' or 'auto'

    Return: odf_style
    """
    tagname, famattr = _get_style_tagname(family)
    element = odf_create_element(tagname)
    # Common attributes
    if name:
        element.set_name(name)
    if famattr:
        element.set_family(famattr)
    if display_name:
        element.set_display_name(display_name)
    if parent:
        element.set_parent_style(parent)
    # Paragraph
    if family == 'paragraph':
        if master_page:
            element.set_master_page(master_page)
    # Master Page
    elif family == 'master-page':
        if page_layout:
            element.set_page_layout(page_layout)
        if next_style:
            element.set_next_style(next_style)
    # Font face
    elif family == 'font-face':
        element.set_font(font_name, family=font_family,
                family_generic=font_family_generic, pitch=font_pitch)
    # Properties
    if area is None:
        area = family
    # Text
    if area == 'text':
        if color:
            kw['fo:color'] = color
        if background_color:
            kw['fo:background-color'] = background_color
        if italic:
            kw['fo:font-style'] = 'italic'
            kw['style:font-style-asian'] = 'italic'
            kw['style:font-style-complex'] = 'italic'
        if bold:
            kw['fo:font-weight'] = 'bold'
            kw['style:font-weight-asian'] = 'bold'
            kw['style:font-weight-complex'] = 'bold'
    # Table cell
    elif area == 'table-cell':
        if border:
            kw['fo:border'] = border
        elif border_top or border_right or border_bottom or border_left:
            kw['fo:border-top'] = border_top or 'none'
            kw['fo:border-right'] = border_right or 'none'
            kw['fo:border-bottom'] = border_bottom or 'none'
            kw['fo:border-left'] = border_left or 'none'
        if shadow:
            kw['style:shadow'] = shadow
        if background_color:
            kw['fo:background-color'] = background_color
    # Table row
    elif area == 'table-row':
        if height:
            kw['style:row-height'] = height
        if use_optimal_height is not None:
            kw['style:use-optimal-row-height'] = Boolean.encode(
                    use_optimal_height)
    # Table column
    elif area == 'table-column':
        if width:
            kw['style:column-width']  = width
        if break_before:
            kw['fo:break-before'] = break_before
        if break_after:
            kw['fo:break-after'] = break_after
    # Graphic
    elif area == 'graphic':
        if min_height:
            kw['fo:min-height'] = min_height
    # Every other properties
    if kw:
        element.set_properties(kw, area=area)
    return element



class odf_style(odf_element):
    """Specialised element for styles, yet generic to all style types.
    """
    def get_name(self):
        return self.get_attribute('style:name')

    get_style_name = obsolete('get_style_name', get_name)


    def set_name(self, name):
        self.set_attribute('style:name', name)


    def get_display_name(self):
        return self.get_attribute('style:display-name')


    def set_display_name(self, name):
        return self.set_style_attribute('style:display-name', name)


    def get_family(self):
        family = self.get_attribute('style:family')
        # Where the family is known from the tag, it must be defined
        if family is None:
            raise ValueError, 'family undefined in %s "%s"' % (self,
                    self.get_name())
        return family


    def set_family(self, family):
        return self.set_attribute('style:family', family)


    def get_parent_style(self):
        """Will only return a name, not an object, because we don't have
        access to the XML part from here.

        See odf_styles.get_parent_style
        """
        return self.get_attribute('style:parent-style-name')

    get_parent_style_name = obsolete('get_parent_style_name',
            get_parent_style)


    def set_parent_style(self, name):
        self.set_style_attribute('style:parent-style-name', name)


    def get_properties(self, area=None):
        """Get the mapping of all properties of this style. By default the
        properties of the same family, e.g. a paragraph style and its
        paragraph properties. Specify the area to get the text properties of
        a paragraph style for example.

        Arguments:

            area -- str

        Return: dict
        """
        if area is None:
            area = self.get_family()
        element = self.get_element('style:%s-properties' % area)
        if element is None:
            return None
        properties = element.get_attributes()
        # Nested properties are nested dictionaries
        for child in element.get_children():
            properties[child.get_tag()] = child.get_attributes()
        return properties


    def set_properties(self, properties={}, style=None, area=None, **kw):
        """Set the properties of the "area" type of this style. Properties
        are given either as a dict or as named arguments (or both). The area
        is identical to the style family by default. If the properties
        element is missing, it is created.

        Instead of properties, you can pass a style with properties of the
        same area. These will be copied.

        Arguments:

            properties -- dict

            style -- odf_style

            area -- 'paragraph', 'text'...
        """
        if area is None:
            area = self.get_family()
        element = self.get_element('style:%s-properties' % area)
        if element is None:
            element = odf_create_element('style:%s-properties' % area)
            self.append(element)
        if properties or kw:
            properties = _expand_properties(_merge_dicts(properties, kw))
        elif style is not None:
            properties = style.get_properties(area=area)
            if properties is None:
                return
        for key, value in properties.iteritems():
            if value is None:
                element.del_attribute(key)
            else:
                element.set_attribute(key, value)

    set_style_properties = obsolete('set_style_properties', set_properties)


    def del_properties(self, properties=[], area=None, *args):
        """Delete the given properties, either by list argument or
        positional argument (or both). Remove only from the given area,
        identical to the style family by default.

        Arguments:

            properties -- list

            area -- str
        """
        if area is None:
            area = self.get_family()
        element = self.get_element('style:%s-properties' % area)
        if element is None:
            raise ValueError, "properties element is inexistent"
        for key in _expand_properties(properties):
            element.del_attribute(key)


    def set_background(self, color=None, url=None, position='center',
                       repeat=None, opacity=None, filter=None):
        """Set the background color of a text style, or the background color
        or image of a paragraph style or page layout.

        With no argument, remove any existing background.

        The position is one or two of 'center', 'left', 'right', 'top' or
        'bottom'.

        The repeat is 'no-repeat', 'repeat' or 'stretch'.

        The opacity is a percentage integer (not a string with the '%s' sign)

        The filter is an application-specific filter name defined elsewhere.

        Though this method is defined on the base style class, it will raise
        an error if the style type is not compatible.

        Arguments:

            color -- '#rrggbb'

            url -- str

            position -- str

            repeat -- str

            opacity -- int

            filter -- str
        """
        family = self.get_family()
        if family not in ('text', 'paragraph', 'page-layout', 'section',
                          'table', 'table-row', 'table-cell', 'graphic'):
            raise TypeError, 'no background support for this family'
        if url is not None and family == 'text':
            raise TypeError, 'no background image for text styles'
        properties = self.get_element('style:%s-properties' % family)
        if properties is None:
            bg_image = None
        else:
            bg_image = properties.get_element('style:background-image')
        # Erasing
        if color is None and url is None:
            if properties is None:
                return
            properties.del_attribute('fo:background-color')
            if bg_image is not None:
                properties.delete(bg_image)
            return
        # Add the properties if necessary
        if properties is None:
            properties = odf_create_element('style:%s-properties' % family)
            self.append(properties)
        # Add the color...
        if color:
            properties.set_attribute('fo:background-color', color)
            if bg_image is not None:
                properties.delete(bg_image)
        # ... or the background
        elif url:
            properties.set_attribute('fo:background-color', 'transparent')
            if bg_image is None:
                bg_image = odf_create_element('style:background-image')
                properties.append(bg_image)
            bg_image.set_url(url)
            if position:
                bg_image.set_position(position)
            if repeat:
                bg_image.set_repeat(repeat)
            if opacity:
                bg_image.set_opacity(opacity)
            if filter:
                bg_image.set_filter(filter)


    def get_master_page(self):
        return self.get_attributes('style:master-page-name')


    def set_master_page(self, name):
        return self.set_style_attribute('style:master-page-name', name)



class odf_list_style(odf_style):
    """A list style is a container for list level styles.
    """
    any_style = ('(text:list-level-style-number'
                 '|text:list-level-style-bullet'
                 '|text:list-level-style-image)')


    def get_family(self):
        return 'list'


    def get_level_style(self, level):
        return _get_element(self, self.any_style, 0, level=level)


    def set_level_style(self, level, num_format=None, bullet_char=None,
            url=None, display_levels=None, prefix=None, suffix=None,
            start_value=None, style=None, clone=None):
        """
        Arguments:

            level -- int

            num_format (for number) -- int

            bullet_char (for bullet) -- unicode

            url (for image) -- str

            display_levels -- int

            prefix -- unicode

            suffix -- unicode

            start_value -- int

            style -- unicode

            clone -- odf_list_style

        Return:
            level_style created
        """
        # Expected name
        if num_format is not None:
            level_style_name = 'text:list-level-style-number'
        elif bullet_char is not None:
            level_style_name = 'text:list-level-style-bullet'
        elif url is not None:
            level_style_name = 'text:list-level-style-image'
        elif clone is not None:
            level_style_name = clone.get_tag()
        else:
            raise ValueError, "unknown level style type"
        was_created = False
        # Cloning or reusing an existing element
        if clone is not None:
            level_style = clone.clone()
            was_created = True
        else:
            level_style = self.get_level_style(level)
            if level_style is None:
                level_style = odf_create_element(level_style_name)
                was_created = True
        # Transmute if the type changed
        if level_style.get_tag() != level_style_name:
            level_style.set_tag(level_style_name)
        # Set the level
        level_style.set_attribute('text:level', str(level))
        # Set the main attribute
        if num_format is not None:
            level_style.set_attribute('fo:num-format', num_format)
        elif bullet_char is not None:
            level_style.set_attribute('text:bullet-char', bullet_char)
        elif url is not None:
            level_style.set_attribute('xlink:href', url)
        # Set attributes
        if prefix:
            level_style.set_attribute('style:num-prefix', prefix)
        if suffix:
            level_style.set_attribute('style:num-suffix', suffix)
        if display_levels:
            level_style.set_attribute('text:display-levels',
                    str(display_levels))
        if start_value:
            level_style.set_attribute('text:start-value', str(start_value))
        if style:
            level_style.set_text_style(style)
        # Commit the creation
        if was_created:
            self.append(level_style)
        return level_style



class odf_outline_style(odf_list_style):

    # FIXME stubs
    def get_family(self):
        return 'outline'



class odf_page_layout(odf_style):
    """Physical presentation of a page.

    XXX to verify
    """
    def get_family(self):
        return 'page-layout'


    def set_family(self):
        raise ValueError, 'family is read-only'


    def get_header_style(self):
        return self.get_element('style:header-style')


    def set_header_style(self, new_style):
        header_style = self.get_header_style()
        if header_style is not None:
            self.delete(header_style)
        self.append(new_style)


    def get_footer_style(self):
        return self.get_element('style:footer-style')


    def set_footer_style(self, new_style):
        footer_style = self.get_footer_style()
        if footer_style is not None:
            self.delete(footer_style)
        self.append(new_style)



class odf_master_page(odf_style):
    """A master page is the style of a page.

    Physical presentation is in the associated page layout.

    XXX to verify
    """
    def __set_header_or_footer(self, text_or_element, name='header',
                               style=u"Header"):
        if name == 'header':
            header_or_footer = self.get_header()
        else:
            header_or_footer = self.get_footer()
        if header_or_footer is None:
            header_or_footer = odf_create_element('style:' + name)
            self.append(header_or_footer)
        else:
            header_or_footer.clear()
        if not isiterable(text_or_element):
            # Already a header or footer?
            if (isinstance(text_or_element, odf_element)
                    and text_or_element.get_tag() == 'style:%s' % name):
                self.delete(header_or_footer)
                self.append(text_or_element)
                return
            text_or_element = [text_or_element]
        # FIXME cyclic import
        from paragraph import odf_create_paragraph
        for item in text_or_element:
            if type(item) is unicode:
                paragraph = odf_create_paragraph(item, style=style)
                header_or_footer.append(paragraph)
            elif isinstance(item, odf_element):
                header_or_footer.append(item)


    #
    # Public API
    #

    def get_family(self):
        return 'master-page'


    def set_family(self):
        raise ValueError, 'family is read-only'


    def get_page_layout(self):
        return self.get_attribute('style:page-layout-name')


    def set_page_layout(self, name):
        self.set_style_attribute('style:page-layout-name', name)


    def get_next_style(self):
        return self.get_attribute('style:next-style-name')


    def set_next_style(self, name):
        self.set_style_attribute('style:next-style-name', name)


    def get_header(self):
        """Get the element that contains the header contents.

        If None, no header was set.
        """
        return self.get_element('style:header')


    def set_header(self, text_or_element):
        """Create or replace the header by the given content. It can already
        be a complete header.

        If you only want to update the existing header, get it and use the
        API.

        Arguments:

            text_or_element -- unicode or odf_element or a list of them
        """
        return self.__set_header_or_footer(text_or_element)


    def get_footer(self):
        """Get the element that contains the footer contents.

        If None, no footer was set.
        """
        return self.get_element('style:footer')


    def set_footer(self, text_or_element):
        """Create or replace the footer by the given content. It can already
        be a complete footer.

        If you only want to update the existing footer, get it and use the
        API.

        Arguments:

            text_or_element -- unicode or odf_element or a list of them
        """
        return self.__set_header_or_footer(text_or_element, name='footer',
                                           style=u"Footer")


class odf_font_style(odf_style):

    def get_family(self):
        return 'font-face'


    def set_font(self, name, family=None, family_generic=None,
            pitch=u"variable"):
        self.set_attribute('style:name', name)
        if family is None:
            family = name
        self.set_attribute('svg:font-family', "'{0}'".format(family))
        if family_generic is not None:
            self.set_attribute('style:font-family-generic', family_generic)
        self.set_attribute('style:font-pitch', pitch)



class odf_number_style(odf_style):

    def get_family(self):
        return 'number'



class odf_percentage_style(odf_style):

    def get_family(self):
        return 'percentage'



class odf_time_style(odf_style):

    def get_family(self):
        return 'time'



class odf_date_style(odf_style):

    def get_family(self):
        return 'date'



class odf_currency_style(odf_style):

    def get_family(self):
        return 'currency'



class odf_presentation_page_layout(odf_style):

    def get_family(self):
        return 'presentation-page-layout'



class odf_list_level_style_number(odf_style):

    def get_text_style(self):
        return self.get_attribute('text:style-name')


    def set_text_style(self, style):
        self.set_style_attribute('text:style-name', style)



class odf_marker(odf_style):

    def get_family(self):
        return 'marker'



class odf_background_image(odf_image):

    def get_position(self):
        return self.get_attribute('style:position')


    def set_position(self, position):
        return self.set_attribute('style:position', position)


    def get_repeat(self):
        return self.get_attribute('style:repeat')


    def set_repeat(self, repeat):
        return self.set_attribute('style:repeat', repeat)


    def get_opacity(self):
        return self.get_attribute('draw:opacity')


    def set_opacity(self, opacity):
        return self.set_attribute('draw:opacity', str(opacity))


    def get_filter(self):
        return self.get_attribute('style:filter-name')


    def set_filter(self, filter):
        return self.set_style_attribute('style:filter-name', filter)



class odf_fill_image(odf_style, odf_image):

    def get_family(self):
        return 'fill-image'



# Some predefined styles
def odf_create_default_number_style():
    return odf_create_element(
            """<number:number-style style:name="lpod-default-number-style">
                  <number:number number:decimal-places="2"
                                 number:min-integer-digits="1"/>
               </number:number-style>""")



def odf_create_default_percentage_style():
    return odf_create_element(
            """<number:percentage-style
                  style:name="lpod-default-percentage-style">
                  <number:number number:decimal-places="2"
                                 number:min-integer-digits="1"/>
                  <number:text>%</number:text>
               </number:percentage-style>""")



def odf_create_default_time_style():
    return odf_create_element(
            """<number:time-style style:name="lpod-default-time-style">
                  <number:hours number:style="long"/>
                  <number:text>:</number:text>
                  <number:minutes number:style="long"/>
                  <number:text>:</number:text>
                  <number:seconds number:style="long"/>
               </number:time-style>""")



def odf_create_default_date_style():
    return odf_create_element(
            """<number:date-style style:name="lpod-default-date-style">
                  <number:year number:style="long"/>
                  <number:text>-</number:text>
                  <number:month number:style="long"/>
                  <number:text>-</number:text>
                  <number:day number:style="long"/>
               </number:date-style>""")



def odf_create_default_boolean_style():
    return odf_create_element(
            """<number:boolean-style style:name="lpod-default-boolean-style">
                  <number:boolean/>
               </number:boolean-style>""")



def odf_create_default_currency_style():
    return odf_create_element(
            """<number:currency-style style:name="lpod-default-currency-style">
                  <number:text>-</number:text>
                  <number:number number:decimal-places="2"
                                 number:min-integer-digits="1"
                                 number:grouping="true"/>
                  <number:text> </number:text>
                  <number:currency-symbol
                      number:language="fr"
                      number:country="FR">€</number:currency-symbol>
               </number:currency-style>""")



registered_styles = []

def register_style(tagname, cls):
    register_element_class(tagname, cls)
    registered_styles.append(tagname)



# FIXME there are (many) more
for name in ('style:style', 'style:default-style', 'style:header-style',
        'style:footer-style', 'text:list-level-style-bullet',
        'text:list-level-style-image'):
    register_style(name, odf_style)
register_style('text:list-style', odf_list_style)
register_style('text:outline-style', odf_outline_style)
register_style('style:page-layout', odf_page_layout)
register_style('style:master-page', odf_master_page)
register_style('style:font-face', odf_font_style)
register_style('number:number-style', odf_number_style)
register_style('number:percentage-style', odf_percentage_style)
register_style('number:time-style', odf_time_style)
register_style('number:date-style', odf_date_style)
register_style('number:currency-style', odf_currency_style)
register_style('style:presentation-page-layout',
        odf_presentation_page_layout)
register_style('text:list-level-style-number', odf_list_level_style_number)
register_style('draw:marker', odf_marker)
register_style('style:background-image', odf_background_image)
register_style('draw:fill-image', odf_fill_image)
