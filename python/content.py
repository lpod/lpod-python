# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from style import odf_style
from utils import _get_element_list, _get_element
from xmlpart import odf_xmlpart


class odf_content(odf_xmlpart):

    def get_body(self):
        return self.get_element('//office:body/*[1]')


    #
    # Styles found in context.xml
    #

    def get_automatic_styles_context(self):
        return self.get_element('//office:automatic-styles')


    # The following two seem useless but they match styles API

    def _get_category_context(self, category):
        if category is None:
            return None
        if category == 'automatic':
            return self.get_automatic_styles_context()
        raise ValueError, "unknown category: " + category


    def _get_category_name(self, category):
        if category is None or category == 'automatic':
            return 'style:style'
        raise ValueError, "unknown category: " + category


    def get_style_list(self, family=None):
        return _get_element_list(self, 'descendant::style:style',
                                 family=family)


    def get_style(self, name_or_element, family, display_name=False):
        """Return the style uniquely identified by the name/family pair. If
        the argument is already a style object, it will return it.

        If the name is not the internal name but the name you gave in the
        desktop application, set display_name to True.

        Arguments:

            name_or_element -- unicode or odf_style

            family -- 'font-face', 'paragraph', 'text', etc. TODO

            display_name -- bool

        Return: odf_style or None if not found
        """
        if display_name is True:
            raise NotImplementedError
        if type(name_or_element) is unicode:
            context = self.get_automatic_styles_context()
            return _get_element(context, 'style:style',
                                style_name=name_or_element, family=family)
        elif isinstance(name_or_element, odf_style):
            return name_or_element
        raise TypeError, "style name or element expected"


    def get_tracked_changes(self):
        """Return the tracked-changes part in the text body.
        """
        return self.get_element('//text:tracked-changes')

