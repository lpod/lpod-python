# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from lpod.utils import _make_xpath_query
from lpod.style import odf_style
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

    def get_default_styles_context(self):
        return self.get_element('//office:styles')


    def get_named_styles_context(self):
        return self.get_element('//office:styles')


    def get_automatic_styles_context(self):
        return self.get_element('//office:automatic-styles')


    def get_page_layout_styles_context(self):
        return self.get_element('//office:automatic-styles')


    def get_master_styles_context(self):
        return self.get_element('//office:master-styles')


    def _get_category_context(self, category):
        if category is None:
            return None
        mapping = {'default': self.get_default_styles_context,
                   'named': self.get_named_styles_context,
                   'automatic': self.get_automatic_styles_context,
                   'page-layout': self.get_page_layout_styles_context,
                   'master': self.get_master_styles_context}
        if category not in mapping:
            raise ValueError, "unknown category: " + category
        return mapping[category]()


    def _get_category_name(self, category):
        mapping = {'default': 'style:default-style',
                   'named': 'style:style',
                   'automatic': 'style:style',
                   'page-layout': 'style:page-layout',
                   'master': 'style:master-page'}
        if category is None:
            return '|'.join(set(mapping.itervalues()))
        if category not in mapping:
            raise ValueError, "unknown category: " + category
        return mapping[category]


    def get_style_list(self, family=None, category=None):
        tagname = self._get_category_name(category)
        query = _make_xpath_query(tagname, family=family)
        context = self._get_category_context()
        if context is None:
            return self.get_element_list(query)
        return context.get_element_list(query)


    def get_style(self, name_or_element, family, automatic=False,
                  display_name=False):
        """Return the style uniquely identified by the name/family pair. If
        the argument is already a style object, it will return it.

        If the name is None, the default style is fetched.

        For fetching an automatic style instead of a named style, set
        automatic to True.

        If the name is not the internal name but the name you gave in the
        desktop application, set display_name to True.

        Arguments:

            name_or_element -- unicode or odf_style

            family -- 'paragraph', 'text',  'graphic', 'page-layout',
                      'page-master', 'list', 'number'

            automatic -- bool

            display_name -- bool

        Return: odf_style or None if not found
        """
        if display_name is True:
            raise NotImplementedError
        if type(name_or_element) is unicode:
            tagname = self._get_category_name(category)
            query = _make_xpath_query(tagname, style_name=name_or_element)
            context = self._get_category_context(category)
            if context is None:
                return self.get_element(query)
            else:
                return context.get_element(query)
        elif isinstance(name_or_element, odf_style):
            return name_or_element
        raise TypeError, "style name or element expected"
