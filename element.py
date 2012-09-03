# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Hervé Cauwelier <herve@itaapy.com>
#          Romain Gauthier <romain@itaapy.com>
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
from re import search, compile

# Import from lxml
from lxml.etree import fromstring, tostring, Element, _Element
from lxml.etree import _ElementStringResult, _ElementUnicodeResult
from lxml.etree import XPath

# Import from lpod
from datatype import DateTime, Boolean
from utils import _get_abspath, _get_elements, _get_element
from utils import _get_style_tagname, get_value  #, obsolete


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
}


FIRST_CHILD, LAST_CHILD, NEXT_SIBLING, PREV_SIBLING, STOPMARKER = range(5)


ns_stripper = compile(' xmlns:\w*="[\w:\-\/\.#]*"')

__xpath_query_cache = {}

# An empty XML document with all namespaces declared
ns_document_path = _get_abspath('templates/namespaces.xml')
file = open(ns_document_path, 'rb')
ns_document_data = file.read()
file.close()



def _decode_qname(qname):
    """Turn a prefixed name to a (uri, name) pair.
    """
    if ':' in qname:
        prefix, name = qname.split(':')
        try:
            uri = ODF_NAMESPACES[prefix]
        except KeyError:
            raise ValueError, "XML prefix '%s' is unknown" % prefix
        return uri, name
    return None, qname



def _uri_to_prefix(uri):
    """Find the prefix associated to the given URI.
    """
    for key, value in ODF_NAMESPACES.iteritems():
        if value == uri:
            return key
    raise ValueError, 'uri "%s" not found' % uri



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


