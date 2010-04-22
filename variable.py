# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Hervé Cauwelier <herve@itaapy.com>
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

# Import from lpod
from datatype import Date, DateTime, Duration
from utils import _set_value_and_type
from element import odf_create_element


def odf_create_variable_decls():
    return odf_create_element('text:variable-decls')



def odf_create_variable_decl(name, value_type):
    element = odf_create_element('text:variable-decl')
    element.set_attribute('office:value-type', value_type)
    element.set_attribute('text:name', name)
    return element



def odf_create_variable_set(name, value, value_type=None, display=False,
        text=None, style=None):
    element = odf_create_element('text:variable-set')
    element.set_attribute('text:name', name)
    text = _set_value_and_type(element, value=value, value_type=value_type,
            text=text)
    if not display:
        element.set_attribute('text:display', 'none')
    else:
        element.set_text(text)
    if style is not None:
        element.set_attribute('style:data-style-name', style)
    return element



def odf_create_variable_get(name, value, value_type=None, text=None,
        style=None):
    element = odf_create_element('text:variable-get')
    element.set_attribute('text:name', name)
    text = _set_value_and_type(element, value=value, value_type=value_type,
            text=text)
    element.set_text(text)
    if style is not None:
        element.set_attribute('style:data-style-name', style)
    return element



def odf_create_user_field_decls():
    return odf_create_element('text:user-field-decls>')



def odf_create_user_field_decl(name, value, value_type=None):
    element = odf_create_element('text:user-field-decl')
    element.set_attribute('text:name', name)
    _set_value_and_type(element, value=value, value_type=value_type)
    return element



def odf_create_user_field_get(name, value, value_type=None, text=None,
        style=None):
    element = odf_create_element('text:user-field-get')
    element.set_attribute('text:name', name)
    text = _set_value_and_type(element, value=value, value_type=value_type,
            text=text)
    element.set_text(text)
    if style is not None:
        element.set_attribute('style:data-style-name', style)
    return element



def odf_create_page_number_variable(select_page=None, page_adjust=None):
    """page_adjust is an integer to add (or subtract) to the page number

    select_page -- string in ('previous', 'current', 'next')

    page_adjust -- int
    """
    element = odf_create_element('text:page-number')
    if select_page is None:
        select_page = 'current'
    element.set_attribute('text:select-page', select_page)
    if page_adjust is not None:
        element.set_attribute('text:page-adjust', str(page_adjust))
    return element



def odf_create_page_count_variable():
    return odf_create_element('text:page-count')



def odf_create_date_variable(date, fixed=False, data_style=None, text=None,
        date_adjust=None):
    element = odf_create_element('text:date')
    element.set_attribute('text:date-value', DateTime.encode(date))
    if fixed:
        element.set_attribute('text:fixed', 'true')
    if data_style is not None:
        element.set_attribute('style:data-style-name', data_style)
    if text is None:
        text = Date.encode(date)
    element.set_text(text)
    if date_adjust is not None:
        element.set_attribute('text:date-adjust',
                               Duration.encode(date_adjust))
    return element



def odf_create_time_variable(time, fixed=False, data_style=None, text=None,
        time_adjust=None):
    element = odf_create_element('text:time')
    element.set_attribute('text:time-value', DateTime.encode(time))
    if fixed:
        element.set_attribute('text:fixed', 'true')
    if data_style is not None:
        element.set_attribute('style:data-style-name', data_style)
    if text is None:
        text = time.strftime('%H:%M:%S')
    element.set_text(text)
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
    element = odf_create_element('text:initial-creator')
    if fixed:
        element.set_attribute('text:fixed', 'true')
    return element



def odf_create_creation_date_variable(fixed=False, data_style=None):
    element = odf_create_element('text:creation-date')
    if fixed:
        element.set_attribute('text:fixed', 'true')
    if data_style is not None:
        element.set_attribute('style:data-style-name', data_style)
    return element



def odf_create_creation_time_variable(fixed=False, data_style=None):
    element = odf_create_element('text:creation-time')
    if fixed:
        element.set_attribute('text:fixed', 'true')
    if data_style is not None:
        element.set_attribute('style:data-style-name', data_style)
    return element



def odf_create_description_variable(fixed=False):
    element = odf_create_element('text:description')
    if fixed:
        element.set_attribute('text:fixed', 'true')
    return element



def odf_create_title_variable(fixed=False):
    element = odf_create_element('text:title')
    if fixed:
        element.set_attribute('text:fixed', 'true')
    return element



def odf_create_subject_variable(fixed=False):
    element = odf_create_element('text:subject')
    if fixed:
        element.set_attribute('text:fixed', 'true')
    return element



def odf_create_keywords_variable(fixed=False):
    element = odf_create_element('text:keywords')
    if fixed:
        element.set_attribute('text:fixed', 'true')
    return element
