# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
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
from datetime import date, datetime, timedelta
from decimal import Decimal as dec
from os import getcwd
from os.path import splitdrive, join, sep
from re import search
from sys import _getframe, modules
from warnings import warn

# Import from lpod
from datatype import Boolean, Date, DateTime, Duration


CELL_TYPES = ('boolean', 'currency', 'date', 'float', 'percentage', 'string',
              'time')

STYLE_FAMILIES = ('paragraph', 'text', 'section', 'table', 'table-column',
                  'table-row', 'table-cell', 'table-page', 'chart',
                  'default', 'drawing-page', 'graphic', 'presentation',
                  'control', 'ruby', 'list', 'number', 'page-layout',
                  'presentation-page-layout', 'font-face', 'master-page')

NOTE_CLASSES = ('footnote', 'endnote')


######################################################################
# Private API
######################################################################

def _get_abspath(local_path):
    """Returns the absolute path to the required file.
    """

    mname = _getframe(1).f_globals.get('__name__')

    if mname == '__main__' or mname == '__init__':
        mpath = getcwd()
    else:
        module = modules[mname]
        if hasattr(module, '__path__'):
            mpath = module.__path__[0]
        elif '.' in mname:
            mpath = modules[mname[:mname.rfind('.')]].__path__[0]
        else:
            mpath = mname

    drive, mpath = splitdrive(mpath)
    mpath = drive + join(mpath, local_path)

    # Make it working with Windows. Internally we use always the "/".
    if sep == '\\':
        mpath = mpath.replace(sep, '/')

    return mpath



def _make_xpath_query(element_name, family=None, text_style=None,
        draw_id=None, draw_name=None, draw_style=None, draw_text_style=None,
        table_name=None, table_style=None, style_name=None,
        display_name=None, note_class=None, text_id=None, text_name=None,
        office_name=None, office_title=None, outline_level=None, level=None,
        page_layout=None, master_page=None, parent_style=None,
        position=None, **kw):
    query = [element_name]
    attributes = kw
    if text_style:
        attributes['text:style-name'] = text_style
    if family:
        attributes['style:family'] = family
    if draw_id:
        attributes['draw:id'] = draw_id
    if draw_name:
        attributes['draw:name'] = draw_name
    if draw_style:
        attributes['draw:style-name'] = draw_style
    if draw_text_style:
        attributes['draw:text-style-name'] = draw_text_style
    if table_name:
        attributes['table:name'] = table_name
    if table_style:
        attributes['table:style-name'] = table_style
    if style_name:
        attributes['style:name'] = style_name
    if display_name:
        attributes['style:display-name'] = display_name
    if note_class:
        attributes['text:note-class'] = note_class
    if text_id:
        attributes['text:id'] = text_id
    if text_name:
        attributes['text:name'] = text_name
    if office_name:
        attributes['office:name'] = office_name
    if office_title:
        attributes['office:title'] = office_title
    if outline_level:
        attributes['text:outline-level'] = outline_level
    if level:
        attributes['text:level'] = level
    if page_layout:
        attributes['style:page-layout-name'] = page_layout
    if master_page:
        attributes['draw:master-page-name'] = master_page
    if parent_style:
        attributes['style:parent-style-name'] = parent_style
    # Sort attributes for reproducible test cases
    for qname in sorted(attributes):
        value = attributes[qname]
        if value is True:
            query.append(u'[@%s]' % qname)
        else:
            query.append(u'[@%s="%s"]' % (qname, unicode(value)))
    query = ''.join(query)
    if position is not None:
        # A position argument that mimics the behaviour of a python's list
        if position >= 0:
            position = str(position + 1)
        elif position == -1:
            position = 'last()'
        else:
            position = 'last()-%d' % (abs(position) - 1)
        query = u'(%s)[%s]' % (query, position)
    return query



# These are listed exhaustively for keeping count of
# implemented style types
family_mapping = {
        'paragraph': ('style:style', 'paragraph'),
        'text': ('style:style', 'text'),
        'section': ('style:style', 'section'),
        'table': ('style:style', 'table'),
        'table-column': ('style:style', 'table-column'),
        'table-row': ('style:style', 'table-row'),
        'table-cell': ('style:style', 'table-cell'),
        'drawing-page': ('style:style', 'drawing-page'),
        'graphic': ('style:style', 'graphic'),
        'presentation': ('style:style', 'presentation'),
        # False families
        'list': ('text:list-style', None),
        'outline': ('text:outline-style', None),
        'page-layout': ('style:page-layout', None),
        'presentation-page-layout': ('style:presentation-page-layout', None),
        'master-page': ('style:master-page', None),
        'font-face': ('style:font-face', None),
        'number': ('number:number-style', None),
        'percentage': ('number:percentage-style', None),
        'time': ('number:time-style', None),
        'date': ('number:date-style', None),
}


