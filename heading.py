# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Hervé Cauwelier <herve@itaapy.com>
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
from paragraph import odf_paragraph
from element import register_element_class, odf_create_element


def odf_create_heading(level, text=None, restart_numbering=False,
                       start_value=None, suppress_numbering=False,
                       style=None):
    """Create a heading element of the given style and level, containing the
    optional given text.

    Level count begins at 1.

    Arguments:

        level -- int

        text -- unicode

        restart_numbering -- bool

        start_value -- int

        style -- unicode

    Return: odf_element
    """
    data = '<text:h text:outline-level="%d"/>'
    element = odf_create_element(data % level)
    if text:
        element.set_text(text)
    if restart_numbering:
        element.set_attribute('text:restart-numbering', 'true')
    if start_value:
        element.set_attribute('text:start-value', start_value)
    if suppress_numbering:
        element.set_attribute('text:suppress-numbering', 'true')
    if style:
        element.set_attribute('text:style-name', style)
    return element



class odf_heading(odf_paragraph):
    """Specialised element for headings, which themselves are Specialised
    paragraphs.
    """

    def get_formated_text(self, context):
        # 5 levels of heading
        level_styles = u"=-+~."

        # Get the title
        title = odf_paragraph.get_formated_text(self, context)
        title = title.strip()

        # Get the level
        level = self.get_outline_level()
        if level > 5:
            raise ValueError, "Too many levels of heading"

        # And return the result
        result = ['\n', title, u'\n', level_styles[level - 1] * len(title),
                  '\n']
        return u''.join(result)


    def set_outline_level(self, level):
        self.set_attribute('text:outline-level', unicode(level))


    def get_outline_level(self):
        return int(self.get_attribute('text:outline-level'))



register_element_class('text:h', odf_heading)
