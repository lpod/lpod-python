# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from copy import deepcopy
from cStringIO import StringIO

# Import from lxml
from lxml.etree import parse, tostring

# Import from lpod
from element import make_odf_element


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
            self.__root = make_odf_element(tree.getroot())
        return self.__root


    def get_element_list(self, xpath_query):
        root = self.get_root()
        return root.xpath(xpath_query)


    def get_element(self, xpath_query):
        result = self.get_element_list(xpath_query)
        if not result:
            return None
        return result[0]


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
        # lxml declaration is too exotic too me
        return ('<?xml version="1.0" encoding="UTF-8"?>\n'
                + tostring(tree, encoding='UTF-8', pretty_print=pretty))


    def delete(self, child):
        parent = child.get_parent()
        parent.delete(child)