def _get_style_tagname(family):
    if family not in family_mapping:
        raise ValueError, "unknown family: " + family
    return family_mapping[family]


def _get_style_family(name):
    for family, (tagname, famattr) in family_mapping.iteritems():
        if tagname == name:
            return family
    return None


def _expand_properties(properties):
    # This mapping is not exhaustive, it only contains cases where replacing
    # '_' with '-' and adding the "fo:" prefix is not enough
    mapping = {# text
               'font': 'style:font-name',
               'size': 'fo:font-size',
               'weight': 'fo:font-weight',
               'style': 'fo:font-style',
               'underline': 'style:text-underline-style',
               'display': 'text:display',
               # paragraph
               'align': 'fo:text-align',
               'align-last': 'fo:text-align-last',
               'indent': 'fo:text-indent',
               'together': 'fo:keep-together',
               # TODO 'page-break-before': 'fo:page-break-before',
               # TODO 'page-break-after': 'fo:page-break-after',
               'shadow': 'fo:text-shadow'}

    def map_key(key):
        key = mapping.get(key, key).replace('_', '-')
        if ":" not in key:
            key = "fo:" + key
        return key

    if type(properties) is dict:
        expanded = {}
        for key, value in properties.iteritems():
            key = map_key(key)
            expanded[key] = value
    elif type(properties) is list:
        expanded = []
        for key in properties:
            key = map_key(key)
            expanded.append(key)
    return expanded



def _merge_dicts(d, *args, **kw):
    """Merge two or more dictionaries into a new dictionary object.
    """
    new_d = d.copy()
    for dic in args:
        new_d.update(dic)
    new_d.update(kw)
    return new_d



#
# Non-public yet useful helpers
#

def _get_elements(context, element_name, content=None, href=None,
        svg_title=None, svg_desc=None, dc_creator=None, dc_date=None, **kw):
    query = _make_xpath_query(element_name, **kw)
    elements = context.get_elements(query)
    # Filter the elements with the regex (TODO use XPath)
    if content is not None:
        elements = [element for element in elements if element.match(content)]
    if href is not None:
        filtered = []
        for element in elements:
            href_attr = element.get_attribute('xlink:href')
            if search(href, href_attr) is not None:
                filtered.append(element)
        elements = filtered
    if dc_date is not None:
        # XXX Date or DateTime?
        dc_date = DateTime.encode(dc_date)
    for variable, childname in [
            (svg_title, 'svg:title'),
            (svg_desc, 'svg:desc'),
            (dc_creator, 'descendant::dc:creator'),
            (dc_date, 'descendant::dc:date')]:
        if not variable:
            continue
        filtered = []
        for element in elements:
            child = element.get_element(childname)
            if child and child.match(variable):
                filtered.append(element)
        elements = filtered
    return elements



def _get_element(context, element_name, position, **kw):
    # TODO Transmit position not to load the whole list
    result = _get_elements(context, element_name, **kw)
    try:
        return result[position]
    except IndexError:
        return None



