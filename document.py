# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
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
from operator import itemgetter
from os.path import splitext
from uuid import uuid4

# Import from lpod
from __init__ import __version__
from container import ODF_PARTS, odf_get_container
from container import odf_new_container_from_template
from container import odf_new_container_from_type, odf_container
from content import odf_content
from meta import odf_meta
from style import odf_style, odf_master_page, odf_font_style
from styles import odf_styles
from utils import _get_style_family
from vfs import vfs
from xmlpart import odf_xmlpart


underline_lvl = ['=', '-', ':', '`', "'", '"', '~', '^', '_', '*', '+']


def _show_styles(element, level=0):
    output = []
    attributes = element.get_attributes()
    children = element.get_children()
    # Don't show the empty elements
    if not attributes and not children:
        return None
    tag_name = element.get_tagname()
    output.append(tag_name)
    # Underline and Overline the name
    underline = underline_lvl[level] * len(tag_name)
    underline = underline if level < len(underline_lvl) else '\n'
    output.append(underline)
    # Add a separation between name and attributes
    output[-1] += '\n'
    attrs = []
    # Attributes
    for key, value in attributes.iteritems():
        attrs.append(u'%s: %s' % (key, value))
    if attrs:
        attrs.sort()
        # Add a separation between attributes and children
        attrs[-1] += '\n'
        output.extend(attrs)
    # Children
    # Sort children according to their names
    children = [(child.get_tagname(), child) for child in children]
    children.sort()
    children = [child for name, child in children]
    for child in children:
        child_output = _show_styles(child, level + 1)
        if child_output:
            output.append(child_output)
    return '\n'.join(output)


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


    def get_content(self):
        """Return the content part.

        Return: odf_content
        """
        return self.get_xmlpart('content')


    def get_meta(self):
        """Return the meta part.

        Return: odf_meta
        """
        return self.get_xmlpart('meta')


    def get_styles(self):
        """Return the styles part.

        Return: odf_styles
        """
        return self.get_xmlpart('styles')


    def get_type(self):
        """
        Get the ODF type (also called class) of this document.

        Return: 'chart', 'database', 'formula', 'graphics',
            'graphics-template', 'image', 'presentation',
            'presentation-template', 'spreadsheet', 'spreadsheet-template',
            'text', 'text-master', 'text-template' or 'text-web'
        """

        mimetype = self.container.get_part('mimetype').strip()

        # The mimetype must be with the form:
        # application/vnd.oasis.opendocument.text

        # Isolate and return the last part
        return mimetype.rsplit('.', 1)[-1]


    def get_body(self):
        """Return the body element of the content part, where actual content
        is inserted.
        """
        if self.__body is None:
            content = self.get_content()
            self.__body = content.get_body()
        return self.__body


    def get_parts(self):
        """Return available part names with path inside the archive, e.g.
        ['content.xml', ..., 'Pictures/100000000000032000000258912EB1C3.jpg']
        """
        return self.container.get_parts()


    def get_part(self, part_name):
        """Return the bytes of the given part. The part_name includes the
        path inside the archive, e.g.
        "Pictures/100000000000032000000258912EB1C3.jpg"
        """
        return self.container.get_part(part_name)


    def set_part(self, part_name, data):
        """Set the bytes of the given part. The part_name includes the
        path inside the archive, e.g.
        "Pictures/100000000000032000000258912EB1C3.jpg"
        """
        return self.container.set_part(part_name, data)


    def get_formatted_text(self, rst_mode=False):
        # For the moment, only "type='text'"
        type = self.get_type()
        if type not in ('text', 'text-template', 'presentation',
                'presentation-template'):
            raise NotImplementedError, ('Type of document "%s" not '
                                        'supported yet' % type)
        # Initialize an empty context
        context = {'document': self,
                   'footnotes': [],
                   'endnotes': [],
                   'annotations': [],
                   'rst_mode': rst_mode}
        body = self.get_body()
        # Get the text
        result = []
        for element in body.get_children():
            if element.get_tagname() == 'table:table':
                result.append(element.get_formatted_text(context))
            else:
                result.append(element.get_formatted_text(context))
                # Insert the notes
                footnotes = context['footnotes']
                # Separate text from notes
                if footnotes:
                    if rst_mode:
                        result.append(u'\n')
                    else:
                        result.append(u'----\n')
                    for citation, body in footnotes:
                        if rst_mode:
                            result.append(u'.. [#] %s\n' % body)
                        else:
                            result.append(u'[%s] %s\n' % (citation, body))
                    # Append a \n after the notes
                    result.append(u'\n')
                    # Reset for the next paragraph
                    context['footnotes'] = []
                # Insert the annotations
                annotations = context['annotations']
                # With a separation
                if annotations:
                    if rst_mode:
                        result.append(u'\n')
                    else:
                        result.append(u'----\n')
                    for annotation in annotations:
                        if rst_mode:
                            result.append('.. [#] %s\n' % annotation)
                        else:
                            result.append('[*] %s\n' % annotation)
                    context['annotations'] = []
        # Append the end notes
        endnotes = context['endnotes']
        if endnotes:
            if rst_mode:
                result.append(u'\n\n')
            else:
                result.append(u'\n========\n')
            for citation, body in endnotes:
                if rst_mode:
                    result.append(u'.. [*] %s\n' % body)
                else:
                    result.append(u'(%s) %s\n' % (citation, body))
        return u''.join(result)


    def get_formated_meta(self):
        result = []

        meta = self.get_meta()

        # Simple values
        def print_info(name, value):
            if value:
                result.append("%s: %s" % (name, value))

        print_info("Title", meta.get_title())
        print_info("Subject", meta.get_subject())
        print_info("Language", meta.get_language())
        print_info("Modification date", meta.get_modification_date())
        print_info("Creation date", meta.get_creation_date())
        print_info("Initial creator", meta.get_initial_creator())
        print_info("Keyword", meta.get_keywords())
        print_info("Editing duration", meta.get_editing_duration())
        print_info("Editing cycles", meta.get_editing_cycles())
        print_info("Generator", meta.get_generator())

        # Statistic
        result.append("Statistic:")
        statistic =  meta.get_statistic()
        for name, value in statistic.iteritems():
            result.append("  - %s: %s" % (
                              name[5:].replace('-', ' ').capitalize(),
                              value))

        # User defined metadata
        result.append("User defined metadata:")
        user_metadata = meta.get_user_defined_metadata()
        for name, value in user_metadata.iteritems():
            result.append("  - %s: %s" % (name, value))

        # And the description
        print_info("Description", meta.get_description())

        return u"\n".join(result) + '\n'


    def add_file(self, uri_or_file):
        name = None
        if type(uri_or_file) is unicode or type(uri_or_file) is str:
            uri_or_file = uri_or_file.encode('utf_8')
            file = vfs.open(uri_or_file)
            name = uri_or_file
        else:
            file = uri_or_file
            name = getattr(file, 'name')
        # Generate a safe portable name
        uuid = str(uuid4())
        if name is None:
            name = uuid
        else:
            _, extension = splitext(name)
            name = uuid + extension.lower()
        name = 'Pictures/%s' % (name)
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


    def save(self, target=None, packaging=None, pretty=False):
        """Save the document, at the same place it was opened or at the given
        URI (target). Target can also be a file like object. It can be saved
        as a Zip file or as a flat XML file. XML parts can be pretty printed.

        Arguments:

            target -- str -or- file like object

            packaging -- 'zip' or 'flat'

            pretty -- bool
        """
        # Some advertising
        meta = self.get_meta()
        if not meta._generator_modified:
            meta.set_generator(u"lpOD Python %s" % __version__)
        # Synchronize data with container
        for part_name, part in self.__xmlparts.items():
            if part is not None:
                self.container.set_part(part_name, part.serialize(pretty))

        # Save the container
        self.container.save(target, packaging)


    #
    # Styles over several parts
    #

    def get_style_list(self, family=None, automatic=False):
        content = self.get_content()
        styles = self.get_styles()
        return (content.get_style_list(family=family)
                + styles.get_style_list(family=family, automatic=automatic))


    def get_style(self, family, name_or_element=None, display_name=None):
        """Return the style uniquely identified by the name/family pair. If
        the argument is already a style object, it will return it.

        If the name is None, the default style is fetched.

        If the name is not the internal name but the name you gave in a
        desktop application, use display_name instead.

        Arguments:

            family -- 'paragraph', 'text',  'graphic', 'table', 'list',
                      'number', 'page-layout', 'master-page'

            name -- unicode or odf_element or None

            display_name -- unicode

        Returns: odf_style or None if not found.
        """
        # 1. content.xml
        content = self.get_content()
        element = content.get_style(family, name_or_element=name_or_element,
                display_name=display_name)
        if element is not None:
            return element
        # 2. styles.xml
        styles = self.get_styles()
        return styles.get_style(family, name_or_element=name_or_element,
                display_name=display_name)


    def insert_style(self, style, name=None, automatic=False, default=False):
        """Insert the given style object in the document, as required by the
        style family and type.

        The style is expected to be a common style with a name. In case it
        was created with no name, the given can be set on the fly.

        If automatic is True, the style will be inserted as an automatic
        style.

        If default is True, the style will be inserted as a default style and
        would replace any existing default style of the same family. Any name
        or display name would be ignored.

        Automatic and default arguments are mutually exclusive.

        All styles can’t be used as default styles. Default styles are
        allowed for the following families: paragraph, text, section, table,
        table-column, table-row, table-cell, table-page, chart, drawing-page,
        graphic, presentation, control and ruby.

        Arguments:

            style -- odf_style

            name -- unicode

            automatic -- bool

            default -- bool
        """

        # Get family and name
        family = style.get_style_family()
        if name is None:
            name = style.get_style_name()

        # Master page style
        if isinstance(style, odf_master_page):
            part = self.get_styles()
            container = part.get_element("office:master-styles")
            existing = part.get_style(family, name)
        # Font face declarations
        elif isinstance(style, odf_font_style):
            # XXX If inserted in styles.xml => It doesn't work, it's normal?
            part = self.get_content()
            container = part.get_element("office:font-face-decls")
            existing = part.get_style(family, name)
        # Common style
        elif isinstance(style, odf_style):
            # Common style
            if name and automatic is False and default is False:
                part = self.get_styles()
                container = part.get_element("office:styles")
                existing = part.get_style(family, name)

            # Automatic style
            elif automatic is True and default is False:
                part = self.get_content()
                container = part.get_element("office:automatic-styles")

                # A name ?
                if name is None:
                    # Make a beautiful name

                    # TODO: Use prefixes of Ooo: Mpm1, ...
                    prefix = 'lpod_auto_'

                    styles = self.get_style_list(family=family, automatic=True)
                    names = [ s.get_style_name () for s in styles ]
                    numbers = [ int(name[len(prefix):]) for name in names
                                if name and name.startswith(prefix) ]
                    if numbers:
                        number = max(numbers) + 1
                    else:
                        number = 1
                    name = prefix + str(number)

                    # And set it
                    style.set_style_name(name)
                    existing = None
                else:
                    existing = part.get_style(family, name)

            # Default style
            elif automatic is False and default is True:
                part = self.get_styles()
                container = part.get_element("office:styles")

                # Force default style
                style.set_tagname("style:default-style")
                if name is not None:
                    style.del_attribute("style:name")

                existing = part.get_style(family)

            # Error
            else:
              raise AttributeError, "invalid combination of arguments"
        # Invalid style
        else:
            raise ValueError, "invalid style"

        # Insert it!
        if existing is not None:
            container.delete_element(existing)
        container.append_element(style)


    def get_styled_elements(self, name=True):
        """Brute-force to find paragraphs, tables, etc. using the given style
        name (or all by default).

        Arguments:

            name -- unicode

        Return: list
        """
        content = self.get_content()
        # Header, footer, etc. have styles too
        styles = self.get_styles()
        return (content.get_root().get_styled_elements(name)
                + styles.get_root().get_styled_elements(name))


    def show_styles(self, automatic=True, common=True, properties=False):
        infos = []
        for style in self.get_style_list():
            name = style.get_style_name()
            is_auto = (style.get_parent().get_tagname()
                    == 'office:automatic-styles')
            if (is_auto and automatic is False
                    or not is_auto and common is False):
                continue
            is_used = bool(self.get_styled_elements(name))
            infos.append({'type': u"auto  " if is_auto else u"common",
                          'used': u"y" if is_used else u"n",
                          'family': style.get_style_family(),
                          'parent': style.get_parent_style_name() or u"",
                          'name': name or u"",
                          'display_name': style.get_style_display_name(),
                          'properties': style.get_style_properties() if
                                        properties else None})
        if not infos:
            return u""
        # Sort by family and name
        infos.sort(key=itemgetter('family', 'name'))
        # Show common and used first
        infos.sort(key=itemgetter('type', 'used'), reverse=True)
        max_family = unicode(max([len(x['family']) for x in infos]))
        max_parent = unicode(max([len(x['parent']) for x in infos]))
        format = (u"%(type)s used:%(used)s family:%(family)-0" + max_family
                + u"s parent:%(parent)-0" + max_parent + u"s name:%(name)s")
        output = []
        for info in infos:
            line = format % info
            if info['display_name']:
                line += u' display_name:' + info['display_name']
            output.append(line)
            if info['properties']:
                for name, value in info['properties'].iteritems():
                    output.append("   - %s: %s" % (name, value))
        output.append(u"")
        return u"\n".join(output)


    def delete_styles(self):
        """Remove all style information from content and all styles.

        Return: number of deleted styles
        """
        # First remove references to styles
        for element in self.get_styled_elements():
            for attribute in ('text:style-name', 'draw:style-name',
                    'draw:text-style-name', 'table:style-name',
                    'style:page-layout-name'):
                try:
                    element.del_attribute(attribute)
                except KeyError:
                    continue
        # Then remove supposedly orphaned styles
        i = 0
        for style in self.get_style_list():
            if style.get_style_name() is None:
                # Don't delete default styles
                continue
            elif type(style) is odf_master_page:
                # Don't suppress header and footer, just styling was removed
                continue
            style.get_parent().delete_element(style)
            i += 1
        return i


    def merge_styles_from(self, document):
        """Copy all the styles of a document into ourself.

        Styles with the same type and name will be replaced, so only unique
        styles will be preserved.
        """
        styles = self.get_styles()
        content = self.get_content()
        for style in document.get_style_list():
            tagname = style.get_tagname()
            family = style.get_style_family()
            if family is None:
                family = _get_style_family(tagname)
            stylename = style.get_style_name()
            container = style.get_parent()
            container_name = container.get_tagname()
            partname = container.get_parent().get_tagname()
            # The destination part
            if partname == "office:document-styles":
                part = styles
            elif partname == "office:document-content":
                part = content
            else:
                raise NotImplementedError, partname
            # Implemented containers
            if container_name not in ('office:styles',
                                      'office:automatic-styles',
                                      'office:master-styles',
                                      'office:font-face-decls'):
                raise NotImplementedError, container_name
            dest = part.get_element('//%s' % container_name)
            # Implemented style types
            if tagname not in ('style:default-style', 'style:style',
                               'style:style', 'style:page-layout',
                               'style:master-page', 'style:font-face',
                               'text:list-style', 'number:number-style',
                               'text:outline-style', 'number:date-style'):
                raise NotImplementedError, tagname
            duplicate = part.get_style(family, stylename)
            if duplicate is not None:
                duplicate.get_parent().delete_element(duplicate)
            dest.append_element(style)



#
# odf_document factories
#

def odf_get_document(uri):
    """Return an "odf_document" instance of the ODF document stored in the
    given file-like object or at the given URI.

    Example::

        >>> document = odf_get_document(stringio)
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
