# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from copy import deepcopy
from cStringIO import StringIO
from re import compile

# Import from lxml
from lxml.etree import parse, fromstring, tostring, _Element

# Import from lpod
from utils import _check_arguments, _get_abspath, DateTime
from utils import _make_xpath_query


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


FIRST_CHILD, LAST_CHILD, NEXT_SIBLING, PREV_SIBLING, STOPMARKER = range(5)


ns_stripper = compile(' xmlns:\w*="[\w:\-\/\.#]*"')


# An empty XML document with all namespaces declared
ns_document_path = _get_abspath('templates/namespaces.xml')
with open(ns_document_path, 'rb') as file:
    ns_document_data = file.read()



def decode_qname(qname):
    """Turn a prefixed name to a (uri, name) pair.
    """
    if ':' in qname:
        prefix, name = qname.split(':')
        try:
            uri = ODF_NAMESPACES[prefix]
        except IndexError:
            raise ValueError, "XML prefix '%s' is unknown" % prefix
        return uri, name
    return None, qname



def uri_to_prefix(uri):
    """Find the prefix associated to the given URI.
    """
    for key, value in ODF_NAMESPACES.iteritems():
        if value == uri:
            return key
    raise ValueError, 'uri "%s" not found' % uri



def get_prefixed_name(tag):
    """Replace lxml "{uri}name" syntax with "prefix:name" one.
    """
    uri, name = tag.split('}', 1)
    prefix = uri_to_prefix(uri[1:])
    return '%s:%s' % (prefix, name)



def odf_create_element(element_data):
    if not isinstance(element_data, str):
        raise TypeError, "element data is not str"
    if not element_data.strip():
        raise ValueError, "element data is empty"
    data = ns_document_data.format(element=element_data)
    root = fromstring(data)
    return odf_element(root[0])



class odf_element(object):
    """Representation of an XML element.
    Abstraction of the XML library behind.
    """

    def __init__(self, native_element):
        if not isinstance(native_element, _Element):
            raise TypeError, "node is not an element node"
        self.__element = native_element


    def __str__(self):
        return '%s "%s"' % (object.__str__(self), self.get_name())


    def get_name(self):
        element = self.__element
        return get_prefixed_name(element.tag)


    def get_element_list(self, xpath_query):
        element = self.__element
        result = element.xpath(xpath_query, namespaces=ODF_NAMESPACES)
        return [odf_element(e) for e in result]


    def get_element(self, xpath_query):
        result = self.get_element_list(xpath_query)
        if result:
            return result[0]
        return None


    def get_attributes(self):
        attributes = {}
        element = self.__element
        for key, value in element.attrib.iteritems():
            attributes[get_prefixed_name(key)] = value
        return attributes


    def get_attribute(self, name):
        element = self.__element
        uri, name = decode_qname(name)
        if uri is None:
            return element.get(name)
        return element.get('{%s}%s' % (uri, name))


    def set_attribute(self, name, value):
        element = self.__element
        uri, name = decode_qname(name)
        if uri is None:
            element.set(name, value)
        else:
            element.set('{%s}%s' % (uri, name), value)


    def del_attribute(self, name):
        element = self.__element
        uri, name = decode_qname(name)
        if uri is None:
            del element.attrib[name]
        else:
            del element.attrib['{%s}%s' % (uri, name)]


    def get_text(self):
        element = self.__element
        text = element.text
        if len(element):
            last_child = element[-1]
            if last_child.tail is not None:
                text += last_child.tail
        return text


    def set_text(self, text, after=False):
        """If "after" is true, sets the text at the end of the element, not
        inside.
        FIXME maybe too specific to lxml
        """
        element = self.__element
        if after:
            element.tail = text
        else:
            element.text = text


    def get_parent(self):
        element = self.__element
        parent = element.getparent()
        if parent is None:
            # Already at root
            return None
        return self.__class__(parent)


    def get_creator(self):
        dc_creator = self.get_element('//dc:creator')
        if dc_creator is None:
            return None
        creator = dc_creator.get_text()
        return unicode(dc_creator.get_text(), 'utf_8')


    def get_date(self):
        dc_date = self.get_element('//dc:date')
        if dc_date is None:
            return None
        date = dc_date.get_text()
        return DateTime.decode(date)


    def get_text_content(self):
        """Like "get_text" but applied to the embedded paragraph:
        annotations, cells...
        """
        element = self.__element
        text = element.xpath('string(text:p)', namespaces=ODF_NAMESPACES)
        return unicode(text, 'utf_8')


    def set_text_content(self, text):
        """Like "set_text" but applied to the embedded paragraph:
        annotations, cells...
        """
        _check_arguments(text=text)
        paragraph = self.get_element('text:p')
        if paragraph is None:
            paragraph = odf_create_element('<text:p/>')
            self.insert_element(paragraph, FIRST_CHILD)
        element = paragraph.__element
        element.clear()
        element.text = text


    def insert_element(self, element, xmlposition=LAST_CHILD):
        _check_arguments(element=element, xmlposition=xmlposition)
        current = self.__element
        element = element.__element
        if xmlposition is FIRST_CHILD:
            current.insert(0, element)
        elif xmlposition is LAST_CHILD:
            current.append(element)
        elif xmlposition is NEXT_SIBLING:
            parent = current.getparent()
            index = parent.index(current)
            parent.insert(index + 1, element)
        elif xmlposition is PREV_SIBLING:
            parent = current.getparent()
            index = parent.index(current)
            parent.insert(index, element)
        else:
            raise ValueError, "xmlposition must be defined"


    def xpath(self, xpath_query):
        element = self.__element
        result = element.xpath(xpath_query, namespaces=ODF_NAMESPACES)
        return [self.__class__(e) for e in result]


    def clear(self):
        element = self.__element
        element.clear()
        element.text = None


    def clone(self):
        element = self.__element
        return odf_element(deepcopy(element))


    def serialize(self):
        element = self.__element
        data = tostring(element)
        # XXX hack over lxml: remove namespaces
        return ns_stripper.sub('', data)


    def delete(self, child):
        _check_arguments(element=child)
        element = self.__element
        element.remove(child.__element)


    def is_style(self):
        return self.get_attribute('style:name') is not None



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
    # Non-public yet useful helpers
    #

    def _get_element_list(self, element_name, style=None, family=None,
                          frame_name=None, frame_style=None, table_name=None,
                          note_class=None, style_name=None, text_id=None,
                          level=None, position=None, context=None):
        _check_arguments(style=style, family=family, note_class=note_class,
                         level=level, position=position, context=context)
        query = _make_xpath_query(element_name, style=style, family=family,
                                  frame_name=frame_name,
                                  frame_style=frame_style,
                                  table_name=table_name,
                                  style_name=style_name,
                                  note_class=note_class, text_id=text_id,
                                  level=level, position=position,
                                  context=context)
        if context is None:
            return self.get_element_list(query)
        return context.get_element_list(query)


    def _get_element(self, element_name, style=None, family=None,
                     frame_name=None, table_name=None, style_name=None,
                     text_id=None, level=None, position=None, context=None):
        result = self._get_element_list(element_name, style=style,
                                        family=family, frame_name=frame_name,
                                        table_name=table_name,
                                        style_name=style_name,
                                        text_id=text_id, level=level,
                                        position=position, context=context)
        if result:
            return result[0]
        return None


    #
    # Public API
    #

    def get_root(self):
        if self.__root is None:
            tree = self.__get_tree()
            self.__root = odf_element(tree.getroot())
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
