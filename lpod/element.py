# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2013 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Hervé Cauwelier <herve@itaapy.com>
#          Romain Gauthier <romain@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>
#
# This file is part of Lpod (see: http://lpod-project.net).
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
import sys
from copy import deepcopy
import re

# Import from lxml
from lxml.etree import fromstring, tostring, Element, _Element
from lxml.etree import _ElementStringResult, _ElementUnicodeResult
from lxml.etree import XPath

# Import from lpod
from datatype import DateTime, Boolean
from utils import _get_abspath, _get_elements, _get_element
from utils import _get_style_tagname, get_value  #, obsolete
from utils import _get_style_tagname, get_value


ODF_NAMESPACES = {
    'anim': "urn:oasis:names:tc:opendocument:xmlns:animation:1.0",
    'chart': "urn:oasis:names:tc:opendocument:xmlns:chart:1.0",
    'config': "urn:oasis:names:tc:opendocument:xmlns:config:1.0",
    'dc': "http://purl.org/dc/elements/1.1/",
    'dom': "http://www.w3.org/2001/xml-events",
    'dr3d': "urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0",
    'draw': "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
    'fo': "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
    'form': "urn:oasis:names:tc:opendocument:xmlns:form:1.0",
    'math': "http://www.w3.org/1998/Math/MathML",
    'meta': "urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
    'number': "urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0",
    'of': "urn:oasis:names:tc:opendocument:xmlns:of:1.2",
    'office': "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    'ooo': "http://openoffice.org/2004/office",
    'oooc': "http://openoffice.org/2004/calc",
    'ooow': "http://openoffice.org/2004/writer",
    'presentation': "urn:oasis:names:tc:opendocument:xmlns:presentation:1.0",
    'rdfa': "http://docs.oasis-open.org/opendocument/meta/rdfa#",
    'rpt': "http://openoffice.org/2005/report",
    'script': "urn:oasis:names:tc:opendocument:xmlns:script:1.0",
    'smil': "urn:oasis:names:tc:opendocument:xmlns:smil-compatible:1.0",
    'style': "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    'svg': "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0",
    'table': "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    'text': "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    'xforms': "http://www.w3.org/2002/xforms",
    'xlink': "http://www.w3.org/1999/xlink",
    'xsd': "http://www.w3.org/2001/XMLSchema",
    'xsi': "http://www.w3.org/2001/XMLSchema-instance",
    'manifest': "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0",
    'xml': 'http://www.w3.org/XML/1998/namespace'
}


FIRST_CHILD, LAST_CHILD, NEXT_SIBLING, PREV_SIBLING, STOPMARKER = range(5)


ns_stripper = re.compile(r' xmlns:\w*="[\w:\-\/\.#]*"')

__xpath_query_cache = {}

# An empty XML document with all namespaces declared
ns_document_path = _get_abspath('templates/namespaces.xml')
__file = open(ns_document_path, 'rb')
ns_document_data = __file.read()
__file.close()



def _decode_qname(qname):
    """Turn a prefixed name to a (uri, name) pair.
    """
    if ':' in qname:
        prefix, name = qname.split(':')
        try:
            uri = ODF_NAMESPACES[prefix]
        except KeyError:
            raise ValueError("XML prefix '%s' is unknown" % prefix)
        return uri, name
    return None, qname



def _uri_to_prefix(uri):
    """Find the prefix associated to the given URI.
    """
    for key, value in ODF_NAMESPACES.iteritems():
        if value == uri:
            return key
    raise ValueError('uri "%s" not found' % uri)



def _get_prefixed_name(tag):
    """Replace lxml "{uri}name" syntax with "prefix:name" one.
    """
    uri, name = tag.split('}', 1)
    prefix = _uri_to_prefix(uri[1:])
    return '%s:%s' % (prefix, name)



def _xpath_compile(path):
    return XPath(path, namespaces=ODF_NAMESPACES, regexp=False)



def _find_query_in_cache(query):
    xpath = __xpath_query_cache.get(query, None)
    if xpath is None:
        xpath = _xpath_compile(query)
        __xpath_query_cache[query] = xpath
    return xpath


_xpath_text = _find_query_in_cache("//text()")   #  descendant and self
_xpath_text_descendant = _find_query_in_cache("descendant::text()")
_xpath_text_main = _find_query_in_cache(
                                '//*[not (parent::office:annotation)]/text()')
_xpath_text_main_descendant = _find_query_in_cache(
                        'descendant::text()[not (parent::office:annotation)]')
#
# Semi-Public API
# (not in the lpOD specification but foundation of the Python implementation)
#

__class_registry = {}

def register_element_class(qname, cls, family=None, caching=False):
    """Associate a qualified element name to a Python class that handles this
    type of element.

    Getting the right Python class when loading an existing ODF document is
    then transparent. Unassociated elements will be handled by the base
    odf_element class.

    Most styles use the "style:style" qualified name and only differ by their
    "style:family" attribute. So the "family" attribute was added to register
    specialized style classes.

    Arguments:

        qname -- str

        cls -- Python class

        family -- str
    """
    # Turn tag name into what lxml is expecting
    tag = '{%s}%s' % _decode_qname(qname)
    if (tag, family) in __class_registry:
        #raise ValueError('element "%s" already registered' % qname)
        return # fix doc generation multi import
    __class_registry[(tag, family)] = (cls, caching)



def _make_odf_element(native_element, cache=None):
    """Turn an lxml Element into an odf_element (or the registered subclass).

    Arguments:

        native_element -- lxml.Element

    Return: odf_element
    """
    tag = native_element.tag
    family = native_element.get("{%s}family" % ODF_NAMESPACES['style'])
    cls, caching = __class_registry.get((tag, family), (None, None))
    if cls is None and family is not None:
        cls, caching = __class_registry.get((tag, None), (None, None))
    if cls is None:
        cls = odf_element
    if caching:
        return cls(native_element, cache)
    else:
        return cls(native_element)



#
# Public API
#



def odf_create_element(element_data, cache=None):
    if type(element_data) is str:
        pass
    elif type(element_data) is unicode:
        element_data = element_data.encode('utf-8')
    else:
        raise TypeError("element data is not str or unicode")
    element_data = element_data.strip()
    if not element_data:
        raise ValueError("element data is empty")
    if '<' not in element_data:
        # Qualified name
        # XXX don't build the element from scratch or lxml will pollute with
        # repeated namespace declarations
        element_data = '<%s/>' % element_data
    # XML fragment
    data = ns_document_data % element_data
    root = fromstring(data)
    element = root[0]
    return _make_odf_element(element, cache)



# TODO remove some day
def _debug_element(native_element):
    return repr(odf_element(native_element).serialize(pretty=True))



class odf_text(unicode):
    """Representation of an XML text node. Created to hide the specifics of
    lxml in searching text nodes using XPath.

    Constructed like any unicode object but only accepts lxml text objects.
    """
    # There's some black magic in inheriting from unicode
    def __init__(self, text_result):
        self.__parent = text_result.getparent()
        self.__is_text = text_result.is_text
        self.__is_tail = text_result.is_tail


    def get_parent(self):
        parent = self.__parent
        # XXX happens just because of the unit test
        if parent is None:
            return None
        return _make_odf_element(parent)


    def is_text(self):
        return self.__is_text


    def is_tail(self):
        return self.__is_tail



