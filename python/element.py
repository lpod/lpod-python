# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from copy import deepcopy
from re import search, compile

# Import from lxml
from lxml.etree import fromstring, tostring, _Element
from lxml.etree import _ElementStringResult, _ElementUnicodeResult

# Import from lpod
from datatype import DateTime
from utils import _get_abspath, _get_element_list, _get_element
from utils import get_value, convert_unicode


ODF_NAMESPACES = {
    'office': "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    'style': "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    'text': "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    'presentation': "urn:oasis:names:tc:opendocument:xmlns:presentation:1.0",
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



class_registry = {}

def register_element_class(qname, cls):
    # Turn tag name into what lxml is expecting
    tag = '{%s}%s' % decode_qname(qname)
    if tag in class_registry:
        raise ValueError,  'element "%s" already registered' % qname
    class_registry[tag] = cls



def make_odf_element(native_element):
    cls = class_registry.get(native_element.tag,  odf_element)
    return cls(native_element)



def odf_create_element(element_data):
    if not isinstance(element_data, (str, unicode)):
        raise TypeError, "element data is not str/unicode"
    if not element_data.strip():
        raise ValueError, "element data is empty"
    element_data = convert_unicode(element_data)
    data = ns_document_data.format(element=element_data)
    root = fromstring(data)
    return make_odf_element(root[0])



class odf_element(object):
    """Representation of an XML element.
    Abstraction of the XML library behind.
    """

    def __init__(self, native_element):
        if not isinstance(native_element, _Element):
            raise TypeError, ('"%s" is not an element node' %
                              type(native_element))
        self.__element = native_element


    def __str__(self):
        return '%s "%s"' % (object.__str__(self), self.get_name())


    def _insert_after(self, element, text):
        """Insert the given element after the text snippet. Typically for
        inserting a footnote after a word.

        Example: '<p>toto<span>titi</span>tata</p>'
        We are in the context of a paragraph, we know it contains "titi", and
        we want to insert the footnote after it without having to know
        it is in a span.
        """
        current = self.__element
        element = element.__element
        for result in current.xpath('descendant::text()'):
            if text in result:
                index = result.index(text) + len(text)
                before = result[:index]
                after = result[index:]
                container = result.getparent()
                if result.is_text:
                    container.text = before
                    container.insert(0, element)
                    element.tail = after
                else:
                    container.tail = before
                    parent = container.getparent()
                    index = parent.index(container)
                    parent.insert(index + 1, element)
                    element.tail = after
                return
        raise ValueError, "text not found"


    # TODO rewrite specifically for span and a, and make private
    def wrap_text(self, element, offset=0, length=0):
        current = self.__element
        element = element.__element
        total = 0
        for text in current.xpath('descendant::text()'):
            total += len(text)
            if offset < total:
                left = text[:-(total - offset)]
                right = text[-(total - offset):]
                center, right = right[:length], right[length:]
                element.tail = right
                if center:
                    element.text = center
                if text.is_tail:
                    owner = text.getparent()
                    # Set text
                    owner.tail = left
                    # Insert element
                    index = current.index(owner)
                    current.insert(index + 1, element)
                    return
                else:
                    # Set text
                    current.text = left
                    # Insert element
                    current.insert(0, element)
                    return
        else:
            # offset is too big => insert at the end
            current.append(element)


    def get_name(self):
        element = self.__element
        return get_prefixed_name(element.tag)


    def get_element_list(self, xpath_query):
        element = self.__element
        result = element.xpath(xpath_query, namespaces=ODF_NAMESPACES)
        return [make_odf_element(e) for e in result]


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
        # FIXME lxml has mixed bytestring and unicode
        return attributes


    def get_attribute(self, name):
        element = self.__element
        uri, name = decode_qname(name)
        if uri is None:
            return element.get(name)
        value = element.get('{%s}%s' % (uri, name))
        if value is None:
            return None
        return unicode(value)


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
        """This function returns a "raw" version of the text
        """
        return u''.join(self.__element.itertext())


    def get_formated_text(self, context):
        """This function must return a beautiful version of the text
        """
        return u''


    def set_text(self, text, after=False):
        """If "after" is true, sets the text at the end of the element, not
        inside.
        FIXME maybe too specific to lxml, see at the end if disposable
        """
        element = self.__element
        if after:
            element.tail = text
        else:
            element.text = text


    def match(self, pattern):
        """ True if the text of the odf_element match one or more times the
        unicode pattern.
        """
        if isinstance(pattern, str):
            # Fail properly if the pattern is an non-ascii bytestring
            pattern = unicode(pattern)
        text = self.get_text()
        return search(pattern, text) is not None


    def get_parent(self):
        element = self.__element
        parent = element.getparent()
        if parent is None:
            # Already at root
            return None
        return make_odf_element(parent)


    def get_next_sibling(self):
        element = self.__element
        next = element.getnext()
        if next is None:
            return None
        return make_odf_element(next)


    def get_prev_sibling(self):
        element = self.__element
        prev = element.getprevious()
        if prev is None:
            return None
        return make_odf_element(prev)


    def get_children(self):
        element = self.__element
        return [make_odf_element(e) for e in element]


    def get_text_content(self):
        """Like "get_text" but applied to the embedded paragraph:
        annotations, cells...
        """
        element = self.__element
        text = element.xpath('string(text:p)', namespaces=ODF_NAMESPACES)
        return unicode(text)


    def set_text_content(self, text):
        """Like "set_text" but applied to the embedded paragraph:
        annotations, cells...
        """
        # Was made descendant for text:p in draw:text-box in draw:frame
        paragraph = self.get_element('descendant::text:p')
        if paragraph is None:
            paragraph = odf_create_element('<text:p/>')
            self.insert_element(paragraph, FIRST_CHILD)
        element = paragraph.__element
        element.clear()
        element.text = text


    def insert_element(self, element, xmlposition=None, position=None):
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
            raise ValueError, "xmlposition must be defined"


    def append_element(self, element):
        """Shortcut to insert at the end.
        """
        self.insert_element(element, LAST_CHILD)


    def xpath(self, xpath_query):
        element = self.__element
        elements = element.xpath(xpath_query, namespaces=ODF_NAMESPACES)
        result = []
        for obj in elements:
            # The results of a xpath query can be a str
            if type(obj) in (_ElementStringResult, _ElementUnicodeResult):
                result.append(unicode(obj))
            else:
                result.append(make_odf_element(obj))
        return result


    def clear(self):
        element = self.__element
        element.clear()
        element.text = None


    def clone(self):
        element = self.__element
        return self.__class__(deepcopy(element))


    def serialize(self, pretty=False):
        element = deepcopy(self.__element)
        data = tostring(element, with_tail=False, pretty_print=pretty)
        # XXX hack over lxml: remove namespaces
        return ns_stripper.sub('', data)


    def delete(self, child):
        element = self.__element
        element.remove(child.__element)


    #
    # Element helpers usable from any context
    #

    #
    # Dublin core
    #

    def get_dc_creator(self):
        dc_creator = self.get_element('descendant::dc:creator')
        if dc_creator is None:
            return None
        return dc_creator.get_text()


    def set_dc_creator(self, creator):
        dc_creator = self.get_element('descendant::dc:creator')
        if dc_creator is None:
            dc_creator = odf_create_element('<dc:creator/>')
            self.append_element(dc_creator)
        dc_creator.set_text(creator)


    def get_dc_date(self):
        dc_date = self.get_element('descendant::dc:date')
        if dc_date is None:
            return None
        date = dc_date.get_text()
        return DateTime.decode(date)


    def set_dc_date(self, date):
        dc_date = self.get_element('descendant::dc:date')
        if dc_date is None:
            dc_date = odf_create_element('<dc:date/>')
            self.append_element(dc_date)
        dc_date.set_text(DateTime.encode(date))

    #
    # Sections
    #

    def get_section_list(self, style=None, regex=None):
        return _get_element_list(self, 'text:section', style=style,
                                 regex=regex)


    def get_section_by_position(self, position):
        return _get_element(self, 'text:section', position=position)


    def get_section_by_content(self, regex):
        return _get_element(self, 'text:section', regex=regex)


    #
    # Paragraphs
    #

    def get_paragraph_list(self, style=None, regex=None):
        return _get_element_list(self, 'text:p', style=style, regex=regex)


    def get_paragraph_by_position(self, position):
        return _get_element(self, 'text:p', position=position)


    def get_paragraph_by_content(self, regex):
        return _get_element(self, 'text:p', regex=regex)


    #
    # Span
    #

    def get_span_list(self, style=None, regex=None):
        return _get_element_list(self, 'text:span', style=style, regex=regex)


    def get_span_by_position(self, position):
        return _get_element(self, 'text:span', position=position)


    def get_span_by_content(self, regex):
        return _get_element(self, 'text:span', regex=regex)


    #
    # Headings
    #

    def get_heading_list(self, style=None, level=None, regex=None):
        return _get_element_list(self, 'text:h', style=style, level=level,
                                 regex=regex)


    def get_heading_by_position(self, position, level=None):
        return _get_element(self, 'text:h', position=position, level=level)


    def get_heading_by_content(self, regex, level=None):
        return _get_element(self, 'text:h', regex=regex, level=level)


    #
    # Frames
    #

    def get_frame_list(self, style=None, title=None, description=None,
                       regex=None):
        return _get_element_list(self, 'draw:frame', draw_style=style,
                                 svg_title=title, svg_desc=description,
                                 regex=regex)


    def get_frame_by_name(self, name):
        return _get_element(self, 'draw:frame', draw_name=name)


    def get_frame_by_position(self, position):
        return _get_element(self, 'draw:frame', position=position)


    def get_frame_by_content(self, regex):
        return _get_element(self, 'draw:frame', regex=regex)


    def get_frame_by_title(self, regex):
        return _get_element(self, 'draw:frame', svg_title=regex)


    def get_frame_by_description(self, regex):
        return _get_element(self, 'draw:frame', svg_desc=regex)


    #
    # Images
    #

    def get_image_list(self, style=None, href=None, regex=None):
        """Get all image elements matching the criteria. Style is the style
        name. Set link to False to get only internal images, and True to
        get only external images (not in the container). Href is a regex to
        find all images with their path matching.

        Arguments:

            style -- str

            link -- bool

            href -- unicode regex

        Return: list of odf_element
        """
        return _get_element_list(self, 'draw:image', style=style, href=href,
                                 regex=regex)


    def get_image_by_name(self, name):
        # The frame is holding the name
        frame = _get_element(self, 'draw:frame', draw_name=name)
        if frame is None:
            return None
        return frame.get_element('draw:image')


    def get_image_by_position(self, position):
        return _get_element(self, 'draw:image', position=position)


    def get_image_by_path(self, regex):
        return _get_element(self, 'draw:image', href=regex)


    def get_image_by_content(self, regex):
        return _get_element(self, 'draw:image', regex=regex)


    #
    # Tables
    #

    def get_table_list(self, style=None, regex=None):
        return _get_element_list(self, 'table:table', style=style,
                                 regex=regex)


    def get_table_by_name(self, name):
        return _get_element(self, 'table:table', table_name=name)


    def get_table_by_position(self, position):
        return _get_element(self, 'table:table', position=position)


    def get_table_by_content(self, regex):
        return _get_element(self, 'table:table', regex=regex)


    #
    # Notes
    #

    def get_note_list(self, note_class=None, regex=None):
        """Return the list of all note element, optionally the ones of the
        given class or that match the given regex.

        Arguments:

            note_class -- 'footnote' or 'endnote'

            regex -- unicode

        Return: list of odf_element
        """
        return _get_element_list(self, 'text:note', note_class=note_class,
                                 regex=regex)


    def get_note_by_id(self, note_id):
        return _get_element(self, 'text:note', text_id=note_id)


    def get_note_by_class(self, note_class):
        return _get_element_list(self, 'text:note', note_class=note_class)


    def get_note_by_content(self, regex):
        return _get_element(self, 'text:note', regex=regex)


    #
    # Annotations
    #

    def get_annotation_list(self, creator=None, start_date=None,
                            end_date=None, regex=None):
        """XXX end date is not included (as expected in Python).
        """
        annotations = []
        for annotation in _get_element_list(self, 'office:annotation',
                                            regex=regex):
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


    def get_annotation(self, creator=None, start_date=None, end_date=None,
                       regex=None):
        annotations = self.get_annotation_list(creator=creator,
                                               start_date=start_date,
                                               end_date=end_date,
                                               regex=regex)
        if annotations:
            return annotations[0]
        return None


    #
    # Variables
    #

    def get_variable_decls(self):
        variable_decls = self.get_element('//text:variable-decls')
        if variable_decls is None:
            from document import odf_create_variable_decls

            # Variable only in a "text" document ?
            body = self.get_body()
            body.insert_element(odf_create_variable_decls(), FIRST_CHILD)
            variable_decls = body.get_element('//text:variable-decls')

        return variable_decls


    def get_variable_list(self):
        return _get_element_list(self, 'text:variable-decl')


    def get_variable_decl(self, name):
        return _get_element(self, 'text:variable-decl', text_name=name)


    def get_variable_sets(self, name):
        return _get_element_list(self, 'text:variable-set', text_name=name)


    def get_variable_value(self, name, value_type=None):
        variable_sets = self.get_variable_sets(name)
        # Nothing ?
        if not variable_sets:
            return None
        # Get the last value
        return get_value(variable_sets[-1], value_type)


    #
    # User fields
    #

    def get_user_field_decls(self):
        user_field_decls = self.get_element('//text:user-field-decls')
        if user_field_decls is None:
            from document import odf_create_user_field_decls
            body = self.get_body()
            body.insert_element(odf_create_user_field_decls(), FIRST_CHILD)
            user_field_decls = body.get_element('//text:user-field-decls')

        return user_field_decls


    def get_user_field_list(self):
        return _get_element_list(self, 'text:user-field-decl')


    def get_user_field_decl(self, name):
        return _get_element(self, 'text:user-field-decl', text_name=name)


    def get_user_field_value(self, name, value_type=None):
        user_field_decl = self.get_user_field_decl(name)
        # Nothing ?
        if user_field_decl is None:
            return None
        return get_value(user_field_decl, value_type)


    #
    # Draw Pages
    #
    def get_draw_page_list(self, style=None, regex=None):
        return _get_element_list(self, 'draw:page', draw_style=style,
                                 regex=regex)


    def get_draw_page_by_name(self, name):
        return _get_element(self, 'draw:page', draw_name=name)


    def get_draw_page_by_position(self, position):
        return _get_element(self, 'draw:page', position=position)


    def get_draw_page_by_content(self, regex):
        return _get_element(self, 'draw:page', regex=regex)


    #
    # Links
    #

    def get_link_list(self, name=None, title=None, href=None, regex=None):
        return _get_element_list(self, 'text:a', office_name=name,
                                 office_title=title, href=href, regex=regex)


    def get_link_by_name(self, name):
        return _get_element(self, 'text:a', office_name=name)


    def get_link_by_path(self, regex):
        return _get_element(self, 'text:a', href=regex)


    def get_link_by_content(self, regex):
        return _get_element(self, 'text:a', regex=regex)


    #
    # Bookmarks
    #

    def get_bookmark_list(self):
        return _get_element_list(self, 'text:bookmark')


    def get_bookmark_by_name(self, name):
        return _get_element(self, 'text:bookmark', text_name=name)


    def get_bookmark_start_list(self):
        return _get_element_list(self, 'text:bookmark-start')


    def get_bookmark_start_by_name(self, name):
        return _get_element(self, 'text:bookmark-start', text_name=name)


    def get_bookmark_end_list(self):
        return _get_element_list(self, 'text:bookmark-end')


    def get_bookmark_end_by_name(self, name):
        return _get_element(self, 'text:bookmark-end', text_name=name)


    #
    # Reference marks
    #

    def get_reference_mark_list(self):
        return _get_element_list(self, 'text:reference-mark')


    def get_reference_mark_by_name(self, name):
        return _get_element(self, 'text:reference-mark', text_name=name)


    def get_reference_mark_start_list(self):
        return _get_element_list(self, 'text:reference-mark-start')


    def get_reference_mark_start_by_name(self, name):
        return _get_element(self, 'text:reference-mark-start',
                            text_name=name)


    def get_reference_mark_end_list(self):
        return _get_element_list(self, 'text:reference-mark-end')


    def get_reference_mark_end_by_name(self, name):
        return _get_element(self, 'text:reference-mark-end', text_name=name)


    #
    # Shapes elements
    #

    #
    # Lines
    #

    def get_draw_line_list(self, draw_style=None, draw_text_style=None, regex=None):
        return _get_element_list(self, 'draw:line', draw_style=draw_style,
                                 draw_text_style=draw_text_style, regex=regex)


    def get_draw_line_by_content(self, regex):
        return _get_element(self, 'draw:line', regex=regex)


    def get_draw_line_by_id(self, id):
        lines = self.get_draw_line_list()
        lines = [line for line in lines
                      if line.get_attribute('draw:id') == id]
        return lines[0] if lines else None

    #
    # Rectangles
    #

    def get_draw_rectangle_list(self, draw_style=None, draw_text_style=None,
                                regex=None):
        return _get_element_list(self, 'draw:rect', draw_style=draw_style,
                                 draw_text_style=draw_text_style, regex=regex)


    def get_draw_rectangle_by_content(self, regex):
        return _get_element(self, 'draw:rect', regex=regex)


    def get_draw_rectangle_by_id(self, id):
        rectangles = self.get_draw_rectangle_list()
        rectangles = [rectangle for rectangle in rectangles
                                if rectangle.get_attribute('draw:id') == id]
        return rectangles[0] if rectangle else None

    #
    # Ellipse
    #

    def get_draw_ellipse_list(self, draw_style=None, draw_text_style=None,
                              regex=None):
        return _get_element_list(self, 'draw:ellipse', draw_style=draw_style,
                                 draw_text_style=draw_text_style, regex=regex)


    def get_draw_ellipse_by_content(self, regex):
        return _get_element(self, 'draw:ellipse', regex=regex)


    def get_draw_ellipse_by_id(self, id):
        ellipses = self.get_draw_ellipse_list()
        ellipses = [ellipse for ellipse in ellipses
                            if ellipse.get_attribute('draw:id') == id]
        return ellipses[0] if ellipse else None

    #
    # Connectors
    #

    def get_draw_connector_list(self, draw_style=None, draw_text_style=None,
                                regex=None):
        return _get_element_list(self, 'draw:connector', draw_style=draw_style,
                                 draw_text_style=draw_text_style, regex=regex)


    def get_draw_connector_by_content(self, regex):
        return _get_element(self, 'draw:connector', regex=regex)


    def get_draw_connector_by_id(self, id):
        connectors = self.get_draw_connector_list()
        connectors = [connector for connector in connectors
                                if connector.get_attribute('draw:id') == id]
        return connectors[0] if connector else None


    def get_draw_orphans_connectors(self):
        """Return a list of connectors, which havn't any shape connected to
        them.
        """
        connectors = []
        for connector in self.get_draw_connector_list():
            start_shape = connector.get_attribute('draw:start-shape')
            end_shape = connector.get_attribute('draw:end-shape')
            if start_shape is None and end_shape is None:
                connectors.append(connector)
        return connectors

    #
    # Tracked changes
    #

    def get_changes_ids(self):
        """Return a list of ids that refers to a change region in the tracked
        changes list.
        """
        # Insertion changes
        xpath_query = 'descendant::text:change-start/@text:change-id'
        # Deletion changes
        xpath_query += ' | descendant::text:change/@text:change-id'
        return self.xpath(xpath_query)

