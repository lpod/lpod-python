# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from lpod.utils import _get_element_list
from lpod.xmlpart import odf_xmlpart


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

    def _get_style_container_name(self, category):
        if category is None:
            return None
        mapping = {'automatic': 'office:automatic-styles',
                   'default': 'office:styles',
                   'master': 'office:master-styles',
                   'named': 'office:styles'}
        if category not in mapping:
            raise ValueError, 'unknown category'
        return mapping[category]


    def _get_style_element_name(self, category):
        if category is None:
            return None
        mapping = {'automatic': '*',
                   'default': 'style:default-style',
                   'master': '*',
                   'named': 'style:style'}
        if category not in mapping:
            raise ValueError, 'unknown category'
        return mapping[category]


    def get_category_context(self, category):
        container_name = self._get_style_container_name(category)
        return self.get_element(container_name)


    def get_style_list(self, style_name=None, family=None, category=None,
                       display_name=None):
        if category is None:
            category = ['automatic', 'default', 'master', 'named']
        styles = []
        for type in category:
            context = self.get_category_context(type)
            child_to_search = self._get_style_element_name(type)
            styles.extend(_get_element_list(context, child_to_search,
                                            style_name=style_name,
                                            family=family))
        return styles


    def get_style(self, style_name=None, family=None, category=None,
                       display_name=None):
        """Return the style uniquely identified by the name/family pair. If
        the argument is already a style object, it will return it.

        The category is for searching a named or automatic style or both (only
        for paragraph, text, etc. styles).

        If the name is not the internal name but the name you gave in the
        desktop application, set display_name to True.

        Arguments:

            style_name -- unicode

            family -- 'font-face', 'paragraph', 'text',

            category -- list which values are one of 'automatic', 'default',
                        'master' and 'named'

            display_name -- unicode

        Return: odf_style or None if not found
        """
        styles = self.get_style_list(style_name=style_name, family=family,
                                     category=category,
                                     display_name=display_name)
        return styles[0] if styles else None

