# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2013 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Hervé Cauwelier <herve@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>
#
# This file is part of Lpod (see: http://lpod-project.net).
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
from element import odf_element, odf_create_element, register_element_class
from paragraph import paragraph_base



def odf_create_link(url, name=None, title=None, text=None, target_frame=None,
                    style=None, visited_style=None):
    """Return a text:a odf_element.

    Arguments:

        url -- str

        name -- unicode

        title -- unicode

        text -- unicode

        target_frame -- '_self', '_blank', '_parent', '_top'

        style -- string

        visited_style -- string
    """
    link = odf_create_element('text:a')
    link.set_url(url)
    if name is not None:
        link.set_name(name)
    if title is not None:
        link.set_title(title)
    if text is not None:
        link.set_text(text)
    #if target_frame is None:
    #    target_frame = '_self'
    if target_frame is not None:
        link.set_target_frame(target_frame)
        if target_frame == '_blank':
            link.set_show('new')
        else:
            link.set_show('replace')
    if style is not None:
        link.set_style(style)
    if visited_style is not None:
        link.set_visited_style(visited_style)
    return link



class odf_link(paragraph_base):

    def get_name(self):
        return self.get_attribute('office:name')


    def set_name(self, name):
        return self.set_attribute('office:name', name)

    def get_url(self):
        return self.get_attribute('xlink:href')


    def set_url(self, url):
        return self.set_attribute('xlink:href', url)


    def get_title(self):
        return self.get_attribute('office:title')


    def set_title(self, title):
        return self.set_attribute('office:title', title)


    def get_target_frame(self):
        return self.get_attribute('office:target-frame-name')


    def set_target_frame(self, name):
        return self.set_style_attribute('office:target-frame-name', name)


    def get_show(self):
        return self.get_attribute('xlink:show')


    def set_show(self, value):
        """'new' or 'replace'
        """
        return self.set_attribute('xlink:show', value)


    def get_visited_style(self):
        return self.get_attribute('text:visited-style-name')


    def set_visited_style(self, name):
        attribute = 'text:visited-style-name'
        return self.set_style_attribute(attribute, name)


register_element_class('text:a', odf_link)
