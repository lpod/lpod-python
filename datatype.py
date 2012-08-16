# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
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
from decimal import Decimal


DATE_FORMAT = '%Y-%m-%d'


DATETIME_FORMAT = DATE_FORMAT + 'T%H:%M:%S'
DATETIME_FORMAT_MICRO = DATETIME_FORMAT + '.%f'


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
        # XXX "Z" means a UTC datetime, convert it ??
        # Cf http://en.wikipedia.org/wiki/ISO_8601
        if data.endswith('Z'):
            data = data[:-1]
        try:
            return datetime.strptime(data, DATETIME_FORMAT_MICRO)
        except ValueError:
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
                buffer = ''
                break
        if buffer != '':
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


# I chose not to inherit from Decimal to avoid operations on different units
class Unit(object):

    def __init__(self, value, unit='cm'):
        if isinstance(value, basestring):
            digits = []
            nondigits = []
            for char in value:
                if char.isdigit() or char == '.':
                    digits.append(char)
                else:
                    nondigits.append(char)
            value = ''.join(digits)
            if nondigits:
                unit = ''.join(nondigits)
        elif isinstance(value, float):
            value = str(value)
        self.value = Decimal(value)
        self.unit = unit


    def __str__(self):
        return str(self.value) + self.unit


    def __repr__(self):
        return "%s %s" % (object.__repr__(self), self)


    def __cmp__(self, other):
        if type(other) is not type(self):
            raise ValueError, "can only compare Unit"
        if self.unit != other.unit:
            raise NotImplementedError, "no conversion yet"
        return cmp(self.value, other.value)


    def convert(self, unit, dpi=72):
        if unit == 'px':
            if self.unit == 'in':
                return Unit(int(self.value * dpi), 'px')
            elif self.unit == 'cm':
                return Unit(int(self.value / Decimal('2.54') * dpi), 'px')
            raise NotImplementedError, self.unit
        raise NotImplementedError, unit