class odf_element(object):
    """Representation of an XML element. Abstraction of the XML library
    behind.
    """

    def __init__(self, native_element, cache=None):
        if not isinstance(native_element, _Element):
            raise TypeError('"%s" is not an element node' %
                              type(native_element))
        self.__element = native_element
        if cache is not None:
            if len(cache) == 3:
                self._tmap, self._cmap, self._rmap = cache
            else:
                self._tmap, self._cmap = cache


    def __str__(self):
        return '%s "%s"' % (super(odf_element, self).__str__(),
                            self.get_tag())


    def _insert(self, element, before=None, after=None, position=0,
                main_text=False):
        """Insert an element before or after the characters in the text which
        match the regex before/after. When the regex matches more of one part
        of the text, position can be set to choice which part must be used. If
        before and after are None, we use only position that is the number of
        characters. If position is positive and before=after=None, we insert
        before the position character. But if position=-1, we insert after the
        last character.

        if main_text is True, filter out the annotations texts in computation.

        Arguments:

        element -- odf_element

        before -- unicode regex

        after -- unicode regex

        position -- int

        main_text -- boolean
        """
        current = self.__element
        element = element.__element

        if main_text:
            xpath_text = _xpath_text_main_descendant
        else:
            xpath_text = _xpath_text_descendant

        # 1) before xor after is not None
        if (before is not None) ^ (after is not None):
            if before is not None:
                regex = re.compile(before)
            else:
                regex = re.compile(after)

            # position = -1
            if position < 0:
                # Found the last text that matches the regex
                text = None
                for a_text in xpath_text(current):
                    if regex.search(a_text) is not None:
                        text = a_text
                if text is None:
                    raise ValueError("text not found")
                sre = list(regex.finditer(text))[-1]
            # position >= 0
            else:
                count = 0
                for text in xpath_text(current):
                    found_nb = len(regex.findall(text))
                    if found_nb + count >= position + 1:
                        break
                    count += found_nb
                else:
                    raise ValueError("text not found")
                sre = list(regex.finditer(text))[position - count]

            # Compute pos
            pos = sre.start() if before is not None else sre.end()
        # 2) before=after=None => only with position
        elif before is None and after is None:
            # Hack if position is negative => quickly
            if position < 0:
                current.append(element)
                return

            # Found the text
            count = 0
            for text in xpath_text(current):
                found_nb = len(text)
                if found_nb + count >= position:
                    break
                count += found_nb
            else:
                raise ValueError("text not found")

            # We insert before the character
            pos = position - count
        else:
            raise ValueError("bad combination of arguments")

        # Compute new texts
        text_before = text[:pos] if text[:pos] else None
        text_after  = text[pos:] if text[pos:] else None

        # Insert!
        parent = text.getparent()
        if text.is_text:
            parent.text = text_before
            element.tail = text_after
            parent.insert(0, element)
        else:
            parent.addnext(element)
            parent.tail = text_before
            element.tail = text_after


    def _insert_between(self, element, from_, to):
        """Insert the given empty element to wrap the text beginning with
        "from_" and ending with "to".

        Example 1: '<p>toto tata titi</p>

        We want to insert a link around "tata".

        Result 1: '<p>toto <a>tata</a> titi</p>

        Example 2: '<p><span>toto</span> tata titi</p>

        We want to insert a link around "tata".

        Result 2: '<p><span>toto</span> <a>tata</a> titi</p>

        Example 3: '<p>toto <span> tata </span> titi</p>'

        We want to insert a link from "tata" to "titi" included.

        Result 3: '<p>toto <span> </span>'
                  '<a><span>tata </span> titi</a></p>'

        Example 4: '<p>toto <span>tata titi</span> tutu</p>'

        We want to insert a link from "titi" to "tutu"

        Result 4: '<p>toto <span>tata </span><a><span>titi</span></a>'
                  '<a> tutu</a></p>'

        Example 5: '<p>toto <span>tata titi</span> '
                   '<span>tutu tyty</span></p>'

        We want to insert a link from "titi" to "tutu"

        Result 5: '<p>toto <span>tata </span><a><span>titi</span><a> '
                  '<a> <span>tutu</span></a><span> tyty</span></p>'
        """
        current = self.__element
        wrapper = element.__element
        for text in _xpath_text_descendant(current):
            if not from_ in text:
                continue
            from_index = text.index(from_)
            text_before = text[:from_index]
            text_after = text[from_index:]
            from_container = text.getparent()
            # Include from_index to match a single word
            to_index = text.find(to, from_index)
            if to_index >= 0:
                # Simple case: "from" and "to" in the same element
                to_end = to_index + len(to)
                if text.is_text:
                    from_container.text = text_before
                    wrapper.text = text[to_index:to_end]
                    wrapper.tail = text[to_end:]
                    from_container.insert(0, wrapper)
                else:
                    from_container.tail = text_before
                    wrapper.text = text[to_index:to_end]
                    wrapper.tail = text[to_end:]
                    parent = from_container.getparent()
                    index = parent.index(from_container)
                    parent.insert(index + 1, wrapper)
                return
            else:
                # Exit to the second part where we search for the end text
                break
        else:
            raise ValueError("start text not found")
        # The container is split in two
        container2 = deepcopy(from_container)
        if text.is_text:
            from_container.text = text_before
            from_container.tail = None
            container2.text = text_after
            from_container.tail = None
        else:
            from_container.tail = text_before
            container2.tail = text_after
        # Stack the copy into the surrounding element
        wrapper.append(container2)
        parent = from_container.getparent()
        index = parent.index(from_container)
        parent.insert(index + 1, wrapper)
        for text in _xpath_text_descendant(wrapper):
            if not to in text:
                continue
            to_end = text.index(to) + len(to)
            text_before = text[:to_end]
            text_after = text[to_end:]
            container_to = text.getparent()
            if text.is_text:
                container_to.text = text_before
                container_to.tail = text_after
            else:
                container_to.tail = text_before
                next_one = container_to.getnext()
                if next_one is None:
                    next_one = container_to.getparent()
                next_one.tail = text_after
            return
        raise ValueError("end text not found")


    def get_tag(self):
        """Return the tag name of the element as a qualified name, e.g.
        "text:span".

        Return: str
        """
        element = self.__element
        return _get_prefixed_name(element.tag)


    def _set_tag_raw(self, qname):
        element = self.__element
        element.tag = '{%s}%s' % _decode_qname(qname)

    def set_tag(self, qname):
        """Change the tag name of the element with the given qualified name.
        Return a new element as there may be a more appropriate class
        afterwards. XXX side effects?

        Arguments:

            qname -- str

        Return: odf_element or a subclass
        """
        element = self.__element
        element.tag = '{%s}%s' % _decode_qname(qname)
        return _make_odf_element(element)

    def elements_repeated_sequence(self, xpath_instance, name):
        uri, name = _decode_qname(name)
        if uri is not None:
            name = '{%s}%s' % (uri, name)
        element = self.__element
        sub_elements = xpath_instance(element)
        result = []
        idx = -1
        for sub_element in sub_elements:
            idx += 1
            value = sub_element.get(name)
            if value is None:
                result.append((idx, 1))
                continue
            try:
                value = int(value)
            except:
                value = 1
            result.append((idx, max(value, 1)))
        return result

    def get_elements(self, xpath_query):
        element = self.__element
        if isinstance(xpath_query, XPath):
            result = xpath_query(element)
        else:
            new_xpath_query = _find_query_in_cache(xpath_query)
            result = new_xpath_query(element)
        if hasattr(self, '_tmap'):
            if hasattr(self, '_rmap'):
                cache = (self._tmap, self._cmap, self._rmap)
            else:
                cache = (self._tmap, self._cmap)
        else:
            cache = None
        return [_make_odf_element(e, cache) for e in result]

    # fixme : need original get_element as wrapper of get_elements

    def get_element(self, xpath_query):
        element = self.__element
        result = element.xpath("(%s)[1]" % xpath_query, namespaces=ODF_NAMESPACES)
        if result:
            return _make_odf_element(result[0])
        return None

    def _get_element_idx(self, xpath_query, idx):
        element = self.__element
        result = element.xpath("(%s)[%s]" % (xpath_query, idx+1),
                               namespaces=ODF_NAMESPACES)
        if result:
            return _make_odf_element(result[0])
        return None

    def _get_element_idx2(self, xpath_instance, idx):
        element = self.__element
        result = xpath_instance(element, idx=idx+1)
        if result:
            return _make_odf_element(result[0])
        return None

    def get_attributes(self):
        attributes = {}
        element = self.__element
        for key, value in element.attrib.iteritems():
            attributes[_get_prefixed_name(key)] = value
        # FIXME lxml has mixed bytestring and unicode
        return attributes


    def get_attribute(self, name):
        element = self.__element
        uri, name = _decode_qname(name)
        if uri is not None:
            name = '{%s}%s' % (uri, name)
        value = element.get(name)
        if value is None:
            return None
        elif value in ('true', 'false'):
            return Boolean.decode(value)
        return unicode(value)


    def set_attribute(self, name, value):
        element = self.__element
        uri, name = _decode_qname(name)
        if uri is not None:
            name = '{%s}%s' % (uri, name)
        if type(value) is bool:
            value = Boolean.encode(value)
        elif value is None:
            try:
                del element.attrib[name]
            except KeyError:
                pass
            return
        element.set(name, value)


    def set_style_attribute(self, name, value):
        """Shortcut to accept a style object as a value.
        """
        if isinstance(value, odf_element):
            value = value.get_name()
        return self.set_attribute(name, value)


    def del_attribute(self, name):
        element = self.__element
        uri, name = _decode_qname(name)
        if uri is not None:
            name = '{%s}%s' % (uri, name)
        del element.attrib[name]


    def get_text(self, recursive=False):
        """Return the text content of the element.

        If recursive is True, all text contents of the subtree.
        """
        if recursive:
            return u''.join(self.__element.itertext())
        text = self.__element.text
        if text is None:
            return None
        return unicode(text)


    def set_text(self, text):
        """Set the text content of the element.
        """
        try:
            self.__element.text = text
        except TypeError:
            raise TypeError('unicode expected, not "%s"' % type(text))


    def get_tail(self):
        """Return the text immediately following the element.

        Inspired by lxml.
        """
        tail = self.__element.tail
        if tail is None:
            return None
        return unicode(tail)


    def set_tail(self, text):
        """Set the text immediately following the element.

        Inspired by lxml.
        """
        self.__element.tail = text


    def search(self, pattern):
        """Return the first position of the pattern in the text content of
        the element, or None if not found.

        Python regular expression syntax applies.

        Arguments:

            pattern -- unicode

        Return: int or None
        """
        if isinstance(pattern, str):
            # Fail properly if the pattern is an non-ascii bytestring
            pattern = unicode(pattern)
        text = self.get_text(recursive=True)
        match = re.search(pattern, text)
        if match is None:
            return None
        return match.start()


    def match(self, pattern):
        """return True if the pattern is found one or more times anywhere in
        the text content of the element.

        Python regular expression syntax applies.

        Arguments:

            pattern -- unicode

        Return: bool
        """
        return self.search(pattern) is not None


    def replace(self, pattern, new=None):
        """Replace the pattern with the given text, or delete if text is an
        empty string, and return the number of replacements. By default, only
        return the number of occurences that would be replaced.

        It cannot replace patterns found across several element, like a word
        split into two consecutive spans.

        Python regular expression syntax applies.

        Arguments:

            pattern -- unicode

            new -- unicode

        Return: int
        """
        if isinstance(pattern, str):
            # Fail properly if the pattern is an non-ascii bytestring
            pattern = unicode(pattern)
        cpattern = re.compile(pattern)
        count = 0
        for text in self.xpath('descendant::text()'):
            if new is None:
                count += len(cpattern.findall(text))
            else:
                new_text, number = cpattern.subn(new, text)
                container = text.get_parent()
                if text.is_text():
                    container.set_text(new_text)
                else:
                    container.set_tail(new_text)
                count += number
        return count


    def get_root(self):
        element = self.__element
        tree = element.getroottree()
        root = tree.getroot()
        return _make_odf_element(root)


    def get_parent(self):
        element = self.__element
        parent = element.getparent()
        if parent is None:
            # Already at root
            return None
        return _make_odf_element(parent)


    def get_next_sibling(self):
        element = self.__element
        next_one = element.getnext()
        if next_one is None:
            return None
        return _make_odf_element(next_one)


    def get_prev_sibling(self):
        element = self.__element
        prev = element.getprevious()
        if prev is None:
            return None
        return _make_odf_element(prev)


    def get_children(self):
        element = self.__element
        return [_make_odf_element(e) for e in element.getchildren()]


    def index(self, child):
        """Return the position of the child in this element.

        Inspired by lxml
        """
        return self.__element.index(child.__element)


    def get_text_content(self):
        """Like "get_text" but return the text of the embedded paragraph:
        annotations, cells...
        """
        text = []
        for child in self.get_elements('descendant::text:p'):
            text.append(child.get_text(recursive=True))
        return u"\n".join(text)


    def _erase_text_content(self):
        paragraphs = self.get_elements('text:p')
        if not paragraphs:
            # E.g., text:p in draw:text-box in draw:frame
            paragraphs = self.get_elements('*/text:p')
        if paragraphs:
            paragraphs.pop(0)
            for obsolete in paragraphs:
                obsolete.delete()


    def set_text_content(self, text):
        """Like "set_text" but set the text of the embedded paragraph:
        annotations, cells...

        Create the paragraph if missing.
        """
        paragraphs = self.get_elements('text:p')
        if not paragraphs:
            # E.g., text:p in draw:text-box in draw:frame
            paragraphs = self.get_elements('*/text:p')
        if paragraphs:
            paragraph = paragraphs.pop(0)
            for obsolete in paragraphs:
                obsolete.delete()
        else:
            paragraph = odf_create_element('text:p')
            self.insert(paragraph, FIRST_CHILD)
        # As "get_text_content" returned all text nodes, "set_text_content"
        # will overwrite all text nodes and children that may contain them
        element = paragraph.__element
        # Clear but the attributes
        del element[:]
        element.text = text


    def is_empty(self):
        """Check if the element is empty : no text, no children, no tail

        Return: Boolean
        """
        element = self.__element
        if element.tail is not None:
            return False
        if element.text is not None:
            return False
        if element.getchildren():
            return False
        return True


    def _get_successor(self, target):
        element = self.__element
        next_one = element.getnext()
        if next_one is not None:
            return _make_odf_element(next_one), target
        parent = self.get_parent()
        if parent is None:
            return None, None
        return parent._get_successor(target.get_parent())


    def _get_between_base(self, tag1, tag2):
        def find_any_id(tag):
            stag = tag.get_tag()
            for attribute in ('text:id', 'text:change-id', 'text:name',
                              'office:name', 'text:ref-name', 'xml:id'):
                idx = tag.get_attribute(attribute)
                if idx is not None:
                    return stag, attribute, idx
            raise ValueError('No Id found in %s' % tag.serialize())

        def common_ancestor(t1, a1, v1, t2, a2, v2):
            root = self.get_root()
            request1 = 'descendant::%s[@%s="%s"]' % (t1, a1, v1)
            request2 = 'descendant::%s[@%s="%s"]' % (t2, a2, v2)
            up = root.xpath(request1)[0]
            while True:
                #print "up",
                up = up.get_parent()
                has_tag2 = up.xpath(request2)
                if not has_tag2:
                    continue
                #print 'found'
                break
            #print up.serialize()
            return up

        t1, a1, v1 = find_any_id(tag1)
        t2, a2, v2 = find_any_id(tag2)
        ancestor = common_ancestor(t1, a1, v1, t2, a2, v2).clone()
        r1 = '%s[@%s="%s"]' % (t1, a1, v1)
        r2 = '%s[@%s="%s"]' % (t2, a2, v2)
        resu = ancestor.clone()
        for child in resu.get_children():
            resu.delete(child)
        resu.set_text(None)
        resu.set_tail(None)
        target = resu
        current = ancestor.get_children()[0]
        state = 0
        while True:
            #print 'current', state, current.serialize()
            if state == 0:  # before tag 1
                if current.xpath('descendant-or-self::%s' % r1):
                    if current.xpath('self::%s' % r1):
                        tail = current.get_tail()
                        if tail:
                            # got a tail => the parent should be either t:p or t:h
                            target.set_text(tail)
                        current, target = current._get_successor(target)
                        state = 1
                        continue
                    # got T1 in chidren, need further analysis
                    new_target = current.clone()
                    for child in new_target.get_children():
                        new_target.delete(child)
                    new_target.set_text(None)
                    new_target.set_tail(None)
                    target.append(new_target)
                    target = new_target
                    current = current.get_children()[0]
                    continue
                else:
                    # before tag1 : forget element, go to next one
                    current, target = current._get_successor(target)
                    continue
            elif state == 1:    # collect elements
                further = False
                if current.xpath('descendant-or-self::%s' % r2):
                    if current.xpath('self::%s' % r2):
                        # end of trip
                        break
                    # got T2 in chidren, need further analysis
                    further = True
                # further analysis needed :
                if further:
                    new_target = current.clone()
                    for child in new_target.get_children():
                        new_target.delete(child)
                    new_target.set_text(None)
                    new_target.set_tail(None)
                    target.append(new_target)
                    target = new_target
                    current = current.get_children()[0]
                    continue
                # collect
                target.append(current.clone())
                current, target = current._get_successor(target)
                continue
        # Now resu should be the "parent" of inserted parts
        # - a text:h or text:p sigle item (simple case)
        # - a upper element, with some text:p, text:h in it => need to be
        #   stripped to have a list of text:p, text:h
        if resu.get_tag() in ('text:p', 'text:h'):
            inner = [resu]
        else:
            inner = resu.get_children()
        return inner


    def get_between(self, tag1, tag2, as_text=False, clean=True,
                    no_header=True):
        """Returns elements between tag1 and tag2, tag1 and tag2 shall
        be unique and having an id attribute.
        (WARN: buggy if tag1/tag2 defines a malformed odf xml.)
        If as_text is True: returns the text content.
        If clean is True: suppress unwanted tags (deletions marks, ...)
        If no_header is True: existing text:h are changed in text:p
        By default: returns a list of odf_element, cleaned and without headers.

        Implementation and standard retrictions:
        Only text:h and text:p sould be 'cut' by an insert tag, so inner parts
        of insert tags are:
            - any text:h, text:p or sub tag of these
            - some text, part of a parent text:h or text:p

        Arguments:

            tag1 -- odf_element

            tag2 -- odf_element

            as_text -- boolean

            clean -- boolean

            no_header -- boolean

        Return: list of odf_paragraph or odf_header
        """
        inner = self._get_between_base(tag1, tag2)
        if clean:
            clean_tags = ('text:change', 'text:change-start', 'text:change-end',
                          'text:reference-mark', 'text:reference-mark-start',
                          'text:reference-mark-end')
            request_self = ' | '.join(
                ['self::%s' % c for c in clean_tags])
            inner = [e for e in inner if not e.xpath(request_self)]
            request = ' | '.join(
                ['descendant::%s' % c for c in clean_tags])
            for element in inner:
                to_del = element.xpath(request)
                for e in to_del:
                    element.delete(e)
        if no_header:  # crude replace t:h by t:p
            new_inner = []
            for element in inner:
                if element.get_tag() == 'text:h':
                    children = element.get_children()
                    text = element.__element.text
                    para = odf_create_element('text:p')
                    para.set_text(text)
                    for c in children:
                        para.append(c)
                    new_inner.append(para)
                else:
                    new_inner.append(element)
            inner = new_inner
        if as_text:
            return '\n'.join(
                [e.get_formatted_text() for e in inner])
        else:
            return inner


    def insert(self, element, xmlposition=None, position=None, start=False):
        """Insert an element relatively to ourself.

        Insert either using DOM vocabulary or by numeric position.
        If text start is True, insert the element before any existing text.

        Position start at 0.

        Arguments:

            element -- odf_element

            xmlposition -- FIRST_CHILD, LAST_CHILD, NEXT_SIBLING
                           or PREV_SIBLING

            start -- Boolean

            position -- int
        """
        child_tag = element.get_tag()
        current = self.__element
        element = element.__element
        if start:
            text = current.text
            if text is not None:
                current.text = None
                tail = element.tail
                if tail is None:
                    tail = text
                else:
                    tail = tail + text
                element.tail = tail
            position = 0
        if position is not None:
            current.insert(position, element)
        elif xmlposition is FIRST_CHILD:
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
            raise ValueError("(xml)position must be defined")


    def extend(self, odf_elements):
        """Fast append elements at the end of ourself using extend.
        """
        if odf_elements:
            current = self.__element
            elements = [ element.__element for element in odf_elements]
            current.extend(elements)


    def append(self, unicode_or_element):
        """Insert element or text in the last position.
        """
        current = self.__element

        # Unicode ?
        if isinstance(unicode_or_element, unicode):
            # Has children ?
            children = current.getchildren()
            if children:
                # Append to tail of the last child
                last_child = children[-1]
                text = last_child.tail
                text = text if text is not None else u""
                text += unicode_or_element
                last_child.tail = text
            else:
                # Append to text of the element
                text = current.text
                text = text if text is not None else u""
                text += unicode_or_element
                current.text = text
        elif isinstance(unicode_or_element, odf_element):
            current.append(unicode_or_element.__element)
        else:
            raise TypeError('odf_element or unicode expected, not "%s"' % (
                    type(unicode_or_element)))


    def delete(self, child=None, keep_tail=True):
        """Delete the given element from the XML tree. If no element is given,
        "self" is deleted. The XML library may allow to continue to use an
        element now "orphan" as long as you have a reference to it.

        if keep_tail is True (default), the tail text is not erased.

        Arguments:

            child -- odf_element

            keep_tail -- boolean (default to True), True for most usages.
        """
        if child is None:
            parent = self.get_parent()
            if parent is None:
                info = self.serialize()
                raise ValueError("cannot delete the root element\n%s" % info)
            child = self
        else:
            parent = self
        if keep_tail and child.__element.tail is not None:
            current = child.__element
            tail = current.tail
            current.tail = None
            prev = current.getprevious()
            if prev is not None:
                if prev.tail is None:
                    prev.tail = tail
                else:
                    prev.tail += tail
            else:
                if parent.__element.text is None:
                    parent.__element.text = tail
                else:
                    parent.__element.text += tail
        parent.__element.remove(child.__element)


    def replace_element(self, old_element, new_element):
        """Replaces in place a sub element with the element passed as second
        argument.

        Warning : no clone for old element.
        """
        current = self.__element
        current.replace(old_element.__element, new_element.__element)


    def strip_elements(self, sub_elements):
        """Remove the tags of provided elements, keeping inner childs and text.

        Return : the striped element.

        Warning : no clone in sub_elements list.

        Arguments:

            sub_elements -- odf_element or list of odf_element
        """
        if not sub_elements:
            return self
        if isinstance(sub_elements, odf_element):
            sub_elements = (sub_elements,)
        for element in sub_elements:
            element._set_tag_raw('text:this-will-be-removed')
        strip = ('text:this-will-be-removed',)
        return self.strip_tags(strip=strip, default=None)


    def strip_tags(self, strip=None, protect=None, default='text:p'):
        """Remove the tags listed in strip, recursively, keeping inner childs
        and text. Tags listed in protect stop the removal one level depth. If
        the first level element is stripped, default is used to embed the
        content in the default element. If default is None and first level is
        striped, a list of text and children is returned. Return : the striped
        element.

        strip_tags should be used by on purpose methods (strip_span ...)
        (Method name taken from lxml).

        Arguments:

            strip -- iterable list of unicode odf tags, or None

            protect -- iterable list of unicode odf tags, or None

            default -- unicode odf tag, or None

        Return:

            odf_element or list.
        """
        if not strip:
            return self
        if not protect:
            protect = ()
        protected = False
        element, modified = odf_element._strip_tags(self, strip, protect,
                                                    protected)
        if modified:
            if type(element) == list and default:
                new = odf_create_element(default)
                for content in element:
                    if isinstance(content, odf_element):
                        new.append(content)
                    else:
                        new.set_text(content)
                element = new
        return element


    @staticmethod
    def _strip_tags(element, strip, protect, protected):
        """sub method for strip_tags()
        """
        copy = element.clone()
        modified = False
        children = []
        if protect and element.get_tag() in protect:
            protect_below = True
        else:
            protect_below = False
        for child in copy.get_children():
            striped_child, is_modified = odf_element._strip_tags(
                child, strip, protect, protect_below)
            if is_modified:
                modified = True
            if type(striped_child) == list:
                children.extend(striped_child)
            else:
                children.append(striped_child)
        if not protected and strip and element.get_tag() in strip:
            element = []
            modified = True
        else:
            if not modified:
                return (element, False)
            element.clear()
            try:
                for key, value in copy.get_attributes().iteritems():
                    element.set_attribute(key, value)
            except ValueError:
                sys.stderr.write("strip_tags(): bad attribute in %s\n" % copy)
        text = copy.get_text()
        tail = copy.get_tail()
        if text is not None:
            element.append(text)
        for child in children:
            element.append(child)
        if tail is not None:
            if type(element) == list:
                element.append(tail)
            else:
                element.set_tail(tail)
        return (element, True)


    def xpath(self, xpath_query):
        """Apply XPath query to the element and its subtree. Return list of
        odf_element or odf_text instances translated from the nodes found.
        """
        element = self.__element
        xpath_instance = _find_query_in_cache(xpath_query)
        elements = xpath_instance(element)
        result = []
        for obj in elements:
            if (type(obj) is _ElementStringResult or
                    type(obj) is _ElementUnicodeResult):
                result.append(odf_text(obj))
            elif type(obj) is _Element:
                result.append(_make_odf_element(obj))
            else:
                result.append(obj)
        return result


    def clear(self):
        """Remove text, children and attributes from the element.
        """
        self.__element.clear()
        if hasattr(self, '_tmap'):
            self._tmap = []
        if hasattr(self, '_cmap'):
            self._cmap = []
        if hasattr(self, '_rmap'):
            self._rmap = []
        if hasattr(self, '_indexes'):
            remember = False
            if '_rmap' in self._indexes:
                remember = True
            self._indexes = {}
            self._indexes['_cmap'] = {}
            self._indexes['_tmap'] = {}
            if remember:
                self._indexes['_rmap'] = {}


    def clone(self):
        clone = deepcopy(self.__element)
        # Now the clone is its own root and lxml lost unused namespace
        # prefixes.
        # Re-attach it to a root with all namespaces
        root = Element('ROOT', nsmap=ODF_NAMESPACES)
        root.append(clone)
        if hasattr(self, '_tmap'):
            if hasattr(self, '_rmap'):
                return self.__class__(clone, (self._tmap[:], self._cmap[:],
                                              self._rmap[:]))
            else:
                return self.__class__(clone, (self._tmap[:], self._cmap[:]))
        return self.__class__(clone)


    def serialize(self, pretty=False, with_ns=False):
        # This copy bypasses serialization side-effects in lxml
        element = deepcopy(self.__element)
        data = tostring(element, with_tail=False,
                pretty_print=pretty)
        if not with_ns:
            # Remove namespaces
            data = ns_stripper.sub('', data)
        return data


    #
    # Element helpers usable from any context
    #

    def get_document_body(self):
        """Return the document body : 'office:body'
        """
        return self.get_element('//office:body/*[1]')


    def replace_document_body(self, new_body):
        """Change in place the full document body content.
        """
        body = self.get_document_body()
        tail = body.get_tail()
        body.clear()
        for item in new_body.get_children():
            body.append(item)
        if tail:
            body.set_tail(tail)


    def get_formatted_text(self, context):
        """This function must return a beautiful version of the text
        """
        return u''


    def get_styled_elements(self, name=True):
        """Brute-force to find paragraphs, tables, etc. using the given style
        name (or all by default).

        Arguments:

            name -- unicode

        Return: list
        """
        # FIXME incomplete (and possibly inaccurate)
        return (  _get_elements(self, 'descendant::*', text_style=name)
                + _get_elements(self, 'descendant::*', draw_style=name)
                + _get_elements(self, 'descendant::*', draw_text_style=name)
                + _get_elements(self, 'descendant::*', table_style=name)
                + _get_elements(self, 'descendant::*', page_layout=name)
                + _get_elements(self, 'descendant::*', master_page=name)
                + _get_elements(self, 'descendant::*', parent_style=name))

    #
    # Common attributes
    #

    def get_outline_level(self):
        outline_level = self.get_attribute('text:outline-level')
        if outline_level is None:
            return None
        return int(outline_level)


    def set_outline_level(self, outline_level):
        if outline_level is None:
            return self.set_attribute('text:outline-level', outline_level)
        return self.set_attribute('text:outline-level', str(outline_level))


    def _get_inner_text(self, tag):
        element = self.get_element(tag)
        if element is None:
            return None
        return element.get_text()


    def _set_inner_text(self, tag, text):
        element = self.get_element(tag)
        if element is None:
            element = odf_create_element(tag)
            self.append(element)
        element.set_text(text)


    #
    # Dublin core
    #

    def get_dc_creator(self):
        """Get dc:creator value.

        Return: unicode (or None if inexistant)
        """
        return self._get_inner_text('dc:creator')


    def set_dc_creator(self, creator):
        """Set dc:creator value.

        Arguments:

            creator -- unicode
        """
        return self._set_inner_text('dc:creator', creator)


    def get_dc_date(self):
        """Get the dc:date value.

        Return: datetime (or None if inexistant)
        """
        date = self._get_inner_text('dc:date')
        if date is None:
            return None
        return DateTime.decode(date)


    def set_dc_date(self, date):
        """Set the dc:date value.

        Arguments:

            darz -- DateTime
        """
        return self._set_inner_text('dc:date', DateTime.encode(date))


    #
    # SVG
    #

    def get_svg_title(self):
        return self._get_inner_text('svg:title')


    def set_svg_title(self, title):
        return self._set_inner_text('svg:title', title)


    def get_svg_description(self):
        return self._get_inner_text('svg:desc')


    def set_svg_description(self, description):
        return self._set_inner_text('svg:desc', description)


    #
    # Sections
    #

    def get_sections(self, style=None, content=None):
        """Return all the sections that match the criteria.

        Arguments:

            style -- unicode

            content -- unicode regex

        Return: list of odf_element
        """
        return _get_elements(self, 'text:section', text_style=style,
                content=content)


    def get_section(self, position=0, content=None):
        """Return the section that matches the criteria.

        Arguments:

            position -- int

            content -- unicode regex

        Return: odf_element or None if not found
        """
        return _get_element(self, 'descendant::text:section', position,
                content=content)


    #
    # Paragraphs
    #

    def get_paragraphs(self, style=None, content=None):
        """Return all the paragraphs that match the criteria.

        Arguments:

            style -- unicode

            content -- unicode regex

        Return: list of odf_paragraph
        """
        return _get_elements(self, 'descendant::text:p', text_style=style,
                content=content)


    def get_paragraph(self, position=0, content=None):
        """Return the paragraph that matches the criteria.

        Arguments:

            position -- int

            content -- unicode regex

        Return: odf_paragraph or None if not found
        """
        return _get_element(self, 'descendant::text:p', position,
                content=content)


    #
    # Span
    #

    def get_spans(self, style=None, content=None):
        """Return all the spans that match the criteria.

        Arguments:

            style -- unicode

            content -- unicode regex

        Return: list of odf_span
        """
        return _get_elements(self, 'descendant::text:span', text_style=style,
                content=content)


    def get_span(self, position=0, content=None):
        """Return the span that matches the criteria.

        Arguments:

            position -- int

            content -- unicode regex

        Return: odf_span or None if not found
        """
        return _get_element(self, 'descendant::text:span', position,
                content=content)


    #
    # Headings
    #

    def get_headings(self, style=None, outline_level=None, content=None):
        """Return all the headings that match the criteria.

        Arguments:

            style -- unicode

            content -- unicode regex

        Return: list of odf_heading
        """
        return _get_elements(self, 'descendant::text:h', text_style=style,
                outline_level=outline_level, content=content)


    def get_heading(self, position=0, outline_level=None, content=None):
        """Return the heading that matches the criteria.

        Arguments:

            position -- int

            content -- unicode regex

        Return: odf_heading or None if not found
        """
        return _get_element(self, 'descendant::text:h', position,
                outline_level=outline_level, content=content)


    #
    # Lists
    #

    def get_lists(self, style=None, content=None):
        """Return all the lists that match the criteria.

        Arguments:

            style -- unicode

            content -- unicode regex

        Return: list of odf_list
        """
        return _get_elements(self, 'descendant::text:list', text_style=style,
                content=content)


    def get_list(self, position=0, content=None):
        """Return the list that matches the criteria.

        Arguments:

            position -- int

            content -- unicode regex

        Return: odf_list or None if not found
        """
        return _get_element(self, 'descendant::text:list', position,
                content=content)


    #
    # Frames
    #

    def get_frames(self, presentation_class=None, style=None, title=None,
            description=None, content=None):
        """Return all the frames that match the criteria.

        Arguments:

            style -- unicode

            title -- unicode regex

            description -- unicode regex

            content -- unicode regex

        Return: list of odf_frame
        """
        return _get_elements(self, 'descendant::draw:frame',
                presentation_class=presentation_class, draw_style=style,
                svg_title=title, svg_desc=description, content=content)


    def get_frame(self, position=0, name=None,
            presentation_class=None, title=None, description=None,
            content=None):
        """Return the section that matches the criteria.

        Arguments:

            position -- int

            title -- unicode regex

            description -- unicode regex

            content -- unicode regex

        Return: odf_frame or None if not found
        """
        return _get_element(self, 'descendant::draw:frame', position,
                draw_name=name, presentation_class=presentation_class,
                svg_title=title, svg_desc=description, content=content)


    #
    # Images
    #

    def get_images(self, style=None, url=None, content=None):
        """Return all the sections that match the criteria.

        Arguments:

            style -- str

            url -- unicode regex

            content -- unicode regex

        Return: list of odf_element
        """
        return _get_elements(self, 'descendant::draw:image', text_style=style,
                url=url, content=content)


    def get_image(self, position=0, name=None, url=None, content=None):
        """Return the image that matches the criteria.

        Arguments:

            position -- int

            content -- unicode regex

        Return: odf_element or None if not found
        """
        # The frame is holding the name
        if name is not None:
            frame = _get_element(self, 'descendant::draw:frame',
                    position=position, draw_name=name)
            if frame is None:
                return None
            # The name is supposedly unique
            return frame.get_element('draw:image')
        return _get_element(self, 'descendant::draw:image', position,
                url=url, content=content)


    #
    # Tables
    #

    def get_tables(self, style=None, content=None):
        """Return all the tables that match the criteria.

        Arguments:

            style -- unicode

            content -- unicode regex

        Return: list of odf_table
        """
        return _get_elements(self, 'descendant::table:table',
                table_style=style, content=content)


    def get_table(self, position=0, name=None, content=None):
        """Return the table that matches the criteria.

        Arguments:

            position -- int

            name -- unicode

            content -- unicode regex

        Return: odf_table or None if not found
        """
        if name is None and content is None:
            result = self._get_element_idx('descendant::table:table', position)
        else :
            result = _get_element(self, 'descendant::table:table', position,
                table_name=name, content=content)
        return result

    #
    # Named Range
    #

    def get_named_ranges(self):
        """Return all the tables named ranges.

        Return: list of odf_named_range
        """
        named_ranges = self.get_elements(
                        'descendant::table:named-expressions/table:named-range')
        return named_ranges


    def get_named_range(self, name):
        """Return the named range of specified name, or None if not found.

        Arguments:

            name -- str

        Return: odf_named_range
        """
        named_range = self.get_elements(
        'descendant::table:named-expressions/table:named-range[@table:name="%s"][1]' % name)
        if named_range:
            return named_range[0]
        else:
            return None


    def append_named_range(self, named_range):
        """Append the named range to the spreadsheet, replacing existing named
        range of same name if any.

        Arguments:

            named_range -- ODF named nange
        """
        if self.get_tag() != 'office:spreadsheet':
            raise ValueError("Element is no 'office:spreadsheet' : %s" %
                             self.get_tag())
        named_expressions = self.get_element('table:named-expressions')
        if not named_expressions:
            named_expressions = odf_create_element('table:named-expressions')
            self.append(named_expressions)
        # exists ?
        current = named_expressions.get_element(
            'table:named-range[@table:name="%s"][1]' % named_range.name)
        if current:
            named_expressions.delete(current)
        named_expressions.append(named_range)


    def delete_named_range(self, name):
        """Delete the Named Range of specified name from the spreadsheet.

        Arguments:

            name -- str
        """
        if self.get_tag() != 'office:spreadsheet':
            raise ValueError("Element is no 'office:spreadsheet' : %s" %
                             self.get_tag())
        named_range = self.get_named_range(name)
        if not named_range:
            return
        named_range.delete()
        named_expressions = self.get_element('table:named-expressions')
        element = named_expressions.__element
        children = len(element.getchildren())
        if not children:
            self.delete(named_expressions)

    #
    # Notes
    #

    def get_notes(self, note_class=None, content=None):
        """Return all the notes that match the criteria.

        Arguments:

            note_class -- 'footnote' or 'endnote'

            content -- unicode regex

        Return: list of odf_note
        """
        return _get_elements(self, 'descendant::text:note',
                note_class=note_class, content=content)


    def get_note(self, position=0, note_id=None, note_class=None,
            content=None):
        """Return the note that matches the criteria.

        Arguments:

            position -- int

            note_id -- unicode

            note_class -- 'footnote' or 'endnote'

            content -- unicode regex

        Return: odf_note or None if not found
        """
        return _get_element(self, 'descendant::text:note', position,
                text_id=note_id, note_class=note_class, content=content)


    #
    # Annotations
    #

    def get_annotations(self, creator=None, start_date=None,
            end_date=None, content=None):
        """Return all the annotations that match the criteria.

        Arguments:

            creator -- unicode

            start_date -- date object

            end_date -- date object

            content -- unicode regex

        Return: list of odf_annotation
        """
        annotations = []
        for annotation in _get_elements(self, 'descendant::office:annotation',
                content=content):
            if (creator is not None
                    and creator != annotation.get_dc_creator()):
                continue
            date = annotation.get_dc_date()
            if start_date is not None and date < start_date:
                continue
            if end_date is not None and date >= end_date:
                continue
            annotations.append(annotation)
        return annotations


    def get_annotation(self, position=0, creator=None, start_date=None,
            end_date=None, content=None, name=None):
        """Return the annotation that matches the criteria.

        Arguments:

            position -- int

            creator -- unicode

            start_date -- date object

            end_date -- date object

            content -- unicode regex

            name -- unicode

        Return: odf_annotation or None if not found
        """
        if name is not None:
            return _get_element(self, 'descendant::office:annotation', 0,
                office_name=name)
        annotations = self.get_annotations(creator=creator,
                start_date=start_date, end_date=end_date, content=content)
        if not annotations:
            return None
        try:
            return annotations[position]
        except IndexError:
            return None


    def get_annotation_ends(self):
        """Return all the annotation ends.

        Return: list of odf_element
        """
        return _get_elements(self, 'descendant::office:annotation-end')


    def get_annotation_end(self, position=0, name=None):
        """Return the annotation end that matches the criteria.

        Arguments:

            position -- int

            name -- unicode

        Return: odf_element or None if not found
        """
        return _get_element(self, 'descendant::office:annotation-end', position,
                office_name=name)


    #
    # office:names
    #

    def get_office_names(self):
        """Return all the used office:name tags values of the element.

        Return: list of unique str
        """
        name_xpath_query = _find_query_in_cache('//@office:name')
        names = name_xpath_query(self.__element)
        uniq_names = list(set(names))
        return uniq_names


    #
    # Variables
    #

    def get_variable_decls(self):
        """Return the container for variable declarations. Created if not
        found.

        Return: odf_element
        """
        variable_decls = self.get_element('//text:variable-decls')
        if variable_decls is None:
            body = self.get_document_body()
            body.insert(odf_create_element('text:variable-decls'), FIRST_CHILD)
            variable_decls = body.get_element('//text:variable-decls')

        return variable_decls


    def get_variable_decl_list(self):
        """Return all the variable declarations.

        Return: list of odf_element
        """
        return _get_elements(self, 'descendant::text:variable-decl')


    def get_variable_decl(self, name, position=0):
        """return the variable declaration for the given name.

        return: odf_element or none if not found
        """
        return _get_element(self, 'descendant::text:variable-decl', position,
                text_name=name)


    def get_variable_sets(self, name=None):
        """Return all the variable sets that match the criteria.

        Arguments:

            name -- unicode

        Return: list of odf_element
        """
        return _get_elements(self, 'descendant::text:variable-set',
                text_name=name)


    def get_variable_set(self, name, position=-1):
        """Return the variable set for the given name (last one by default).

        Arguments:

            name -- unicode

            position -- int

        Return: odf_element or None if not found
        """
        return _get_element(self, 'descendant::text:variable-set', position,
                text_name=name)


    def get_variable_set_value(self, name, value_type=None):
        """Return the last value of the given variable name.

        Arguments:

            name -- unicode

            value_type -- 'boolean', 'currency', 'date', 'float',
                          'percentage', 'string', 'time' or automatic

        Return: most appropriate Python type
        """
        variable_set = self.get_variable_set(name)
        if not variable_set:
            return None
        return get_value(variable_set, value_type)


    #
    # User fields
    #

    def get_user_field_decls(self):
        """Return the container for user field declarations. Created if not
        found.

        Return: odf_element
        """
        user_field_decls = self.get_element('//text:user-field-decls')
        if user_field_decls is None:
            body = self.get_document_body()
            body.insert(odf_create_element('text:user-field-decls'),
                        FIRST_CHILD)
            user_field_decls = body.get_element('//text:user-field-decls')

        return user_field_decls


    def get_user_field_decl_list(self):
        """Return all the user field declarations.

        Return: list of odf_element
        """
        return _get_elements(self, 'descendant::text:user-field-decl')


    def get_user_field_decl(self, name, position=0):
        """return the user field declaration for the given name.

        return: odf_element or none if not found
        """
        return _get_element(self, 'descendant::text:user-field-decl',
                position, text_name=name)


    def get_user_field_value(self, name, value_type=None):
        """Return the value of the given user field name.

        Arguments:

            name -- unicode

            value_type -- 'boolean', 'currency', 'date', 'float',
                          'percentage', 'string', 'time' or automatic

        Return: most appropriate Python type
        """
        user_field_decl = self.get_user_field_decl(name)
        if user_field_decl is None:
            return None
        return get_value(user_field_decl, value_type)


    #
    # User defined fields
    # They are fields who should contain a copy of a user defined medtadata

    def get_user_defined_list(self):
        """Return all the user defined field declarations.

        Return: list of odf_element
        """
        return _get_elements(self, 'descendant::text:user-defined')


    def get_user_defined(self, name, position=0):
        """return the user defined declaration for the given name.

        return: odf_element or none if not found
        """
        return _get_element(self, 'descendant::text:user-defined',
                position, text_name=name)


    def get_user_defined_value(self, name, value_type=None):
        """Return the value of the given user defined field name.

        Arguments:

            name -- unicode

            value_type -- 'boolean', 'date', 'float',
                          'string', 'time' or automatic

        Return: most appropriate Python type
        """
        user_defined = self.get_user_defined(name)
        if user_defined is None:
            return None
        return get_value(user_defined, value_type)


    #
    # Draw Pages
    #

    def get_draw_pages(self, style=None, content=None):
        """Return all the draw pages that match the criteria.

        Arguments:

            style -- unicode

            content -- unicode regex

        Return: list of odf_draw_page
        """
        return _get_elements(self, 'descendant::draw:page', draw_style=style,
                content=content)


    def get_draw_page(self, position=0, name=None, content=None):
        """Return the draw page that matches the criteria.

        Arguments:

            position -- int

            name -- unicode

            content -- unicode regex

        Return: odf_draw_page or None if not found
        """
        return _get_element(self, 'descendant::draw:page', position,
                draw_name=name, content=content)


    #
    # Links
    #

    def get_links(self, name=None, title=None, url=None, content=None):
        """Return all the links that match the criteria.

        Arguments:

            name -- unicode

            title -- unicode

            url -- unicode regex

            content -- unicode regex

        Return: list of odf_element
        """
        return _get_elements(self, 'descendant::text:a', office_name=name,
                office_title=title, url=url, content=content)


    def get_link(self, position=0, name=None, title=None, url=None,
            content=None):
        """Return the link that matches the criteria.

        Arguments:

            position -- int

            name -- unicode

            title -- unicode

            url -- unicode regex

            content -- unicode regex

        Return: odf_element or None if not found
        """
        return _get_element(self, 'descendant::text:a', position,
                office_name=name, office_title=title, url=url,
                content=content)


    #
    # Bookmarks
    #

    def get_bookmarks(self):
        """Return all the bookmarks.

        Return: list of odf_element
        """
        return _get_elements(self, 'descendant::text:bookmark')


    def get_bookmark(self, position=0, name=None):
        """Return the bookmark that matches the criteria.

        Arguments:

            position -- int

            name -- unicode

        Return: odf_element or None if not found
        """
        return _get_element(self, 'descendant::text:bookmark', position,
                text_name=name)


    def get_bookmark_starts(self):
        """Return all the bookmark starts.

        Return: list of odf_element
        """
        return _get_elements(self, 'descendant::text:bookmark-start')


    def get_bookmark_start(self, position=0, name=None):
        """Return the bookmark start that matches the criteria.

        Arguments:

            position -- int

            name -- unicode

        Return: odf_element or None if not found
        """
        return _get_element(self, 'descendant::text:bookmark-start',
                position, text_name=name)


    def get_bookmark_ends(self):
        """Return all the bookmark ends.

        Return: list of odf_element
        """
        return _get_elements(self, 'descendant::text:bookmark-end')


    def get_bookmark_end(self, position=0, name=None):
        """Return the bookmark end that matches the criteria.

        Arguments:

            position -- int

            name -- unicode

        Return: odf_element or None if not found
        """
        return _get_element(self, 'descendant::text:bookmark-end', position,
                text_name=name)


    #
    # Reference marks
    #

    def get_reference_marks_single(self):
        """Return all the reference marks. Search only the tags
        text:reference-mark.
        Consider using : get_reference_marks()

        Return: list of odf_element
        """
        return _get_elements(self, 'descendant::text:reference-mark')


    def get_reference_mark_single(self, position=0, name=None):
        """Return the reference mark that matches the criteria. Search only the
        tags text:reference-mark.
        Consider using : get_reference_mark()

        Arguments:

            position -- int

            name -- unicode

        Return: odf_element or None if not found
        """
        return _get_element(self, 'descendant::text:reference-mark',
                position, text_name=name)


    def get_reference_mark_starts(self):
        """Return all the reference mark starts. Search only the tags
        text:reference-mark-start.
        Consider using : get_reference_marks()

        Return: list of odf_element
        """
        return _get_elements(self, 'descendant::text:reference-mark-start')


    def get_reference_mark_start(self, position=0, name=None):
        """Return the reference mark start that matches the criteria. Search
        only the tags text:reference-mark-start.
        Consider using : get_reference_mark()

        Arguments:

            position -- int

            name -- unicode

        Return: odf_element or None if not found
        """
        return _get_element(self, 'descendant::text:reference-mark-start',
                position, text_name=name)


    def get_reference_mark_ends(self):
        """Return all the reference mark ends. Search only the tags
        text:reference-mark-end.
        Consider using : get_reference_marks()

        Return: list of odf_element
        """
        return _get_elements(self, 'descendant::text:reference-mark-end')


    def get_reference_mark_end(self, position=0, name=None):
        """Return the reference mark end that matches the criteria. Search only
        the tags text:reference-mark-end.
        Consider using : get_reference_marks()

        Arguments:

            position -- int

            name -- unicode

        Return: odf_element or None if not found
        """
        return _get_element(self, 'descendant::text:reference-mark-end',
                position, text_name=name)


    def get_reference_marks(self):
        """Return all the reference marks, either single position reference
        (text:reference-mark) or start of range reference
        (text:reference-mark-start).

        Return: list of odf_element
        """
        request = ('descendant::text:reference-mark-start '
                   '| descendant::text:reference-mark')
        return _get_elements(self, request)


    def get_reference_mark(self, position=0, name=None):
        """Return the reference mark that match the criteria. Either single
        position reference mark (text:reference-mark) or start of range
        reference (text:reference-mark-start).

        Arguments:

            position -- int

            name -- unicode

        Return: odf_element or None if not found
        """
        if name:
            request = ('descendant::text:reference-mark-start[@text:name="%s"] '
                   '| descendant::text:reference-mark[@text:name="%s"]') % (
                                                                    name, name)

            return _get_element(self, request, position=0)
        else:
            request = ('descendant::text:reference-mark-start '
                   '| descendant::text:reference-mark')
            return _get_element(self, request, position)


    def get_references(self, name=None):
        """Return all the references (text:reference-ref). If name is
        provided, returns the references of that name.

        Return: list of odf_element

        Arguments:

            name -- unicode or None
        """
        if name is None:
            return _get_elements(self, 'descendant::text:reference-ref')
        request = 'descendant::text:reference-ref[@text:ref-name="%s"]' % name
        return _get_elements(self, request)


    #
    # Shapes elements
    #

    #
    # Groups
    #

    def get_draw_groups(self, title=None, description=None, content=None):
        return _get_elements(self, 'descendant::draw:g', svg_title=title,
                svg_desc=description, content=content)


    def get_draw_group(self, position=0, name=None, title=None,
            description=None, content=None):
        return _get_element(self, 'descendant::draw:g', position,
                draw_name=name, svg_title=title, svg_desc=description,
                content=content)


    #
    # Lines
    #

    def get_draw_lines(self, draw_style=None, draw_text_style=None,
            content=None):
        """Return all the draw lines that match the criteria.

        Arguments:

            draw_style -- unicode

            draw_text_style -- unicode

            content -- unicode regex

        Return: list of odf_shape
        """
        return _get_elements(self, 'descendant::draw:line',
                draw_style=draw_style, draw_text_style=draw_text_style,
                content=content)


    def get_draw_line(self, position=0, id=None, content=None):
        """Return the draw line that matches the criteria.

        Arguments:

            position -- int

            id -- unicode

            content -- unicode regex

        Return: odf_shape or None if not found
        """
        return _get_element(self, 'descendant::draw:line', position,
                draw_id=id, content=content)


    #
    # Rectangles
    #

    def get_draw_rectangles(self, draw_style=None, draw_text_style=None,
            content=None):
        """Return all the draw rectangles that match the criteria.

        Arguments:

            draw_style -- unicode

            draw_text_style -- unicode

            content -- unicode regex

        Return: list of odf_shape
        """
        return _get_elements(self, 'descendant::draw:rect',
                draw_style=draw_style, draw_text_style=draw_text_style,
                content=content)


    def get_draw_rectangle(self, position=0, id=None, content=None):
        """Return the draw rectangle that matches the criteria.

        Arguments:

            position -- int

            id -- unicode

            content -- unicode regex

        Return: odf_shape or None if not found
        """
        return _get_element(self, 'descendant::draw:rect', position,
                draw_id=id, content=content)


    #
    # Ellipse
    #

    def get_draw_ellipses(self, draw_style=None, draw_text_style=None,
            content=None):
        """Return all the draw ellipses that match the criteria.

        Arguments:

            draw_style -- unicode

            draw_text_style -- unicode

            content -- unicode regex

        Return: list of odf_shape
        """
        return _get_elements(self, 'descendant::draw:ellipse',
                draw_style=draw_style, draw_text_style=draw_text_style,
                content=content)


    def get_draw_ellipse(self, position=0, id=None, content=None):
        """Return the draw ellipse that matches the criteria.

        Arguments:

            position -- int

            id -- unicode

            content -- unicode regex

        Return: odf_shape or None if not found
        """
        return _get_element(self, 'descendant::draw:ellipse', position,
                draw_id=id, content=content)


    #
    # Connectors
    #

    def get_draw_connectors(self, draw_style=None, draw_text_style=None,
            content=None):
        """Return all the draw connectors that match the criteria.

        Arguments:

            draw_style -- unicode

            draw_text_style -- unicode

            content -- unicode regex

        Return: list of odf_shape
        """
        return _get_elements(self, 'descendant::draw:connector',
                draw_style=draw_style, draw_text_style=draw_text_style,
                content=content)


    def get_draw_connector(self, position=0, id=None, content=None):
        """Return the draw connector that matches the criteria.

        Arguments:

            position -- int

            id -- unicode

            content -- unicode regex

        Return: odf_shape or None if not found
        """
        return _get_element(self, 'descendant::draw:connector', position,
                draw_id=id, content=content)


    def get_orphan_draw_connectors(self):
        """Return a list of connectors which don't have any shape connected
        to them.
        """
        connectors = []
        for connector in self.get_draw_connectors():
            start_shape = connector.get_attribute('draw:start-shape')
            end_shape = connector.get_attribute('draw:end-shape')
            if start_shape is None and end_shape is None:
                connectors.append(connector)
        return connectors


    #
    # Tracked changes and text change
    #

    def get_tracked_changes(self):
        """Return the tracked-changes part in the text body.
        """
        return self.get_element('//text:tracked-changes')


    def get_changes_ids(self):
        """Return a list of ids that refers to a change region in the tracked
        changes list.
        """
        # Insertion changes
        xpath_query = 'descendant::text:change-start/@text:change-id'
        # Deletion changes
        xpath_query += ' | descendant::text:change/@text:change-id'
        return self.xpath(xpath_query)


    def get_text_change_deletions(self):
        """Return all the text changes of deletion kind: the tags text:change.
        Consider using : get_text_changes()

        Return: list of odf_element
        """
        return _get_elements(self, 'descendant::text:text:change')


    def get_text_change_deletion(self, position=0, idx=None):
        """Return the text change of deletion kind that matches the criteria.
        Search only for the tags text:change.
        Consider using : get_text_change()

        Arguments:

            position -- int

            idx -- unicode

        Return: odf_element or None if not found
        """
        return _get_element(self, 'descendant::text:change',
                position, change_id=idx)


    def get_text_change_starts(self):
        """Return all the text change-start. Search only for the tags
        text:change-start.
        Consider using : get_text_changes()

        Return: list of odf_element
        """
        return _get_elements(self, 'descendant::text:change-start')


    def get_text_change_start(self, position=0, idx=None):
        """Return the text change-start that matches the criteria. Search
        only the tags text:change-start.
        Consider using : get_text_change()

        Arguments:

            position -- int

            idx -- unicode

        Return: odf_element or None if not found
        """
        return _get_element(self, 'descendant::text:change-start',
                position, change_id=idx)


    def get_text_change_ends(self):
        """Return all the text change-end. Search only the tags
        text:change-end.
        Consider using : get_text_changes()

        Return: list of odf_element
        """
        return _get_elements(self, 'descendant::text:change-end')


    def get_text_change_end(self, position=0, idx=None):
        """Return the text change-end that matches the criteria. Search only
        the tags text:change-end.
        Consider using : get_text_change()

        Arguments:

            position -- int

            idx -- unicode

        Return: odf_element or None if not found
        """
        return _get_element(self, 'descendant::text:change-end',
                position, change_id=idx)


    def get_text_changes(self):
        """Return all the text changes, either single deletion
        (text:change) or start of range of changes (text:change-start).

        Return: list of odf_element
        """
        request = ('descendant::text:change-start '
                   '| descendant::text:change')
        return _get_elements(self, request)


    def get_text_change(self, position=0, idx=None):
        """Return the text change that matches the criteria. Either single
        deletion (text:change) or start of range of changes (text:change-start).
        position : index of the element to retrieve if several matches, default
        is 0.
        idx : change-id of the element.

        Arguments:

            position -- int

            idx -- unicode

        Return: odf_element or None if not found
        """
        if idx:
            request = ('descendant::text:change-start[@text:change-id="%s"] '
            '| descendant::text:change[@text:change-id="%s"]') % (idx, idx)
            return _get_element(self, request, position=0)
        else:
            request = ('descendant::text:change-start '
                   '| descendant::text:change')
            return _get_element(self, request, position)


    #
    # Table Of Content
    #

    def get_tocs(self):
        """Return all the tables of contents.

        Return: list of odf_toc
        """
        return _get_elements(self, 'text:table-of-content')


    def get_toc(self, position=0, content=None):
        """Return the table of contents that matches the criteria.

        Arguments:

            position -- int

            content -- unicode regex

        Return: odf_toc or None if not found
        """
        return _get_element(self, 'text:table-of-content', position,
                content=content)


    #
    # Styles
    #
    @staticmethod
    def _get_style_tagname(family, is_default=False):
        """Widely match possible tag names given the family (or not).
        """
        if family is None:
            tagname = '(' + '|'.join(['style:default-style',
                '*[@style:name]', 'draw:fill-image', 'draw:marker']) + ')'
            famattr = None
        elif is_default is True:
            # Default style
            tagname = 'style:default-style'
            famattr = family
        else:
            tagname, famattr = _get_style_tagname(family)
            if famattr:
                # Include family default style
                tagname = '(%s|style:default-style)' % tagname
        return tagname, famattr


    def get_styles(self, family=None):
        # Both common and default styles
        tagname, famattr = self._get_style_tagname(family)
        return _get_elements(self, tagname, family=famattr)


    def get_style(self, family, name_or_element=None, display_name=None):
        """Return the style uniquely identified by the family/name pair. If
        the argument is already a style object, it will return it.

        If the name is not the internal name but the name you gave in the
        desktop application, use display_name instead.

        Arguments:

            family -- 'paragraph', 'text', 'graphic', 'table', 'list',
                      'number'

            name_or_element -- unicode or odf_style

            display_name -- unicode

        Return: odf_style or None if not found
        """
        if isinstance(name_or_element, odf_element):
            name = self.get_attribute('style:name')
            if name is not None:
                return name_or_element
            else:
                raise ValueError('Not a odf_style ?  %s' % name_or_element)
        style_name = name_or_element
        is_default = not (style_name or display_name)
        tagname, famattr = self._get_style_tagname(family,
                is_default=is_default)
        # famattr became None if no "style:family" attribute
        return _get_element(self, tagname, 0, style_name=style_name,
                display_name=display_name, family=famattr)
