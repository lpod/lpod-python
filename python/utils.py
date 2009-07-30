# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from datetime import date, datetime, timedelta
from decimal import Decimal
from os import getcwd
from os.path import splitdrive, join, sep
from sys import _getframe, modules


DATE_FORMAT = '%Y-%m-%d'


DATETIME_FORMAT = DATE_FORMAT + 'T%H:%M:%S'


DURATION_FORMAT = 'PT%02dH%02dM%02dS'


CELL_TYPES = ('boolean', 'currency', 'date', 'float', 'percentage', 'string',
              'time')

STYLE_FAMILIES = ('paragraph', 'text', 'section', 'table', 'table-column',
                  'table-row', 'table-cell', 'table-page', 'chart',
                  'default', 'drawing-page', 'graphic', 'presentation',
                  'control', 'ruby', 'page-layout')

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



def _make_xpath_query(element_name, style=None, family=None, draw_name=None,
                      draw_style=None, table_name=None, style_name=None,
                      note_class=None, text_id=None, text_name=None,
                      level=None, position=None, context=None, **kw):
    if context is None:
        query = ['//']
    else:
        query = []
    query.append(element_name)
    attributes = kw
    if style:
        attributes['text:style-name'] = style
    if family:
        attributes['style:family'] = family
    if draw_name:
        attributes['draw:name'] = draw_name
    if draw_style:
        attributes['draw:style-name'] = draw_style
    if table_name:
        attributes['table:name'] = table_name.encode('utf_8')
    if style_name:
        attributes['style:name'] = style_name
    if note_class:
        attributes['text:note-class'] = note_class
    if text_id:
        attributes['text:id'] = text_id
    if text_name:
        attributes['text:name'] = text_name
    if level:
        attributes['text:outline-level'] = level
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



def _get_cell_coordinates(obj):
    # By values ?
    if isinstance(obj, (list, tuple)):
        return tuple(obj)

    # Or by 'B3' notation ?
    if not isinstance(obj, (str, unicode)):
        raise ValueError, ('_get_cell_coordinates called with a bad argument '
                'type: "%s"' % type(obj))

    lower = obj.lower()

    # First "x"
    x = 0
    for p in xrange(len(lower)):
        c = lower[p]
        if not c.isalpha():
            break
        v = ord(c) - ord('a') + 1
        x = x * 26 + v
    if x == 0:
        raise ValueError, 'cell name "%s" is malformed' % obj

    # And "y"
    try:
        y = int(lower[p:])
    except ValueError:
        raise ValueError, 'cell name "%s" is malformed' % obj
    if y <= 0:
        raise ValueError, 'cell name "%s" is malformed' % obj

    return x, y



def _check_position_or_name(position, name):
    if not ((position is None) ^ (name is None)):
        raise ValueError, 'You must choose either position or name'



class Date(object):

    @staticmethod
    def decode(data):
        return datetime.strptime(data, DATE_FORMAT)


    @staticmethod
    def encode(value):
        return value.strftime(DATE_FORMAT)



class DateTime(object):

    @staticmethod
    def decode(data):
        return datetime.strptime(data, DATETIME_FORMAT)


    @staticmethod
    def encode(value):
        return value.strftime(DATETIME_FORMAT)



class Duration(object):
    """ISO 8601 format.
    """

    @staticmethod
    def decode(data):
        if data.startswith('PT'):
            sign = 1
        elif data.startswith('-PT'):
            sign = -1
        else:
            raise ValueError, "duration is not '%s" % DURATION_FORMAT

        hours = 0
        minutes = 0
        seconds = 0

        buffer = ''
        for c in data:
            if c.isdigit():
                buffer += c
            elif c == 'H':
                hours = int(buffer)
                buffer = ''
            elif c == 'M':
                minutes = int(buffer)
                buffer = ''
            elif c == 'S':
                seconds = int(buffer)
                break
        else:
            raise ValueError, "duration is not '%s" % DURATION_FORMAT

        return timedelta(hours=sign*hours,
                         minutes=sign*minutes,
                         seconds=sign*seconds)


    @staticmethod
    def encode(value):
        if type(value) is not timedelta:
            raise TypeError, "duration must be a timedelta"

        days = value.days
        if days < 0:
            microseconds = -((days * 24 * 60 *60 + value.seconds) * 1000000 +
                             value.microseconds)
            sign = '-'
        else:
            microseconds = ((days * 24 * 60 *60 + value.seconds) * 1000000 +
                             value.microseconds)
            sign = ''

        hours = microseconds / ( 60 * 60 * 1000000)
        microseconds %= 60 * 60 * 1000000

        minutes = microseconds / ( 60 * 1000000)
        microseconds %= 60 * 1000000

        seconds = microseconds / 1000000

        return sign + DURATION_FORMAT % (hours, minutes, seconds)



