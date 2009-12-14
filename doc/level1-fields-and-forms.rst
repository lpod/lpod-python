.. Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.

   Authors: Hervé Cauwelier <herve@itaapy.com>
            Jean-Marie Gouarné <jean-marie.gouarne@arsaperta.com>
            Luis Belmar-Letelier <luis@itaapy.com>

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


Text Fields
===========

.. contents::
   :local:

A `text field` is a special text area, generally short-sized, whose content may
be automatically set, changed or checked by an interactive editor or viewer
according to a calculation formula and/or an information coming from somewhere
in the environment.

A table cell may be regarded as an example of field, according to such a
definition. However, while a table cell is always part of a table row that is in
turn an element in a table, a `text field` may be inserted anywhere in the
content of a text paragraph.

Common field-related features [tbc]
-----------------------------------

Field creation
~~~~~~~~~~~~~~

A text field is created "in place" using the ``set_field()`` element-based
method from a text container that may be a paragraph, a heading or a span.
This method works in a similar way as ``set_bookmark()`` or ``set_index_mark()``
introduced in the Text Marks and Indices section.

By default, the field is created and inserted  before the first character of
the content in the calling element. As an example, this instruction creates
a ``title`` field (whose role is to display the title of the document) before
the first character of a paragraph::

  paragraph.set_field("title")

A field may be positioned at any place in the text of the host container; to do
so, an optional ``position`` parameter, whose value is offset of the target,
may be provided. The value of this parameter is either a positive position,
zero-based and counted from the beginning, or a negative position counted from
the end. The following example puts a ``title`` field at the fifth position and
a ``subject`` field 5 characters before the end::

  paragraph.set_field("title", 4)
  paragraph.set_field("subject", -5)

The ``set_field()`` method allows field positioning at a position that depends
on the content of the target, instead of a position. Thanks to a ``before`` or
a ``after`` parameter, it's possible to provide a regexp that tells
to insert the new field just before of after the first substring that
matches a given filter ``set_field()``. The next example inserts the name of
the initial creator of the document after a given string::

  paragraph.set_field("initial creator", after="and the winner is ")

If ``position`` is provided with ``after`` or ``before``, any substring before
the given position is ignored, even if it matches the string filter, so the
field is inserted after the position, or not inserted. In addition, it's
possible to combine ``before`` and ``after``; in such a situation, the field is
inserted between the two substrings that respectively match the two filters,
and only if these substrings are contiguous and in the right order.

``set_field()`` returns the created ODF element in case of success, or null if
(due to the given parameters and the content of the target container) the field
can't be created.

Document fields [todo]
----------------------


Declared fields and variables [todo]
------------------------------------


Text fields [todo]
-------------------

