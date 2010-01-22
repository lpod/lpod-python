# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
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

# Import from the Standard Library
from copy import deepcopy
from cStringIO import StringIO

# Import from lxml
from lxml.etree import parse, tostring

# Import from lpod
from element import _make_odf_element


class odf_xmlpart(object):
    """Representation of an XML part.
    Abstraction of the XML library behind.
    """
    def __init__(self, part_name, container):
        self.part_name = part_name
        self.container = container

        # Internal state
        self.__tree = None
        self.__root = None


    def __get_tree(self):
        if self.__tree is None:
            container = self.container
            part = container.get_part(self.part_name)
            self.__tree = parse(StringIO(part))
        return self.__tree


    #
    # Public API
    #

    def get_root(self):
        if self.__root is None:
            tree = self.__get_tree()
            self.__root = _make_odf_element(tree.getroot())
        return self.__root


    def get_element_list(self, xpath_query):
        root = self.get_root()
        return root.xpath(xpath_query)


    def get_element(self, xpath_query):
        result = self.get_element_list(xpath_query)
        if not result:
            return None
        return result[0]


    def delete_element(self, child):
        child.get_parent().delete_element(child)


    def clone(self):
        clone = object.__new__(self.__class__)
        for name in self.__dict__:
            if name == 'container':
                setattr(clone, name, self.container.clone())
            elif name in ('_odf_xmlpart__tree',):
                setattr(clone, name, None)
            else:
                value = getattr(self, name)
                value = deepcopy(value)
                setattr(clone, name, value)
        return clone


    def serialize(self, pretty=False):
        tree = self.__get_tree()
        # Lxml declaration is too exotic to me
        data = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                + tostring(tree, encoding='UTF-8', pretty_print=pretty))
        # Lxml with pretty_print is adding a empty line
        if pretty:
            data = data.strip()
        return data
