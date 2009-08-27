# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from copy import deepcopy
from uuid import uuid4

# Import from lpod
from container import ODF_PARTS, odf_get_container
from container import odf_new_container_from_type, odf_container
from container import odf_new_container_from_template
from content import odf_content
from meta import odf_meta
from styles import odf_styles
from xmlpart import odf_xmlpart
from vfs import vfs


class odf_document(object):
    """Abstraction of the ODF document.
    """
    def __init__(self, container):
        if not isinstance(container, odf_container):
            raise TypeError, "container is not an ODF container"
        self.container = container

        # Cache of XML parts
        self.__xmlparts = {}

        # Cache of the body
        self.__body = None


    #
    # Public API
    #

    def get_xmlpart(self, part_name):
        if part_name not in ODF_PARTS:
            raise ValueError, '"%s" is not an XML part' % part_name
        parts = self.__xmlparts
        part = parts.get(part_name)
        if part is None:
            container = self.container
            if part_name == 'content':
                part = odf_content(part_name, container)
            elif part_name == 'meta':
                part = odf_meta(part_name, container)
            elif part_name == 'styles':
                part = odf_styles(part_name, container)
            else:
                part = odf_xmlpart(part_name, container)
            parts[part_name] = part
        return part


    def get_type(self):
        """
        Get the ODF type (also called class) of this document.

        Return: 'chart', 'database', 'formula', 'graphics',
            'graphics-template', 'image', 'presentation',
            'presentation-templatemplate', 'spreadsheet',
            'spreadsheet-template', 'text', 'text-master',
            'text-template' or 'text-web'
        """

        mimetype = self.container.get_part('mimetype').strip()

        # The mimetype must be with the form:
        # application/vnd.oasis.opendocument.text

        # Isolate and return the last part
        return mimetype.split('.')[-1]


    def get_body(self):
        if self.__body is None:
            content = self.get_xmlpart('content')
            self.__body = content.get_body()
        return self.__body


    def get_formated_text(self):
        # XXX Fix thix cyclic import
        from table import odf_table
        # For the moment, only "type='text'"
        if self.get_type() != 'text':
            raise NotImplementedError, ('This functionality is only '
                                        'implemented for a "text" document')
        # Initialize an empty context
        context = {'notes_counter': 0,
                   'footnotes': [],
                   'endnotes': []}
        body = self.get_body()
        # Get the text
        result = []
        for element in body.get_children():
            if element.get_name() == 'table:table':
                table = odf_table(odf_element=element)
                result.append(table.get_formated_text(context))
            else:
                result.append(element.get_formated_text(context))
                # Insert the notes
                footnotes = context['footnotes']
                # Separate text from notes
                if footnotes:
                    result.append(u'---\n')
                    for citation, body in footnotes:
                        result.append(u'[%s] %s\n' % (citation, body))
                    # Append a \n after the notes
                    result.append(u'\n')
                    # Reset for the next paragraph
                    context['footnotes'] = []
        # Append the end notes
        endnotes = context['endnotes']
        if endnotes:
            result.append(u'\n------\n')
            for citation, body in endnotes:
                result.append(u'(%s) %s\n' % (citation, body))
        return u''.join(result)


    def add_file(self, uri_or_file):
        if type(uri_or_file) is unicode or type(uri_or_file) is str:
            uri_or_file = uri_or_file.encode('utf_8')
            file = vfs.open(uri_or_file)
        else:
            file = uri_or_file
        name = 'Pictures/%s' % uuid4()
        data= file.read()
        self.container.set_part(name, data)
        return name


    def clone(self):
        """Return an exact copy of the document.
        Return: odf_document
        """
        clone = object.__new__(self.__class__)
        for name in self.__dict__:
            if name == 'container':
                setattr(clone, name, self.container.clone())
            elif name == '_odf_document__xmlparts':
                xmlparts = {}
                for key, value in self.__xmlparts.iteritems():
                    xmlparts[key] = value.clone()
                setattr(clone, name, xmlparts)
            else:
                value = getattr(self, name)
                value = deepcopy(value)
                setattr(clone, name, value)
        return clone


    def save(self, uri=None, packaging=None, pretty=False):
        """Save the document, at the same place it was opened or at the given
        URI. It can be saved as a Zip file or as a plain XML file. The XML
        can be pretty printed.
        Arguments:

            uri -- str
            packaging -- 'zip' or 'flat'
            pretty -- bool
        """
        # Synchronize data with container
        for part_name, part in self.__xmlparts.items():
            if part is not None:
                self.container.set_part(part_name, part.serialize(pretty))

        # Save the container
        self.container.save(uri, packaging)


    #
    # Styles over several parts
    #

    def get_style_list(self, family=None, automatic=False):
        styles = self.get_xmlpart('styles')
        if automatic:
            content = self.get_xmlpart('content')
            return (styles.get_style_list(family=family, automatic=True)
                    + content.get_style_list(family=family))
        return styles.get_style_list(family=family)


    def get_style(self, name_or_element, family, display_name=False):
        """Return the style uniquely identified by the name/family pair. If
        the argument is already a style object, it will return it.

        If the name is None, the default style is fetched.

        If the name is not the internal name but the name you gave in a
        desktop application, set display_name to True.

        Arguments:

            name -- unicode or odf_element or None

            family -- 'paragraph', 'text',  'graphic', 'table', 'list',
                      'number', 'page-layout', 'master-page'

            display_name -- bool

        Returns: odf_style or None if not found.
        """
        # 1. content.xml
        content = self.get_xmlpart('content')
        element = content.get_style(name_or_element, family,
                                    display_name=display_name)
        if element is not None:
            return element
        # 2. styles.xml
        styles = self.get_xmlpart('styles')
        return styles.get_style(name_or_element, family,
                                display_name=display_name)



#
# odf_document factories
#

def odf_get_document(uri):
    """Return an "odf_document" instance of the ODF document stored at the
    given URI.

    Example::

        >>> uri = 'uri://of/a/document.odt'
        >>> document = odf_get_document(uri)
    """
    container = odf_get_container(uri)
    return odf_document(container)



def odf_new_document_from_template(template_uri):
    """Return an "odf_document" instance using the given template.

    Example::

        >>> uri = 'uri://of/a/template.ott'
        >>> document = odf_new_document_from_template(uri)
    """
    container = odf_new_container_from_template(template_uri)
    return odf_document(container)



def odf_new_document_from_type(odf_type):
    """Return an "odf_document" instance of the given type.
    Arguments:

        odf_type -- 'text', 'spreadsheet', 'presentation' or 'drawing'

    Example::

        >>> document = odf_new_document_from_type('spreadsheet')
    """
    container = odf_new_container_from_type(odf_type)
    return odf_document(container)
