# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from copy import deepcopy
from zipfile import ZipFile
from cStringIO import StringIO

# Import from itools
from itools import vfs
from itools.core import get_abspath
from itools.xml import XMLParser



def create_element(data):
    return XMLParser(data)



class odf_element(object):
    """Representation of an XML element.
    Abstraction of the XML library behind.
    """

    def get_element_list(self, xpath):
        raise NotImplementedError


    def get_attribute(self, name):
        raise NotImplementedError


    def set_attribute(self, name):
        raise NotImplementedError

    
    def get_text(self):
        raise NotImplementedError


    def set_text(self, text):
        raise NotImplementedError


    def insert_element(self, element, position):
        raise NotImplementedError


    def copy(self):
        raise NotImplementedError



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
        self.__events = None


    def __get_events(self):
        if self.__events is None:
            container = self.container
            part = container.get_part(self.part_name)
            self.__events = XMLParser(part)
        return self.__events


    def get_element_list(self, xpath):
        raise NotImplementedError


    def serialize(self):
        raise NotImplementedError
