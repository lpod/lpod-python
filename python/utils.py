# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from datetime import datetime

# Import from lpod


DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'


CELL_TYPES = ('boolean', 'currency', 'date', 'float', 'percentage', 'string',
              'time')

STYLE_FAMILIES = ('paragraph', 'text', 'section', 'table', 'tablecolumn',
                  'table-row', 'table-cell', 'table-page', 'chart',
                  'default', 'drawing-page', 'graphic', 'presentation',
                  'control', 'ruby')

NOTE_CLASSES = ('footnote', 'endnote')



def _generate_xpath_query(element_name, attributes={}, position=None,
                          context=None):
    if context is None:
        query = ['//']
    else:
        query = []
    query.append(element_name)
    # Sort attributes for reproducible test cases
    for qname in sorted(attributes):
        value = attributes[qname]
        if value is not None:
            query.append('[@{qname}="{value}"]'.format(qname=qname,
                                                      value=str(value)))
        else:
            query.append('[@{qname}]'.format(qname=qname))
    if position is not None:
        query.append('[{position}]'.format(position=str(position)))
    return ''.join(query)


def _get_cell_coordinates(name):
    lower = name.lower()

    # First "x"
    x = 0
    for p in xrange(len(lower)):
        c = lower[p]
        if not c.isalpha():
            break
        v = ord(c) - ord('a') + 1
        x = x * 26 + v
    if x == 0:
        raise ValueError, 'cell name "%s" is malformed' % name

    # And "y"
    try:
        y = int(lower[p:])
    except ValueError:
        raise ValueError, 'cell name "%s" is malformed' % name
    if y <= 0:
        raise ValueError, 'cell name "%s" is malformed' % name

    return x, y


def _check_arguments(context=None, element=None, xmlposition=None,
                     position=None, level=None, text=None, style=None,
                     family=None, cell_type=None, currency=None,
                     note_class=None, creator=None, date=None,
                     start_date=None, end_date=None, offset=None):
    if context is not None:
        # FIXME cyclic import
        from xmlpart import odf_element
        if not isinstance(context, odf_element):
            raise TypeError, "context must be an odf element"
    if element is not None:
        # FIXME cyclic import
        from xmlpart import odf_element
        if not isinstance(element, odf_element):
            raise TypeError, "element must be an odf element"
    if xmlposition is not None:
        # FIXME cyclic import
        from xmlpart import STOPMARKER
        if type(xmlposition) is not int or xmlposition >= STOPMARKER:
            raise ValueError, "invalid XML position"
    if position is not None:
        if type(position) is not int:
            raise TypeError, "an integer position is expected"
        if position < 1:
            raise ValueError, "position count begin at 1"
    if level is not None:
        if not isinstance(level, int):
            raise TypeError, "an integer level is expected"
        if level < 1:
            raise ValueError, "level count begin at 1"
    if text is not None:
        if type(text) is not unicode:
            raise TypeError, "text must be an unicode string"
    if style is not None:
        if type(style) is not str:
            raise TypeError, "a style name is expected"
    if family is not None:
        if not family in STYLE_FAMILIES:
            raise ValueError, '"%s" is not a valid style family' % family
    if cell_type is not None:
        if not cell_type in CELL_TYPES:
            raise ValueError, '"%s" is not a valid cell type' % cell_type
        if cell_type == 'currency':
            if currency is None:
                raise ValueError, 'currency is mandatory in monetary cells'
            if type(currency) is not str:
                raise TypeError, 'currency must be a three-letter code'
    if note_class is not None:
        if not note_class in NOTE_CLASSES:
            raise ValueError, '"%s" is not a valid note class' % note_class
    if creator is not None:
        if type(creator) is not unicode:
            raise TypeError, "creator must be an unicode string"
    if date is not None:
        if type(date) is not datetime:
            raise TypeError, "date must be a datetime object"
    if start_date is not None:
        if type(start_date) is not datetime:
            raise TypeError, "start date must be a datetime object"
    if end_date is not None:
        if type(end_date) is not datetime:
            raise TypeError, "end date must be a datetime object"
    if offset is not None:
        if type(offset) is not int:
            raise TypeError, "offset must be an integer"



def _check_position_or_name(position, name):
    if not ((position is None) ^ (name is None)):
        raise ValueError, 'You must choose either position or name'
