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
from style import odf_style
from utils import _make_xpath_query, _get_style_tagname
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


def hex2rgb(color):
    """Turns a "#RRGGBB" hexadecimal color representation into a (R, G, B)
    tuple.
    Arguments:

        color: str

    Returns: tuple
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

    Returns: str

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

    def _get_style_context(self, name, family, automatic=False):
        if name is None:
            return self.get_element('//office:styles')
        elif name is False:
            # Treat the case for get_style_list where the name is undefined
            if automatic:
                return self.get_element('//office:automatic-styles')
            # The most including element
            return self.get_root()
        if automatic:
            return self.get_element('//office:automatic-styles')
        mapping = {'paragraph': '//office:styles',
                   'text': '//office:styles',
                   'graphic': '//office:styles',
                   'page-layout': '//office:automatic-styles',
                   'master-page': '//office:master-styles',
                   'font-face': '//office:font-face-decls',
                   'outline': '//office:styles',
                   'date': '//office:automatic-styles'}
        if family not in mapping:
            raise ValueError, "unknown family: " + family
        return self.get_element(mapping[family])


    def _get_style_tagname(self, family, name):
        if name is None:
            return ('style:default-style', family)
        # Treat the case for get_style_list where the name is undefined
        elif name is False:
            if family is None:
                return ('(//style:default-style|//*[@style:name])', None)
            tagname, famattr = _get_style_tagname(family)
            tagname = '//' + tagname
            if famattr:
                # Candidate for a default style
                tagname = '(%s|//style:default-style)' % tagname
            return (tagname, famattr)
        return _get_style_tagname(family)


    def get_style_list(self, family=None, automatic=False):
        tagname, famattr = self._get_style_tagname(family, False)
        query = _make_xpath_query(tagname, family=famattr)
        context = self._get_style_context(False, family, automatic)
        return context.get_element_list(query)


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
        if type(name_or_element) is unicode or name_or_element is None:
            if display_name is True:
                style_name = None
                display_name = name_or_element
            else:
                style_name = name_or_element
                display_name = None
            tagname, famattr = self._get_style_tagname(family,
                                                       name_or_element)
            # famattr became None if no "style:family" attribute
            query = _make_xpath_query(tagname, style_name=style_name,
                                      display_name=display_name,
                                      family=famattr)
            context = self._get_style_context(name_or_element, family)
            return context.get_element(query)
        elif isinstance(name_or_element, odf_style):
            return name_or_element
        raise TypeError, "style name or element expected"
