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
from xmlpart import odf_xmlpart


class odf_content(odf_xmlpart):

    def get_body(self):
        return self.get_root().get_body()


    # The following two seem useless but they match styles API

    def _get_style_contexts(self, family):
        if family == 'font-face':
            return (self.get_element('//office:font-face-decls'),)
        return (self.get_element('//office:font-face-decls'),
                self.get_element('//office:automatic-styles'))


    #
    # Public API
    #

    def get_style_list(self, family=None):
        """Return the list of styles in the Content part, optionally limited
        to the given family.

        Arguments:

            family -- str

        Return: list of odf_style
        """
        result = []
        for context in self._get_style_contexts(family):
            if context is None:
                continue
            result.extend(context.get_style_list(family=family))
        return result


    def get_style(self, family, name_or_element=None, display_name=None):
        """Return the style uniquely identified by the name/family pair. If
        the argument is already a style object, it will return it.

        If the name is not the internal name but the name you gave in the
        desktop application, use display_name instead.

        Arguments:

            family -- 'paragraph', 'text', 'graphic', 'table', 'list',
                      'number'

            name_or_element -- unicode or odf_style

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
