.. Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.

   Authors: Hervé Cauwelier <herve@itaapy.com>
            Luis Belmar-Letelier <luis@itaapy.com>
            David Versmisse <david.versmisse@itaapy.com>

   This file is part of Lpod (see: http://lpod-project.org).
   Lpod is free software; you can redistribute it and/or modify it under
   the terms of either:

   a) the GNU General Public License as published by the Free Software
      Foundation, either version 3 of the License, or (at your option)
      any later version.
      Lpod is distributed in the hope that it will be useful,
      but WITHOUT ANY WARRANTY; without even the implied warranty of
      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
      GNU General Public License for more details.
      You should have received a copy of the GNU General Public License
      along with Lpod.  If not, see <http://www.gnu.org/licenses/>.

   b) the Apache License, Version 2.0 (the "License");
      you may not use this file except in compliance with the License.
      You may obtain a copy of the License at
      http://www.apache.org/licenses/LICENSE-2.0

#################
Metadata Cookbook
#################

.. contents::
   :local:

To illustrate metadata introspection, let's open an existing document::

    >>> from lpod.document import odf_get_document
    >>> document = odf_get_document('http://example.com/odf/cookbook')

Metadata are accessible through the `meta` part::

    >>> meta = document.get_meta()

You then get access to various getters and setters.

The getters return Python types and the respective setters take the same
Python type as a parameter.

Accessing properties
====================

The API has the form `get_xxx` and `set_xxx(value)`.

Example of getting the title::

    >>> meta.get_title()
    Example Document for the Cookbook
    >>> type(meta.get_title())
    <type 'unicode'>

Example of setting the title::

    >>> meta.set_title(u"First Example of a Long Series")

Notice that LpOD doesn't increment editing cycles nor statistics when saving
the document.

Properties helpers
==================

For the metadata using dates or durations, lpOD provides datatypes that
decode from and serialize back to strings.

Example for dates::

    >>> from lpod.datatype import DateTime
    >>> modification_date = DateTime.decode('2009-11-17T12:02:49')
    >>> type(modification_date)
    <type 'datetime.datetime'>
    >>> metadata.set_modification_date(modification_date)

Example for durations::

    >>> from lpod.datatype import Duration
    >>> duration = Duration.decode('PT00H03M02S')
    >>> type(duration)
    <type 'datetime.timedelta'>
    >>> meta.set_editing_duration(duration)

Of course you can use the datetime and timedelta constructors instead.

User-defined metadata
=====================

The ODF specification reserved place for free-form metadata for the user to
fill in.

They are loaded as a dict::

    >>> meta.get_user_defined_metadata()::
    {}

You are allowed to store the following Python types: str, unicode, bool, int,
float, Decimal, date, datetime, timedelta::

    >>> meta.set_user_defined_metadata(u"lpOD Version", 'v0.7-67-g24c08f4')
    >>> meta.get_user_defined_metadata()
    {u'lpOD Version': u'v0.7-67-g24c08f4'}

Strings are always decoded as unicode, numeric values are always decoded as
Decimal (as they offer the best precision).

For the whole list of metadata, consult the :doc:`lpod.meta module
<autodocs/meta>`.
