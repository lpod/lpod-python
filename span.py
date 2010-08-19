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
from element import odf_create_element, register_element_class
from paragraph import odf_paragraph



def odf_create_span(text=None, style=None):
    """Create a span element of the given style containing the optional
    given text.

    Arguments:

        style -- unicode

        text -- unicode

    Return: odf_element
    """
    element = odf_create_element('text:span')
    if text:
        element.set_text(text)
    if style:
        element.set_text_style(style)
    return element



class odf_span(odf_paragraph):

    def get_style(self):
        return self.get_attribute('text:style-name')


    def set_style(self, name):
        return self.set_attribute('text:style-name', name)



register_element_class('text:span', odf_span)
