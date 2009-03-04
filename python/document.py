# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from container import get_odf_container, new_odf_container_from_template
from container import new_odf_container_from_class, odf_container


def create_paragraph(style, text=''):
    raise NotImplementedError



def create_heading(style, level, text=''):
    raise NotImplementedError



class odf_document(object):

    def __init__(self, container):
        if not isinstance(container, odf_container):
            raise TypeError, "container is not an ODF container"
        self.container = container

    #
    # Paragraphs
    #

    def get_paragraph_list(self, style=None, context=None):
        raise NotImplementedError


    def get_paragraph(self, position, context=None):
        raise NotImplementedError


    def insert_paragraph(self, element, context=None):
        raise NotImplementedError


    #
    # Headings
    #

    def get_heading_list(self, style=None, level=None, context=None):
        raise NotImplementedError


    def get_heading(self, position, level=None, context=None):
        raise NotImplementedError


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
