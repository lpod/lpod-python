# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from style import odf_style
from utils import _make_xpath_query, _get_style_tagname
from xmlpart import odf_xmlpart


class odf_content(odf_xmlpart):

    def get_body(self):
        return self.get_element('//office:body/*[1]')


    # The following two seem useless but they match styles API

    def _get_style_context(self, name, family):
        return self.get_element('//office:automatic-styles')


    def _get_style_tagname(self, family, name):
        if name is False:
            # Treat the case for get_style_list where the name is undefined
            all = ['style:style']
            return ('(//%s)' % '|//'.join(all), family)
        return _get_style_tagname(family)


    #
    # Public API
    #

    def get_style_list(self, family=None):
        tagname, famattr = self._get_style_tagname(family, False)
        query = _make_xpath_query(tagname, family=famattr)
        context = self._get_style_context(False, family)
        return context.get_element_list(query)


    def get_style(self, family, name_or_element=None, display_name=False):
        """Return the style uniquely identified by the name/family pair. If
        the argument is already a style object, it will return it.

        If the name is not the internal name but the name you gave in the
        desktop application, set display_name to True.

        Arguments:

            name_or_element -- unicode or odf_style

            family -- 'paragraph', 'text', 'graphic', 'table', 'list',
                      'number'

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


    def get_tracked_changes(self):
        """Return the tracked-changes part in the text body.
        """
        return self.get_element('//text:tracked-changes')
