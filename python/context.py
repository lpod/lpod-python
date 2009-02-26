# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from libxml2
from libxml2 import parseMemory



class odf_element(object):
    """Representation of an XML element.
    Abstraction of the XML library behind.
    """

    def __init__(self, internal_element):
        # TODO check is element node
        self.__element = internal_element


    def get_element_list(self, xpath_expression):
        element = self.__element
        xpath_context = element.xpathNewContext()
        result = xpath_context.xpathEval(xpath_expression)
        xpath_context.xpathFreeContext()
        # TODO only element nodes
        return [odf_element(e) for e in result]


    def get_attribute(self, name):
        element = self.__element
        properties = element.properties
        if properties is None:
            return None
        return properties.get(name)


    def set_attribute(self, name, value):
        element = self.__element
        element.setProp(name, value)

    
    def get_text(self):
        # XXX all text recursively is need?
        element = self.__element
        # FIXME encoding?
        return element.getContent()


    def set_text(self, text):
        element = self.__element
        # TODO apply the warning in help(elt.setContent)
        # FIXME encoding?
        element.setContent(text)


    def insert_element(self, element, position):
        raise NotImplementedError


    def copy(self):
        element = self.__element
        # TODO only element nodes
        return [odf_element(e) for e in element.copyNodeList()]


    def delete(self):
        raise NotImplementedError



class odf_context(object):
    """Representation of an XML part.
    Abstraction of the XML library behind.
    """

    def __init__(self, part_name, container):
        self.part_name = part_name
        self.container = container

        # Internal state
        self.__document = None


    def __del__(self):
        if self.__document is not None:
            self.__document.freeDoc()


    def __get_document(self):
        if self.__document is None:
            container = self.container
            part = container.get_part(self.part_name)
            self.__document = parseMemory(part, len(part))
        return self.__document


    def get_element_list(self, xpath_expression):
        document = self.__get_document()
        xpath_context = document.xpathNewContext()
        result = xpath_context.xpathEval(xpath_expression)
        xpath_context.xpathFreeContext()
        # TODO only element nodes
        return [odf_element(e) for e in result]


    def serialize(self):
        # TODO another method to write back in the container?
        return str(self.__get_document())



def create_element(data):
    document = parseMemory(data, len(data))
    copy = document.children.copyNodeList()
    document.freeDoc()
    return odf_element(copy)
