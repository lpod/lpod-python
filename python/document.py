# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from copy import deepcopy

# Import from lpod
from container import odf_get_container, odf_new_container_from_template
from container import odf_new_container_from_class, odf_container
from xmlpart import odf_element, odf_xmlpart, LAST_CHILD
from xmlpart import odf_create_element



def odf_create_section(style):
    data = '<text:section text:style-name="%s"></text:section>' % style
    return odf_create_element(data)



def odf_create_paragraph(style, text=''):
    data = '<text:p text:style-name="%s">%s</text:p>' % (style, text)
    return odf_create_element(data)



def odf_create_heading(style, level, text=''):
    data = '<text:h text:style-name="%s" text:outline-level="%d">%s</text:h>'
    return odf_create_element(data % (style, level, text))



def odf_create_frame(name, style, width, height, page=None, x=None, y=None):
    if page is None:
        anchor = 'text:anchor-type="paragraph"'
    else:
        anchor = 'text:anchor-type="page" text:anchor-page-number="%d"' % page
        if x is not None:
            anchor += ' svg:x="%s"' % x
        if y is not None:
            anchor += ' svg:y="%s"' % y
    data = ('<draw:frame draw:name="%s" draw:style-name="%s" '
            'svg:width="%s" svg:height="%s" %s/>')

    return odf_create_element(data % (name, style, width, height, anchor))


def odf_create_image(link):
    return odf_create_element('<draw:image xlink:href="%s"/>' % link)


def odf_create_cell():
    return odf_create_element(
                    '<table:table-cell office:value-type="String"/>')


def odf_create_row(width=None):
    row = odf_create_element('<table:table-row/>')
    if width is not None:
        for i in xrange(width):
            cell = odf_create_cell()
            row.insert_element(cell, LAST_CHILD)
    return row


def odf_create_column(style):
    data = '<table:table-column table:style-name="%s"/>'
    return odf_create_element(data % style)


def odf_create_table(name, style, width=None, height=None):
    data = '<table:table table:name="%s" table:style-name="%s"/>'
    table = odf_create_element(data % (name, style))
    if width is not None or height is not None:
        width = width if width is not None else 1
        height = height if height is not None else 1
        for i in xrange(height):
            row = odf_create_row(width)
            table.insert_element(row, LAST_CHILD)
    return table


def odf_create_item():
    return odf_create_element('<text:list-item/>')


def odf_create_list(style):
    return odf_create_element('<text:list text:style-name="%s"/>' % style)



def _generate_xpath_query(element_name, attributes={}, position=None,
                          context=None):
    if context is not None:
        query = [context._get_xpath_path(), '//']
    else:
        query = ['//']
    query.append(element_name)
    # Sort attributes for reproducible test cases
    for name in sorted(attributes):
        value = attributes[name]
        if value is not None:
            query.append('[@{name}="{value}"]'.format(name=name,
                                                      value=str(value)))
        else:
            query.append('[@{name}]'.format(name=name))
    if position is not None:
        query.append('[{position}]'.format(position=str(position)))
    return ''.join(query)



def _check_arguments(context=None, position=None, style=None, level=None):
    if context is not None:
        if not isinstance(context, odf_element):
            raise TypeError, "an odf element is expected"
    if position is not None:
        if not isinstance(position, int):
            raise TypeError, "an integer position is expected"
        if position < 1:
            raise ValueError, "position count begin at 1"
    if style is not None:
        if not isinstance(style, str):
            raise TypeError, "a style name is expected"
    if level is not None:
        if not isinstance(level, int):
            raise TypeError, "an integer level is expected"
        if level < 1:
            raise ValueError, "level count begin at 1"



