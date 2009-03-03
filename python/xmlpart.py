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


CHILD, NEXT_SIBLING, PREV_SIBLING = range(3)



class odf_element(object):
    """Representation of an XML element.
    Abstraction of the XML library behind.
    """

    def __init__(self, internal_element):
        # TODO check is element node
        self.__element = internal_element


    def __del__(self):
        element = self.__element
        document = element.doc
        if getattr(document, '__lpod_must_free', False) is True:
            # It's an element created ex nihilo
            document.freeDoc()
        # FIXME raises a segmentation fault
        #element.freeNode()


    def get_element_list(self, xpath_expression):
        element = self.__element
        document = element.doc
        xpath_context = document.xpathNewContext()
        result = xpath_context.xpathEval(xpath_expression)
        xpath_context.xpathFreeContext()
        # TODO only element nodes
        return [odf_element(e) for e in result]


    def get_attribute(self, name):
        element = self.__element
        property = element.hasProp(name)
        if property is None:
            return None
        # Entites and special characters seem to be decoded internally
        return property.getContent()


    def set_attribute(self, name, value):
        element = self.__element
        if isinstance(value, unicode):
            value = value.encode('utf_8')
        if not isinstance(value, str):
            raise TypeError, 'value is not str'
        # Entites and special characters seem to be encoded internally
        element.setProp(name, value)


    def del_attribute(self, name):
        element = self.__element
        element.unsetProp(name)


    def get_text(self):
        # XXX all text recursively is need?
        element = self.__element
        # FIXME str or unicode?
        return element.getContent()


    def set_text(self, text):
        element = self.__element
        if isinstance(text, unicode):
            text = text.encode('utf_8')
        if not isinstance(text, str):
            raise TypeError, 'text is not str'
        # Encode entites and special characters
        doc = element.doc
        text = doc.encodeEntitiesReentrant(text)
        text = doc.encodeSpecialChars(text)
        element.setContent(text)


    def insert_element(self, element, position):
        if not isinstance(element, odf_element):
            raise TypeError, "element is not of type odf_element"
        current = self.__element
        element = element.__element
        if position == CHILD:
            current = current.addChild(element)
        elif position == NEXT_SIBLING:
            current = current.addNextSibling(element)
        elif position == PREV_SIBLING:
            current = current.addPrevSibling(element)
        else:
            raise ValueError, "invalid positioning"
        return odf_element(current)


    def copy(self):
        element = self.__element
        # TODO only element nList()]List()]odes
        doc = element.doc
        return odf_element(doc.copyNodeList(element))


    def serialize(self):
        element = self.__element
        return str(element)


    def delete(self):
        element = self.__element
        element.unlinkNode()



class odf_xmlpart(object):
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
    # XXX must free it along with the element
    document.__lpod_must_free = True
    return odf_element(document.children)
