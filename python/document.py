# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from container import get_odf_container, new_odf_container_from_template
from container import new_odf_container_from_class, odf_container
from xmlpart import odf_element


def create_paragraph(style, text=''):
    raise NotImplementedError



def create_heading(style, level, text=''):
    raise NotImplementedError



def generate_xpath_query(element_name, attributes={}, position=None):
    query = ['//']
    query.append(element_name)
    for name, value in attributes.items():
        if value is not None:
            query.append('[@{name}="{value}"]'.format(name, str(value)))
        else:
            query.append('[@{name}]'.format(name))
    if position is not None:
        query.append('[{position}]'.format(str(position)))
    return ''.join(query)



def check_arguments(context=None, position=None, style=None, level=None):
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
        self.__content = None
        self.__styles = None
        self.__meta = None


    def __get_xmlpart(self, part_name):
        part = getattr(self, '__' + part_name, None)
        if part is None:
            container = self.container
            part = odf_xmlpart(part_name, container)
            setattr(self, '__' + part_name, part)
        return part

    #
    # Paragraphs
    #

    def get_paragraph_list(self, style=None, context=None):
        check_arguments(style=style, context=context)
        content = self.__get_xmlpart('content')
        attributes = {}
        if style:
            attributes['text:style-name'] = style
        query = generate_xpath_query('text:p', attributes)
        return content.get_element_list(query, context=context)


    def get_paragraph(self, position, context=None):
        check_arguments(position=position, context=context)
        content = self.__get_xmlpart('content')
        query = generate_xpath_query('text:p', position)
        return content.get_element_list(query, context=context)


    def insert_paragraph(self, element, context=None):
        raise NotImplementedError


    #
    # Headings
    #

    def get_heading_list(self, style=None, level=None, context=None):
        check_arguments(style=style, level=level, context=context)
        content = self.__get_xmlpart('content')
        attributes = {}
        if style:
            attributes['text:style-name'] = style
        if level:
            attributes['text:level'] = level
        query = generate_xpath_query('text:h', attributes)
        return content.get_element_list(query, context=context)


    def get_heading(self, position, level=None, context=None):
        check_arguments(position=position, level=level, context=context)
        content = self.__get_xmlpart('content')
        query = generate_xpath_query('text:h', position)
        return content.get_element_list(query, context=context)


    def insert_heading(self, element, context=None):
        raise NotImplementedError


    #
    # Styles
    #

    def get_style(name):
        """Only paragraph styles for now.
        """
        raise NotImplementedError



def get_odf_document(uri):
    """Return an "odf_document" instance of the ODF document stored at the
    given URI.
    """
    container = get_odf_container(uri)
    return odf_document(container)



def new_odf_document_from_template(template_uri):
    """Return an "odf_document" instance using the given template.
    """
    container = new_odf_container_from_template(template_uri)
    return odf_document(container)


def new_odf_document_from_class(odf_class):
    """Return an "odf_document" instance of the given class.
    """
    container = new_odf_container_from_class(odf_class)
    return odf_document(container)
