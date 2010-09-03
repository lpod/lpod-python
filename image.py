# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
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


def odf_create_image(url, type='simple', show='embed', actuate='onLoad'):
    """Create an image element showing the image at the given URL.

    Warning: image elements must be stored in a frame.

    Arguments:

        url -- str

    Return: odf_element
    """
    image = odf_create_element('draw:image')
    image.set_url(url)
    image.set_type(type)
    image.set_show(show)
    image.set_actuate(actuate)
    return image



class odf_image(odf_element):

    def get_url(self):
        return self.get_attribute('xlink:href')


    def set_url(self, url):
        return self.set_attribute('xlink:href', url)


    def get_type(self):
        return self.get_attribute('xlink:type')


    def set_type(self, type):
        return self.set_attribute('xlink:type', type)


    def get_show(self):
        return self.get_attribute('xlink:show')


    def set_show(self, show):
        return self.set_attribute('xlink:show', show)


    def get_actuate(self):
        return self.get_attribute('xlink:actuate')


    def set_actuate(self, actuate):
        return self.set_attribute('xlink:actuate', actuate)



register_element_class('draw:image', odf_image)
