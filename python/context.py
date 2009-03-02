# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from libxml2
from libxml2 import parseMemory


ODF_NAMESPACES = {
        'office': "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
        'style': "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
        'text': "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
        'table': "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
        'draw': "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
        'fo': "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
        'xlink': "http://www.w3.org/1999/xlink",
        'dc': "http://purl.org/dc/elements/1.1/",
        'meta': "urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
        'number': "urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0",
        'svg': "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0",
        'chart': "urn:oasis:names:tc:opendocument:xmlns:chart:1.0",
        'dr3d': "urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0",
        'math': "http://www.w3.org/1998/Math/MathML",
        'form': "urn:oasis:names:tc:opendocument:xmlns:form:1.0",
        'script': "urn:oasis:names:tc:opendocument:xmlns:script:1.0",
        'ooo': "http://openoffice.org/2004/office",
        'ooow': "http://openoffice.org/2004/writer",
        'oooc': "http://openoffice.org/2004/calc",
        'dom': "http://www.w3.org/2001/xml-events",
        'xforms': "http://www.w3.org/2002/xforms",
        'xsd': "http://www.w3.org/2001/XMLSchema",
        'xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'rpt': "http://openoffice.org/2005/report",
        'of': "urn:oasis:names:tc:opendocument:xmlns:of:1.2",
        'rdfa': "http://docs.oasis-open.org/opendocument/meta/rdfa#",
        'config': "urn:oasis:names:tc:opendocument:xmlns:config:1.0",
        }



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
        self.__xpath_context = None


    def __del__(self):
        if self.__xpath_context is not None:
            self.__xpath_context.xpathFreeContext()
        if self.__document is not None:
            self.__document.freeDoc()


    def __get_document(self):
        if self.__document is None:
            container = self.container
            part = container.get_part(self.part_name)
            self.__document = parseMemory(part, len(part))
        return self.__document


    def __get_xpath_context(self):
        if self.__xpath_context is None:
            document = self.__get_document()
            xpath_context = document.xpathNewContext()
            # XXX needs to be filled with all the ODF namespaces or something
            for name, uri in ODF_NAMESPACES.items():
                xpath_context.xpathRegisterNs(name, uri)
            self.__xpath_context = xpath_context
        return self.__xpath_context


    def get_element_list(self, xpath_expression):
        xpath_context = self.__get_xpath_context()
        result = xpath_context.xpathEval(xpath_expression)
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