class odf_document(object):

    def __init__(self, container):
        if not isinstance(container, odf_container):
            raise TypeError, "container is not an ODF container"
        self.container = container

        # Cache of XML parts
        self.__xmlparts = {}


    def __get_xmlpart(self, part_name):
        parts = self.__xmlparts
        part = parts.get(part_name)
        if part is None:
            container = self.container
            part = odf_xmlpart(part_name, container)
            parts[part_name] = part
        return part


    def __get_element_list(self, name, style=None, level=None, context=None):
        _check_arguments(style=style, level=level, context=context)
        content = self.__get_xmlpart('content')
        attributes = {}
        if style:
            attributes['text:style-name'] = style
        if level:
            attributes['text:outline-level'] = level
        query = _generate_xpath_query(name, attributes=attributes,
                                      context=context)
        return content.get_element_list(query)


    def __get_element(self, name, position, level=None, context=None):
        _check_arguments(position=position, context=context)
        content = self.__get_xmlpart('content')
        attributes = {}
        if level:
            attributes['text:outline-level'] = level
        query = _generate_xpath_query(name, attributes=attributes,
                                      position=position, context=context)
        result = content.get_element_list(query)
        if not result:
            return None
        return result[0]


    def __insert_element(self, element, context, position):
        if context is not None:
            context.insert_element(element, position)
        else:
            # We insert it in the last office:text
            content = self.__get_xmlpart('content')
            office_text = content.get_element_list('//office:text')[-1]
            office_text.insert_element(element, LAST_CHILD)


    def clone(self):
        clone = object.__new__(self.__class__)
        for name in self.__dict__:
            if name == 'container':
                setattr(clone, name, self.container.clone())
            elif name == '_odf_document__xmlparts':
                # TODO odf_xmlpart.clone
                setattr(clone, name, {})
            else:
                value = getattr(self, name)
                value = deepcopy(value)
                setattr(clone, name, value)
        return clone


    def save(self, uri=None, packaging=None):
        # Synchronize data with container
        for part_name, part in self.__xmlparts:
            if part is not None:
                self.container.set_part(part_name, part.serialize())

        # Save the container
        self.container.save(uri, packaging)


    #
    # Sections
    #

    def get_section_list(self, style=None, context=None):
        return self.__get_element_list('text:section', style=style,
                                       context=context)


    def get_section(self, position, context=None):
        return self.__get_element('text:section', position, context=context)


    def insert_section(self, element, context=None, position=LAST_CHILD):
        self.__insert_element(element, context, position)


    #
    # Paragraphs
    #

    def get_paragraph_list(self, style=None, context=None):
        return self.__get_element_list('text:p', style=style,
                                       context=context)


    def get_paragraph(self, position, context=None):
        return self.__get_element('text:p', position, context=context)


    def insert_paragraph(self, element, context=None, position=LAST_CHILD):
        self.__insert_element(element, context, position)


    #
    # Headings
    #

    def get_heading_list(self, style=None, level=None, context=None):
        return self.__get_element_list('text:h', style=style, level=level,
                                       context=context)


    def get_heading(self, position, level=None, context=None):
        return self.__get_element('text:h', position, level=level,
                                  context=context)


    def insert_heading(self, element, context=None, position=LAST_CHILD):
        self.__insert_element(element, context, position)


    #
    # Frames
    #

    def insert_frame(self, element, context=None, position=LAST_CHILD):
        self.__insert_element(element, context, position)


    #
    # Images
    #

    def insert_image(self, element, context=None, position=LAST_CHILD):
        # XXX If context is None
        #     => auto create a frame with the good dimensions
        if context is None:
            raise NotImplementedError

        self.__insert_element(element, context, position)


    #
    # Tables
    #

    def insert_table(self, element, context=None, position=LAST_CHILD):
        self.__insert_element(element, context, position)


    def insert_column(self, element, context, position=LAST_CHILD):
        context.insert_element(element, position)


    def insert_row(self, element, context, position=LAST_CHILD):
        context.insert_element(element, position)


    def insert_cell(self, element, context, position=LAST_CHILD):
        context.insert_element(element, position)


    #
    # Lists
    #

    def insert_list(self, element, context=None, position=LAST_CHILD):
        self.__insert_element(element, context, position)


    def insert_item(self, element, context, position=LAST_CHILD):
        context.insert_element(element, position)


    #
    # Styles
    #

    def get_style(name):
        """Only paragraph styles for now.
        """
        raise NotImplementedError



def odf_get_document(uri):
    """Return an "odf_document" instance of the ODF document stored at the
    given URI.
    """
    container = odf_get_container(uri)
    return odf_document(container)



def odf_new_document_from_template(template_uri):
    """Return an "odf_document" instance using the given template.
    """
    container = odf_new_container_from_template(template_uri)
    return odf_document(container)



def odf_new_document_from_class(odf_class):
    """Return an "odf_document" instance of the given class.
    """
    container = odf_new_container_from_class(odf_class)
    return odf_document(container)