class Boolean(object):

    @staticmethod
    def decode(data):
        if data == 'true':
            return True
        elif data == 'false':
            return False
        raise ValueError, 'boolean "%s" is invalid' % data


    @staticmethod
    def encode(value):
        if value is True:
            return 'true'
        elif value is False:
            return 'false'
        raise TypeError, '"%s" is not a boolean' % value


def _set_value_and_type(element, value=None, value_type=None,
                        representation=None, currency=None):
    if type(value) is bool:
        if value_type is None:
            value_type = 'boolean'
        if representation is None:
            representation = u'true' if value else u'false'
        value = Boolean.encode(value)
    elif isinstance(value, (int, float, Decimal)):
        if value_type is None:
            value_type = 'float'
        if representation is None:
            representation = unicode(value)
        value = str(value)
    elif type(value) is date:
        if value_type is None:
            value_type = 'date'
        if representation is None:
            representation = unicode(Date.encode(value))
        value = Date.encode(value)
    elif type(value) is datetime:
        if value_type is None:
            value_type = 'date'
        if representation is None:
            representation = unicode(DateTime.encode(value))
        value = DateTime.encode(value)
    elif type(value) is str:
        if value_type is None:
            value_type = 'string'
        if representation is None:
            representation = unicode(value)
    elif type(value) is unicode:
        if value_type is None:
            value_type = 'string'
        if representation is None:
            representation = value
        value = value.encode('utf_8')
    elif type(value) is timedelta:
        if value_type is None:
            value_type = 'time'
        if representation is None:
            representation = unicode(Duration.encode(value))
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

    return representation



# Place here to avoid a cyclic import
from xmlpart import odf_element
def _get_text(current, context):

    result = []
    for element in current.get_children():

        tag = element.get_name()

        # Heading
        if tag == 'text:h':
            result.append(u'\n')
            result.append(element.get_text())
            result.append(u'\n')

        # Paragraph
        elif tag == 'text:p':
            for obj in element.xpath('text:span|text:a|text:note|text()'):
                if isinstance(obj, odf_element):
                    # A note
                    if obj.get_name() == 'text:note':
                        context['notes_counter'] += 1
                        notes_counter = context['notes_counter']
                        text = obj.get_element('text:note-body').get_text()
                        text = text.strip()

                        if obj.get_attribute('text:note-class') == 'footnote':
                            context['footnotes'].append((notes_counter, text))
                            result.append('[%d]' % notes_counter)
                        else:
                            context['endnotes'].append((notes_counter, text))
                            result.append('(%d)' % notes_counter)
                    # An other element
                    else:
                        result.append(obj.get_text())
                else:
                    result.append(obj)

            # Insert the footnotes
            result.append(u'\n')
            for note in context['footnotes']:
                result.append(u'[%d] %s\n' % note)
            context['footnotes'] = []

        # Look the descendants
        else:
            result.append(_get_text(element, context))

    return u''.join(result)



######################################################################
# Public API
######################################################################
def get_value(element, value_type=None):
    """Only for "with office:value-type" elements
    """

    if value_type is None:
        value_type = element.get_attribute('office:value-type')

    if value_type == 'boolean':
        value = element.get_attribute('office:boolean-value')
        return Boolean.decode(value)
    elif value_type in  ('float', 'percentage', 'currency'):
        value = element.get_attribute('office:value')
        return float(value)
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
        else:
            # Try with get_text
            value = element.get_text()
            if value != '':
                return value
            else:
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

    tag = element.get_name()

    # A table:cell ?
    if tag == 'table:table-cell':
        element.clear()
        representation = _set_value_and_type(element, value=value)
        element.set_text_content(representation)
        return

    # A text:variable-set ?
    if tag == 'text:variable-set':
        name = element.get_attribute('text:name')
        display = element.get_attribute('text:display')
        element.clear()

        representation = _set_value_and_type(element, value=value)

        element.set_attribute('text:name', name)
        if display is not None:
            element.set_attribute('text:display', display)
        element.set_text(representation)
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
