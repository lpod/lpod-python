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
from element import register_element_class, odf_element, odf_create_element


def odf_create_draw_page(page_id, name=None, master_page=None,
                         page_layout=None, style=None):
    """This element is a container for content in a drawing or presentation
    document.

    Arguments:

        page_id -- str

        name -- unicode

        master_page -- str

        page_layout -- str

        style -- str

    Return: odf_element
    """
    element = odf_create_element('<draw:page/>')
    element.set_attribute('draw:id', page_id)
    if name:
        element.set_attribute(u'draw:name', name)
    if style:
        element.set_attribute('draw:style-name', style)
    if master_page:
        element.set_attribute('draw:master-page-name', master_page)
    if page_layout:
        element.set_attribute('presentation:presentation-page-layout-name',
                              page_layout)
    return element



class odf_draw_page(odf_element):
    """Specialised element for pages of presentation and drawing.
    """
    def get_page_name(self):
        return self.get_attribute('draw:name')


    def set_page_name(self, name):
        self.set_attribute('draw:name', name)



register_element_class('draw:page', odf_draw_page)