def _set_value_and_type(element, value=None, value_type=None, text=None,
        currency=None):
    # Remove possible previous value and type
    for name in ('office:value-type', 'office:boolean-value',
            'office:value', 'office:date-value', 'office:string-value',
            'office:time-value'):
        try:
            element.del_attribute(name)
        except KeyError:
            pass
    if type(value) is bool:
        if value_type is None:
            value_type = 'boolean'
        if text is None:
            text = u'true' if value else u'false'
        value = Boolean.encode(value)
    elif isinstance(value, (int, float, dec)):
        if value_type is None:
            value_type = 'float'
        if text is None:
            text = unicode(value)
        value = str(value)
    elif type(value) is date:
        if value_type is None:
            value_type = 'date'
        if text is None:
            text = unicode(Date.encode(value))
        value = Date.encode(value)
    elif type(value) is datetime:
        if value_type is None:
            value_type = 'date'
        if text is None:
            text = unicode(DateTime.encode(value))
        value = DateTime.encode(value)
    elif type(value) is str:
        if value_type is None:
            value_type = 'string'
        if text is None:
            text = unicode(value)
    elif type(value) is unicode:
        if value_type is None:
            value_type = 'string'
        if text is None:
            text = value
    elif type(value) is timedelta:
        if value_type is None:
            value_type = 'time'
        if text is None:
            text = unicode(Duration.encode(value))
        value = Duration.encode(value)
    elif value is not None:
        raise TypeError, 'type "%s" is unknown' % type(value)

    if value_type is not None:
        element.set_attribute('office:value-type', value_type)

    if value_type == 'boolean':
        element.set_attribute('office:boolean-value', value)
    elif value_type == 'currency':
        element.set_attribute('office:value', value)
        element.set_attribute('office:currency', currency)
    elif value_type == 'date':
        element.set_attribute('office:date-value', value)
    elif value_type in ('float', 'percentage'):
        element.set_attribute('office:value', value)
    elif value_type == 'string':
        element.set_attribute('office:string-value', value)
    elif value_type == 'time':
        element.set_attribute('office:time-value', value)

    return text



######################################################################
# Public API
######################################################################
def get_value(element, value_type=None, try_get_text=True):
    """Only for "with office:value-type" elements
    """

    if value_type is None:
        value_type = element.get_attribute('office:value-type')

    if value_type == 'boolean':
        value = element.get_attribute('office:boolean-value')
        return Boolean.decode(value)
    elif value_type in  ('float', 'percentage', 'currency'):
        value = dec(element.get_attribute('office:value'))
        # Return 3 instead of 3.0 if possible
        if int(value) == value:
            return int(value)
        return value
    elif value_type == 'date':
        value = element.get_attribute('office:date-value')
        if 'T' in value:
            return DateTime.decode(value)
        else:
            return Date.decode(value)
    elif value_type == 'string':
        value = element.get_attribute('office:string-value')
        if value is not None:
            return unicode(value)
        if try_get_text:
            value = element.get_text()
            if value != '':
                return value
        return None

    elif value_type == 'time':
        value = element.get_attribute('office:time-value')
        return Duration.decode(value)
    elif value_type is None:
        return None

    raise ValueError, 'unexpected value type "%s"' % value_type



def set_value(element, value):
    """Only for "with office:value-type" elements
    """
    tag = element.get_tag()
    # A table:cell ?
    if tag == 'table:table-cell':
        element.clear()
        text = _set_value_and_type(element, value=value)
        element.set_text_content(text)
        return
    # A text:variable-set ?
    if tag == 'text:variable-set':
        name = element.get_attribute('text:name')
        display = element.get_attribute('text:display')
        element.clear()
        text = _set_value_and_type(element, value=value)
        element.set_attribute('text:name', name)
        if display is not None:
            element.set_attribute('text:display', display)
        element.set_text(text)
        return
    # A text:user-field-decl ?
    if tag == 'text:user-field-decl':
        name = element.get_attribute('text:name')
        element.clear()
        _set_value_and_type(element, value=value)
        element.set_attribute('text:name', name)
        return
    # Else => error
    raise ValueError, 'set_value: unexpected element "%s"' % tag



def convert_unicode(text):
    """Mostly used to compare lxml serialization to what is expected.
    """
    result = []
    for c in text:
        code = ord(c)
        if code >= 128:
            result.append('&#%d;' % code)
        else:
            result.append(c)
    return ''.join(result)



def oooc_to_ooow(formula):
    """Convert (proprietary) formula from calc format to writer format.

    Arguments:

        formula -- unicode

    Return: unicode
    """
    prefix, formula = formula.split(":=", 1)
    assert "oooc" in prefix
    # Convert cell addresses
    formula = formula.replace("[.", "<").replace(":.", ":").replace("]", ">")
    # Convert functions
    formula = formula.replace("SUM(", "sum ").replace(")", "")
    return "ooow:" + formula



def obsolete(old_name, new_func):
    def decorate(*args, **kwargs):
        new_name = new_func.__name__
        message = '"%s" is obsolete, call "%s" instead' % (old_name,
                new_name)
        warn(message, category=DeprecationWarning)
    return decorate
