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
from xmlpart import odf_xmlpart
from utils import _get_elements, _get_element, obsolete


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


context_mapping = {
        'paragraph': ('//office:styles', '//office:automatic-styles'),
        'text': ('//office:styles',),
        'graphic': ('//office:styles',),
        'page-layout': ('//office:automatic-styles',),
        'master-page': ('//office:master-styles',),
        'font-face': ('//office:font-face-decls',),
        'outline': ('//office:styles',),
        'date': ('//office:automatic-styles',),
        'list': ('//office:styles',),
        'presentation': ('//office:styles', '//office:automatic-styles'),
        'drawing-page': ('//office:automatic-styles',),
        'presentation-page-layout': ('//office:styles',),
        'marker': ('//office:styles',),
        'fill-image': ('//office:styles',),
        # FIXME Do they?
        'table': ('//office:automatic-styles',),
        'table-cell': ('//office:automatic-styles',),
        'table-row': ('//office:automatic-styles',),
        'table-column': ('//office:automatic-styles',),
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



class odf_styles(odf_xmlpart):

    def _get_style_contexts(self, family, automatic=False):
        if automatic is True:
            return (self.get_element('//office:automatic-styles'),)
        elif family is None:
            # All possibilities
            return (self.get_element('//office:automatic-styles'),
                    self.get_element('//office:styles'),
                    self.get_element('//office:master-styles'),
                    self.get_element('//office:font-face-decls'))
        queries = context_mapping.get(family)
        if queries is None:
            raise ValueError, "unknown family: " + family
        return [self.get_element(query) for query in queries]


    def get_styles(self, family=None, automatic=False):
        """Return the list of styles in the Content part, optionally limited
        to the given family.

        Arguments:

            family -- str

        Return: list of odf_style
        """
        result = []
        for context in self._get_style_contexts(family, automatic=automatic):
            if context is None:
                continue
            result.extend(context.get_styles(family=family))
        return result

    get_style_list = obsolete('get_style_list', get_styles)


    def get_style(self, family, name_or_element=None, display_name=None):
        """Return the style uniquely identified by the name/family pair. If
        the argument is already a style object, it will return it.

        If the name is None, the default style is fetched.

        If the name is not the internal name but the name you gave in the
        desktop application, use display_name instead.

        Arguments:

            name_or_element -- unicode, odf_style or None

            family -- 'paragraph', 'text',  'graphic', 'table', 'list',
                      'number', 'page-layout', 'master-page'

            display_name -- unicode

        Return: odf_style or None if not found
        """
        for context in self._get_style_contexts(family):
            if context is None:
                continue
            style = context.get_style(family,
                    name_or_element=name_or_element,
                    display_name=display_name)
            if style is not None:
                return style
        return None


    def get_master_pages(self):
        return _get_elements(self, 'descendant::style:master-page')


    def get_master_page(self, position=0):
        return _get_element(self, 'descendant::style:master-page', position)
