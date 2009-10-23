# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
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
        # Default style
        if name_or_element is None and display_name is False:
            return None

        # Common style
        elif type(name_or_element) is unicode or name_or_element is None:
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

        # An odf_style
        elif isinstance(name_or_element, odf_style):
            return name_or_element

        # Error
        raise TypeError, "style name or element expected"


    def get_tracked_changes(self):
        """Return the tracked-changes part in the text body.
        """
        return self.get_element('//text:tracked-changes')
