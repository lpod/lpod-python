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
        if value is True or str(value).lower() == "true":
            return "true"
        elif value is False or str(value).lower() == "false":
            return "false"
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
        if data.startswith('P'):
            sign = 1
        elif data.startswith('-P'):
            sign = -1
        else:
            raise ValueError, "duration not valid"

        days = 0
        hours = 0
        minutes = 0
        seconds = 0

        buffer = ''
        for c in data:
            if c.isdigit():
                buffer += c
            elif c == 'D':
                days = int(buffer)
                buffer = ''
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
            raise ValueError, "duration not valid"

        return timedelta(days=sign*days,
                         hours=sign*hours,
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
