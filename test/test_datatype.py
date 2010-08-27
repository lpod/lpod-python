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
from unittest import TestCase, main

# Import from lpod
from lpod.datatype import DateTime, Duration, Boolean


class DateTimeTestCase(TestCase):

    def test_encode(self):
        date = datetime(2009, 06, 26, 11, 9, 36)
        expected = '2009-06-26T11:09:36'
        self.assertEqual(DateTime.encode(date), expected)


    def test_decode(self):
        date = '2009-06-29T14:33:21'
        expected = datetime(2009, 6, 29, 14, 33, 21)
        self.assertEqual(DateTime.decode(date), expected)



class DurationTestCase(TestCase):

    def test_encode(self):
        duration = timedelta(0, 53, 0, 0, 6)
        expected = 'PT00H06M53S'
        self.assertEqual(Duration.encode(duration), expected)


    def test_decode(self):
        duration = 'PT12H34M56S'
        expected = timedelta(0, 56, 0, 0, 34, 12)
        self.assertEqual(Duration.decode(duration), expected)



class BooleanTestCase(TestCase):

    def test_encode(self):
        self.assertEqual(Boolean.encode(True), 'true')
        self.assertEqual(Boolean.encode(False), 'false')
        self.assertEqual(Boolean.encode("true"), 'true')
        self.assertEqual(Boolean.encode("false"), 'false')


    def test_bad_encode(self):
        self.assertRaises(TypeError, Boolean.encode, 'on')
        self.assertRaises(TypeError, Boolean.encode, 1)


    def test_decode(self):
        self.assertEqual(Boolean.decode('true'), True)
        self.assertEqual(Boolean.decode('false'), False)


    def test_bad_decode(self):
        self.assertRaises(ValueError, Boolean.decode, 'True')
        self.assertRaises(ValueError, Boolean.decode, '1')



if __name__ == '__main__':
    main()
