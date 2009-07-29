# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library

# Import from lpod
from lpod.utils import _make_xpath_query
from lpod.xmlpart import odf_element, odf_xmlpart


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

    def get_category_context(self, category):
        if category is None:
            return None
        elif category == 'named':
            return self.get_element('//office:styles')
        elif category == 'automatic':
            return self.get_element('//office:automatic-styles')
        elif category == 'master':
            return self.get_element('//office:master-styles')
        raise ValueError, ('category must be None, "named", "automatic" '
                           'or "master"')


    def get_style_list(self, family=None, category=None):
        query = _make_xpath_query('style:style', family=family)
        context = self.get_category_context(category)
        if context is None:
            return self.get_element_list(query)
        else:
            return context.get_element_list(query)


    def get_style(self, name_or_element, family, category=None,
                  retrieve_by='name'):
        if isinstance(name_or_element, odf_element):
            if not name_or_element.is_style():
                raise ValueError, "element is not a style element"
        elif type(name_or_element) is str:
            if family == 'page-layout':
                query = _make_xpath_query('style:page-layout',
                                          style_name=name_or_element)
            else:
                query = _make_xpath_query('style:style',
                                          style_name=name_or_element)
            context = self.get_category_context(category)
            if context is None:
                return self.get_element(query)
            else:
                return context.get_element(query)
        raise TypeError, "style name or element expected"


    def get_parent_style(self, name_or_element, family):
        style = self.get_style(name_or_element, family)
        parent_name = style.get_attribute('style:parent-style-name')
        return self.get_style(parent_name, family)


    # TODO get/set_properties(name_or_element, style, family=None)
    # same family than the style by default, or "text", "paragraph", etc.