_xpath_text = _find_query_in_cache("//text()")
_xpath_text_descendant = _find_query_in_cache("descendant::text()")
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
        raise ValueError,  'element "%s" already registered' % qname
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
        raise TypeError, "element data is not str or unicode"
    element_data = element_data.strip()
    if not element_data:
        raise ValueError, "element data is empty"
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
            raise TypeError, ('"%s" is not an element node' %
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


    def _insert(self, element, before=None, after=None, position=0):
        """Insert an element before or after the characters in the text which
        match the regex before/after. When the regex matches more of one part
        of the text, position can be set to choice which part must be used. If
        before and after are None, we use only position that is the number of
        characters. If position is positive and before=after=None, we insert
        before the position character. But if position=-1, we insert after the
        last character.

        Arguments:

        element -- odf_element

        before -- unicode regex

        after -- unicode regex

        position -- int
        """

        current = self.__element
        element = element.__element

        # 1) before xor after is not None
        if (before is not None) ^ (after is not None):
            regex = compile(before) if before is not None else compile(after)

            # position = -1
            if position < 0:
                # Found the last text that matches the regex
                text = None
                for a_text in _xpath_text(current):
                    if regex.search(a_text) is not None:
                        text = a_text
                if text is None:
                    raise ValueError, "text not found"
                sre = list(regex.finditer(text))[-1]
            # position >= 0
            else:
                count = 0
                for text in _xpath_text(current):
                    found_nb = len(regex.findall(text))
                    if found_nb + count >= position + 1:
                        break
                    count += found_nb
                else:
                    raise ValueError, "text not found"
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
            for text in _xpath_text(current):
                found_nb = len(text)
                if found_nb + count >= position:
                    break
                count += found_nb
            else:
                raise ValueError, "text not found"

            # We insert before the character
            pos = position - count
        else:
            raise ValueError, "bad combination of arguments"

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
            raise ValueError, "start text not found"
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
                next = container_to.getnext()
                if next is None:
                    next = container_to.getparent()
                next.tail = text_after
            return
        raise ValueError, "end text not found"


    def get_tag(self):
        """Return the tag name of the element as a qualified name, e.g.
        "text:span".

        Return: str
        """
        element = self.__element
        return _get_prefixed_name(element.tag)


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

    #get_element_list = obsolete('get_element_list', get_elements)

    # fixme : need original get_element as wrapper of get_elements

    def get_element(self, xpath_query):
        element = self.__element
        result = element.xpath("(%s)[1]" % xpath_query, namespaces=ODF_NAMESPACES)
        if result:
            return _make_odf_element(result[0])
        return None

    def get_element_idx(self, xpath_query, idx):
        element = self.__element
        result = element.xpath("(%s)[%s]" % (xpath_query, idx+1), namespaces=ODF_NAMESPACES)
        if result:
            return _make_odf_element(result[0])
        return None

    def get_element_idx2(self, xpath_instance, idx):
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
            raise TypeError, 'unicode expected, not "%s"' % type(text)


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
        match = search(pattern, text)
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
        pattern = compile(pattern)
        count = 0
        for text in self.xpath('descendant::text()'):
            if new is None:
                count += len(pattern.findall(text))
            else:
                new_text, number = pattern.subn(new, text)
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
        next = element.getnext()
        if next is None:
            return None
        return _make_odf_element(next)


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
            paragraph = paragraphs.pop(0)
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


    def insert(self, element, xmlposition=None, position=None):
        """Insert an element relatively to ourself.

        Insert either using DOM vocabulary or by numeric position.

        Position start at 0.

        Arguments:

            element -- odf_element

            xmlposition -- FIRST_CHILD, LAST_CHILD, NEXT_SIBLING
                           or PREV_SIBLING

            position -- int
        """
        current = self.__element
        element = element.__element
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
            raise ValueError, "(xml)position must be defined"


    def extend(self, odf_elements):
        """Fast append elements at the end of ourself using extend.
        """
        if odf_elements:
            current = self.__element
            elements = [ odf_element.__element for odf_element in odf_elements]
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
            raise TypeError, 'odf_element or unicode expected, not "%s"' % (
                    type(unicode_or_element))

    #append_element = obsolete('append_element', append)


    def delete(self, child=None):
        """Delete the given element from the XML tree. If no element is given,
        "self" is deleted. The XML library may allow to continue to use an
        element now "orphan" as long as you have a reference to it.

        Arguments:

            child -- odf_element
        """
        if child is None:
            parent = self.get_parent()
            if parent is None:
                raise ValueError, "cannot delete the root element"
            child = self
        else:
            parent = self
        parent.__element.remove(child.__element)


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
            self._indexes={}
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
                return self.__class__(clone, (self._tmap[:], self._cmap[:], self._rmap[:]))
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
        return self.get_element('//office:body/*[1]')


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
        return self._get_inner_text('dc:creator')


    def set_dc_creator(self, creator):
        return self._set_inner_text('dc:creator', creator)


    def get_dc_date(self):
        date = self._get_inner_text('dc:date')
        if date is None:
            return None
        return DateTime.decode(date)


    def set_dc_date(self, date):
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

    #get_section_list = obsolete('get_section_list', get_sections)


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

    #get_paragraph_list = obsolete('get_paragraph_list', get_paragraphs)


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

    #get_span_list = obsolete('get_span_list', get_spans)


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

    #get_heading_list = obsolete('get_heading_list', get_headings)


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

    #get_list_list = obsolete('get_list_list', get_lists)


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

    #get_frame_list = obsolete('get_frame_list', get_frames)


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

    #get_image_list = obsolete('get_image_list', get_images)


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

    #get_table_list = obsolete('get_table_list', get_tables)


    def get_table(self, position=0, name=None, content=None):
        """Return the table that matches the criteria.

        Arguments:

            position -- int

            name -- unicode

            content -- unicode regex

        Return: odf_table or None if not found
        """
        if name is None and content is None:
            result = self.get_element_idx('descendant::table:table', position)
        else :
            result = _get_element(self, 'descendant::table:table', position,
                table_name=name, content=content)
        return result


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

    #get_note_list = obsolete('get_note_list', get_notes)


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
        """Return all the sections that match the criteria.

        End date is not included (as expected in Python).

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

    #get_annotation_list = obsolete('get_annotation_list', get_annotations)


    def get_annotation(self, position=0, creator=None, start_date=None,
            end_date=None, content=None):
        """Return the section that matches the criteria.

        End date is not included (as expected in Python).

        Arguments:

            position -- int

            creator -- unicode

            start_date -- date object

            end_date -- date object

            content -- unicode regex

        Return: odf_annotation or None if not found
        """
        annotations = self.get_annotations(creator=creator,
                start_date=start_date, end_date=end_date, content=content)
        if not annotations:
            return None
        try:
            return annotations[position]
        except IndexError:
            return None


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
            from variable import odf_create_variable_decls
            body = self.get_document_body()
            body.insert(odf_create_variable_decls(), FIRST_CHILD)
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

    #get_variable_set_list = obsolete('get_variable_set_list',
    #        get_variable_sets)


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
            from variable import odf_create_user_field_decls
            body = self.get_document_body()
            body.insert(odf_create_user_field_decls(), FIRST_CHILD)
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

    #get_draw_page_list = obsolete('get_draw_page_list', get_draw_pages)


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

    #get_link_list = obsolete('get_link_list', get_links)


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

    #get_bookmark_list = obsolete('get_bookmark_list', get_bookmarks)


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

    #get_bookmark_start_list = obsolete('get_bookmark_start_list',
    #        get_bookmark_starts)


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

    #get_bookmark_end_list = obsolete('get_bookmark_end_list',
    #        get_bookmark_ends)


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

    def get_reference_marks(self):
        """Return all the reference marks.

        Return: list of odf_element
        """
        return _get_elements(self, 'descendant::text:reference-mark')

    #get_reference_mark_list = obsolete('get_reference_mark_list',
    #        get_reference_marks)


    def get_reference_mark(self, position=0, name=None):
        """Return the reference mark that matches the criteria.

        Arguments:

            position -- int

            name -- unicode

        Return: odf_element or None if not found
        """
        return _get_element(self, 'descendant::text:reference-mark',
                position, text_name=name)


    def get_reference_mark_starts(self):
        """Return all the reference mark starts.

        Return: list of odf_element
        """
        return _get_elements(self, 'descendant::text:reference-mark-start')

    #get_reference_mark_start_list = obsolete('get_reference_mark_start_list',
    #        get_reference_mark_starts)


    def get_reference_mark_start(self, position=0, name=None):
        """Return the reference mark start that matches the criteria.

        Arguments:

            position -- int

            name -- unicode

        Return: odf_element or None if not found
        """
        return _get_element(self, 'descendant::text:reference-mark-start',
                position, text_name=name)


    def get_reference_mark_ends(self):
        """Return all the reference mark ends.

        Return: list of odf_element
        """
        return _get_elements(self, 'descendant::text:reference-mark-end')

    #get_reference_mark_end_list = obsolete('get_reference_mark_end_list',
    #        get_reference_mark_ends)


    def get_reference_mark_end(self, position=0, name=None):
        """Return the reference mark end that matches the criteria.

        Arguments:

            position -- int

            name -- unicode

        Return: odf_element or None if not found
        """
        return _get_element(self, 'descendant::text:reference-mark-end',
                position, text_name=name)


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

    #get_draw_line_list = obsolete('get_draw_line_list', get_draw_lines)


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

    #get_draw_rectangle_list = obsolete('get_draw_rectangle_list',
    #        get_draw_rectangles)


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

    #get_draw_ellipse_list = obsolete('get_draw_ellipse_list',
    #        get_draw_ellipses)


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

    #get_draw_connector_list = obsolete('get_draw_connector_list',
    #        get_draw_connectors)


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
    # Tracked changes
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


    #
    # Table Of Content
    #

    def get_tocs(self):
        """Return all the tables of contents.

        Return: list of odf_toc
        """
        return _get_elements(self, 'text:table-of-content')

    #get_toc_list = obsolete('get_toc_list', get_tocs)


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

    def _get_style_tagname(self, family, is_default=False):
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

    #get_style_list = obsolete('get_style_list', get_styles)


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
        from style import odf_style

        if isinstance(name_or_element, odf_style):
            return name_or_element
        style_name = name_or_element
        is_default = not (style_name or display_name)
        tagname, famattr = self._get_style_tagname(family,
                is_default=is_default)
        # famattr became None if no "style:family" attribute
        return _get_element(self, tagname, 0, style_name=style_name,
                display_name=display_name, family=famattr)
