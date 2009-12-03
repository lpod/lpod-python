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

- Open an existing document::

    >>> from lpod.document import odf_get_document
    >>> document = odf_get_document('http://example.com/odf/cookbook')

- Access the metadata part::

    >>> meta = document.get_meta()

You then get the list of getters and setters.

- Most of them return unicode::

    >>> meta.get_title()
    Example Document for the Cookbook
    >>> meta.get_description()
    >>> meta.get_subject()
    >>> meta.get_language()
    >>> meta.get_initial_creator()
    >>> meta.get_keyword()
    >>> meta.get_generator()
    LpOD Project v0.7-67-g24c08f4

- They accept unicode in return::

    >>> meta.set_title(u"First Example of a Long Series")

- Some return int::

    >>> meta.get_editing_cycles()
    2

- They accept int in return::

    >>> meta.set_editing_cycles(3)

- Some return dict::

    >>> meta.get_statistic()
    {'meta:word-count': 63, 'meta:image-count': 0, 'meta:object-count': 0,
    'meta:page-count': 3, 'meta:character-count': 273, 'meta:paragraph-count':
    25, 'meta:table-count': 2}

- They accept dict of the same form::

    >>> stat = meta.get_statistic()
    # ... update stat
    >>> meta.set_statistic(stat)

- Some return datetime object::

    >>> meta.get_modification_date()
    datetime.datetime(2009, 8, 25, 15, 40, 28)
    >>> meta.get_creation_date()
    datetime.datetime(2009, 7, 11, 15, 21, 27)

- So they need datetime object in return::

    >>> from datetime import datetime
    >>> metadata.set_modification_date(datetime.now())

- There is an helper for manipulating dates::

    >>> from lpod.datatype import DateTime
    >>> metadata.set_modification_date(DateTime.decode('2009-11-17T12:02:49'))

- Other return timedelta object::

    >>> meta.get_editing_duration()
    >>> datetime.timedelta(0, 174)

- So they need timedelta object in return::

    >>> from datetime import timedelta
    >>> meta.set_editing_duration(timedelta(seconds=182))

- There is an helper for this too::

    >>> from lpod.datatype import Duration
    >>> meta.set_editing_duration(Duration.encode('PT00H03M02S')

- There are finally user-defined metadata (generally unused)::

    >>> meta.get_user_defined_metadata()::
    {}

- Free for you to store str, unicode, bool, int, float, Decimal, date,
  datetime, timedelta::

    >>> meta.set_user_defined_metadata('lpod-version', 'v0.7-67-g24c08f4')
    >>> meta.get_user_defined_metadata()
    {u'lpod-version': u'v0.7-67-g24c08f4'}

Strings are always decoded as unicode, numeric values are always decoded as
Decimal.
