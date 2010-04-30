# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
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


# TODO Read from a shipped file
COLORMAP = {
    'black': (0, 0, 0),
    'blue': (0, 0, 255),
    'brown': (165, 42, 42),
    'cyan': (0, 255, 255),
    'green': (0, 255, 0),
    'grey': (190, 190, 190),
    'magenta': (255, 0, 255),
    'orange': (255, 165, 0),
    'pink': (255, 192, 203),
    'red': (255, 0, 0),
    'violet': (238, 130, 238),
    'white': (255, 255, 255),
    'yellow': (255, 255, 0)
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
            code = COLORMAP[color]
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


    def get_style_list(self, family=None, automatic=False):
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
            result.extend(context.get_style_list(family=family))
        return result


    def get_style(self, family, name_or_element=None, display_name=False):
        """Return the style uniquely identified by the name/family pair. If
        the argument is already a style object, it will return it.

        If the name is None, the default style is fetched.

        If the name is not the internal name but the name you gave in the
        desktop application, set display_name to True.

        Arguments:

            name_or_element -- unicode, odf_style or None

            family -- 'paragraph', 'text',  'graphic', 'table', 'list',
                      'number', 'page-layout', 'master-page'

            display_name -- bool

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
