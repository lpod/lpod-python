# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from datatype import Date, DateTime, Duration
from utils import _set_value_and_type
from element import odf_create_element


def odf_create_variable_decls():
    return odf_create_element('<text:variable-decls />')



def odf_create_variable_decl(name, value_type):
    data = u'<text:variable-decl office:value-type="%s" text:name="%s"/>'
    return odf_create_element(data % (value_type, name))



def odf_create_variable_set(name, value, value_type=None, display=False,
                            representation=None, style=None):
    data = u'<text:variable-set text:name="%s" />'
    element = odf_create_element(data % name)
    representation = _set_value_and_type(element, value=value,
                                         value_type=value_type,
                                         representation=representation)
    if not display:
        element.set_attribute('text:display', 'none')
    else:
        element.set_text(representation)
    if style is not None:
        element.set_attribute('style:data-style-name', style)
    return element



def odf_create_variable_get(name, value, value_type=None,
                            representation=None, style=None):
    data = u'<text:variable-get text:name="%s" />'
    element = odf_create_element(data % name)
    representation = _set_value_and_type(element, value=value,
                                         value_type=value_type,
                                         representation=representation)
    element.set_text(representation)
    if style is not None:
        element.set_attribute('style:data-style-name', style)
    return element



def odf_create_user_field_decls():
    return odf_create_element('<text:user-field-decls />')



def odf_create_user_field_decl(name, value, value_type=None):
    data = u'<text:user-field-decl text:name="%s"/>'
    element = odf_create_element(data % name)
    _set_value_and_type(element, value=value, value_type=value_type)
    return element



def odf_create_user_field_get(name, value, value_type=None,
                              representation=None, style=None):
    data = u'<text:user-field-get text:name="%s" />'
    element = odf_create_element(data % name)
    representation = _set_value_and_type(element, value=value,
                                         value_type=value_type,
                                         representation=representation)
    element.set_text(representation)
    if style is not None:
        element.set_attribute('style:data-style-name', style)
    return element



def odf_create_page_number_variable(select_page=None, page_adjust=None):
    """page_adjust is an integer to add (or subtract) to the page number

    select_page -- string in ('previous', 'current', 'next')

    page_adjust -- int
    """
    element = odf_create_element('<text:page-number/>')
    if select_page is None:
        select_page = 'current'
    element.set_attribute('text:select-page', select_page)
    if page_adjust is not None:
        element.set_attribute('text:page-adjust', str(page_adjust))
    return element



def odf_create_page_count_variable():
    return odf_create_element('<text:page-count />')



def odf_create_date_variable(date, fixed=False, data_style=None,
                             representation=None, date_adjust=None):
    data = '<text:date text:date-value="%s"/>'
    element = odf_create_element(data % DateTime.encode(date))
    if fixed:
        element.set_attribute('text:fixed', 'true')
    if data_style is not None:
        element.set_attribute('style:data-style-name', data_style)
    if representation is None:
        representation = Date.encode(date)
    element.set_text(representation)
    if date_adjust is not None:
        element.set_attribute('text:date-adjust',
                               Duration.encode(date_adjust))
    return element



def odf_create_time_variable(time, fixed=False, data_style=None,
                             representation=None, time_adjust=None):
    data = '<text:time text:time-value="%s"/>'
    element = odf_create_element(data % DateTime.encode(time))
    if fixed:
        element.set_attribute('text:fixed', 'true')
    if data_style is not None:
        element.set_attribute('style:data-style-name', data_style)
    if representation is None:
        representation = time.strftime('%H:%M:%S')
    element.set_text(representation)
    if time_adjust is not None:
        element.set_attribute('text:time-adjust',
                               Duration.encode(time_adjust))
    return element



def odf_create_chapter_variable(display='name', outline_level=None):
    """display can be: 'number', 'name', 'number-and-name', 'plain-number' or
                       'plain-number-and-name'
    """
    data = '<text:chapter text:display="%s"/>'
    element = odf_create_element(data % display)
    if outline_level is not None:
        element.set_attribute('text:outline-level', str(outline_level))
    return element



def odf_create_filename_variable(display='full', fixed=False):
    """display can be: 'full', 'path', 'name' or 'name-and-extension'
    """
    data = '<text:file-name text:display="%s"/>'
    element = odf_create_element(data % display)
    if fixed:
        element.set_attribute('text:fixed', 'true')
    return element



def odf_create_initial_creator_variable(fixed=False):
    element = odf_create_element('<text:initial-creator/>')
    if fixed:
        element.set_attribute('text:fixed', 'true')
    return element



def odf_create_creation_date_variable(fixed=False, data_style=None):
    element = odf_create_element('<text:creation-date/>')
    if fixed:
        element.set_attribute('text:fixed', 'true')
    if data_style is not None:
        element.set_attribute('style:data-style-name', data_style)
    return element



def odf_create_creation_time_variable(fixed=False, data_style=None):
    element = odf_create_element('<text:creation-time/>')
    if fixed:
        element.set_attribute('text:fixed', 'true')
    if data_style is not None:
        element.set_attribute('style:data-style-name', data_style)
    return element



def odf_create_description_variable(fixed=False):
    element = odf_create_element('<text:description/>')
    if fixed:
        element.set_attribute('text:fixed', 'true')
    return element



def odf_create_title_variable(fixed=False):
    element = odf_create_element('<text:title/>')
    if fixed:
        element.set_attribute('text:fixed', 'true')
    return element



def odf_create_subject_variable(fixed=False):
    element = odf_create_element('<text:subject/>')
    if fixed:
        element.set_attribute('text:fixed', 'true')
    return element



def odf_create_keywords_variable(fixed=False):
    element = odf_create_element('<text:keywords/>')
    if fixed:
        element.set_attribute('text:fixed', 'true')
    return element
