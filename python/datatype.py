# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from datetime import datetime, timedelta


DATE_FORMAT = '%Y-%m-%d'


DATETIME_FORMAT = DATE_FORMAT + 'T%H:%M:%S'


DURATION_FORMAT = 'PT%02dH%02dM%02dS'



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
