# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from itools
from itools.core import get_abspath

# Import from libxml2
from libxml2 import parseDoc, xmlNode


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


FIRST_CHILD, LAST_CHILD, NEXT_SIBLING, PREV_SIBLING = range(4)



class odf_element(object):
    """Representation of an XML element.
    Abstraction of the XML library behind.
    """

    def __init__(self, internal_element):
        if (not isinstance(internal_element, xmlNode)
                or internal_element.type != 'element'):
            raise TypeError, "node is not an element node"
        self.__element = internal_element


    def __decode_qname(self, qname):
        if ':' in qname:
            prefix, name = qname.split(':')
            try:
                uri = ODF_NAMESPACES[prefix]
            except IndexError:
                raise ValueError, "XML prefix '%s' is unknown" % prefix
            element = self.__element
            namespace = element.searchNsByHref(element.doc, uri)
        else:
            namespace, uri, name = None, None, qname
        return namespace, uri, name


    def get_element_list(self, xpath_query, context=None):
        if context is not None:
            raise NotImplementedError
        element = self.__element
        document = element.doc
        xpath_context = document.xpathNewContext()
        result = xpath_context.xpathEval(xpath_query)
        xpath_context.xpathFreeContext()
        return [odf_element(e) for e in result]


    def get_attribute(self, name):
        element = self.__element
        namespace, uri, name = self.__decode_qname(name)
        if namespace is not None:
            property = element.hasNsProp(name, uri)
        else:
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
        namespace, uri, name = self.__decode_qname(name)
        if namespace is not None:
            element.setNsProp(namespace, name, value)
        else:
            element.setProp(name, value)
        # Entites and special characters seem to be encoded internally


    def del_attribute(self, name):
        element = self.__element
        namespace, uri, name = self.__decode_qname(name)
        if namespace is not None:
            element.unsetNsProp(namespace, name)
        else:
            element.unsetProp(name)
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
            raise TypeError, "element is not odf_element"
        current = self.__element
        element = element.__element
        if position is FIRST_CHILD:
            first_child = current.children
            first_child.addPrevSibling(element)
        elif position is LAST_CHILD:
            current.addChild(element)
        elif position is NEXT_SIBLING:
            current.addNextSibling(element)
        elif position is PREV_SIBLING:
            current.addPrevSibling(element)
        else:
            raise ValueError, "invalid position"
        return odf_element(current)


    def copy(self):
        element = self.__element
        doc = element.doc
        return odf_element(doc.copyNodeList(element))


    def serialize(self):
        element = self.__element
        return str(element)


    def delete(self):
        element = self.__element
        element.unlinkNode()


# An empty XML document with all namespaces declared
ns_document_path = get_abspath('templates/namespaces.xml')
with open(ns_document_path, 'rb') as file:
    ns_document_data = file.read()



def odf_create_element(element_data):
    if not isinstance(element_data, str):
        raise TypeError, "element data is not str"
    if not element_data.strip():
        raise ValueError, "element data is empty"
    data = ns_document_data.format(element=element_data)
    document = parseDoc(data)
    root = document.children
    element = root.children
    return odf_element(element)



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
            self.__document = parseDoc(part)
        return self.__document


    def __get_xpath_context(self):
        if self.__xpath_context is None:
            document = self.__get_document()
            xpath_context = document.xpathNewContext()
            # XXX needs to be filled with all the ODF namespaces or something
            for prefix, uri in ODF_NAMESPACES.items():
                xpath_context.xpathRegisterNs(prefix, uri)
            self.__xpath_context = xpath_context
        return self.__xpath_context


    def get_element_list(self, xpath_query, context=None):
        if context is not None:
            raise NotImplementedError
        xpath_context = self.__get_xpath_context()
        result = xpath_context.xpathEval(xpath_query)
        return [odf_element(e) for e in result]


    def serialize(self):
        # TODO another method to write back in the container?
        return str(self.__get_document())
