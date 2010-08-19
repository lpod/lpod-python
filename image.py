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
from element import odf_create_element, odf_element, register_element_class
from style import register_style


def odf_create_image(uri):
    """Create an image element showing the image at the given URI.

    Warning: image elements must be stored in a frame.

    Arguments:

        uri -- str

    Return: odf_element
    """
    element = odf_create_element('draw:image')
    element.set_href(uri)
    return element



class odf_image(odf_element):

    def get_href(self):
        return self.get_attribute('xlink:href')


    def set_href(self, href):
        return self.set_attribute('xlink:href', href)



class odf_background_image(odf_image):

    def get_position(self):
        return self.get_attribute('style:position')


    def set_position(self, position):
        return self.set_attribute('style:position', position)


    def get_repeat(self):
        return self.get_attribute('style:repeat')


    def set_repeat(self, repeat):
        return self.set_attribute('style:repeat', repeat)


    def get_opacity(self):
        return self.get_attribute('draw:opacity')


    def set_opacity(self, opacity):
        return self.set_attribute('draw:opacity', str(opacity))


    def get_filter(self):
        return self.get_attribute('style:filter-name')


    def set_filter(self, filter):
        return self.set_style_attribute('style:filter-name', filter)



register_element_class('draw:image', odf_image)
register_style('style:background-image', odf_background_image)
