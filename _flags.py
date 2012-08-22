# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2012 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Jerome Dumonteil <jerome.dumonteil@itaapy.com>
#
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
"""
Options flags management for Lpod. Internal use of the library.
"""


# some singleton boolean frame
# default is False
class Flag:
    """
    A boolean object.
    """
    def __init__(self, value=False):
        self.__flag = bool(value)

    def set(self, value):
        self.__flag = bool(value)

    def __repr__(self):
        return '<lpod flag> %s' % self.__flag

    def __bool__(self):
        return self.__flag

    __nonzero__ = __bool__



legacy = Flag(False)

future = Flag(False)

experimental = Flag(False)
