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
according to a calculation formula and/or a content coming from somewhere
in the environment.

A table cell may be regarded as an example of field, according to such a
definition. However, while a table cell is always part of a table row that is in
turn an element in a table, a `text field` may be inserted anywhere in the
content of a text paragraph.

Common field-related features [tbc]
-----------------------------------

Field creation and retrieval
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A text field is created "in place" using the ``set_field()`` element-based
method from a text container that may be a paragraph, a heading or a span;
``set_field()`` requires a ``content`` parameter that specifies the kind of
information to be associated (and possibly displayed) with the field.

Regarding the positioning, this method works in a similar way as
``set_bookmark()`` or ``set_index_mark()`` introduced in the `Text Marks and
Indices` section.

By default, the field is created and inserted  before the first character of
the content in the calling element. As an example, this instruction creates
a ``title`` field (whose role is to display the title of the document) before
the first character of a paragraph::

  paragraph.set_field(content="title")

A field may be positioned at any place in the text of the host container; to do
so, an optional ``position`` parameter, whose value is offset of the target,
may be provided. The value of this parameter is either a positive position,
zero-based and counted from the beginning, or a negative position counted from
the end. The following example puts a ``title`` field at the fifth position and
a ``subject`` field 5 characters before the end::

  paragraph.set_field(content="title", 4)
  paragraph.set_field(content="subject", -5)

The ``set_field()`` method allows field positioning at a position that depends
on the content of the target, instead of a position. Thanks to a ``before`` or
a ``after`` parameter, it's possible to provide a regexp that tells
to insert the new field just before of after the first substring that
matches a given filter ``set_field()``. The next example inserts the name of
the initial creator of the document after a given string::

  paragraph.set_field(content="subject", after="this paper is related to ")

If ``position`` is provided with ``after`` or ``before``, any substring before
the given position is ignored, even if it matches the string filter, so the
field is inserted after the position, or not inserted. In addition, it's
possible to combine ``before`` and ``after``; in such a situation, the field is
inserted between the two substrings that respectively match the two filters,
and only if these substrings are contiguous and in the right order.

``set_field()`` returns the created ODF element in case of success, or null if
(due to the given parameters and the content of the target container) the field
can't be created.

A text field can't be identified by a unique name or ID attribute and can't be
selected by coordinates in the same way as a cell in a table. However, there is
a context-based ``get_fields()`` that returns, by default, all the text
field elements in the calling context. This method, when called with a single
``content`` parameter, that specifies the associated content, returns the fields
that match the given kind of content only, if any. For example, this instruction
returns all the page number fields in the document body::

  document.get_fields(content="page number")

Field datatypes
~~~~~~~~~~~~~~~

The value of a field has a data type. The default data type is ``string``, but
it's possible to set any ODF-compliant data type as well, using the optional
parameter ``type``. According to ODF 1.1, §6.7.1, possible types are ``float``,
``percentage``, ``currency``, ``date``, ``time``, ``boolean`` and, of course,
``string``.

If the selected ``type`` is ``currency``, then a ``currency`` additional
parameter is required, in order to provide the conventional currency unit
identifier (ex: EUR, USD). As soon as a ``currency`` parameter is set,
``set_field()`` automatically selects ``currency`` as the field type (so the
``type`` parameter may be omitted).

Note that for some kinds of fields, the data type is implicit and can't be
selected by the applications; in such a situation, the ``type`` parameter, if
provided, is just ignored. For example, a ``title`` or ``subject`` field is
always a string, so its data type is implicit and can't be set.

Common field properties and methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A text field may be created with an optional ``fixed`` boolean parameter, that
is ``false`` by default but, if ``true``, means that the content of the field
should not be automatically updated by the editing applications. For example,
a ``date`` field, that is (by default) automatically set to the current date by
a typical ODF editor each time the document is updated is no longer changed as
long as its ``fixed`` attribute is ``true``. This option is allowed for some
kinds of text fields.

A numeric text field (ex: date, number) may be associated with a display format,
that is identified by a unique name and described elsewhere through a numeric
style; this style is set using the ``style`` parameter with ``set_field()``.

While a field is often inserted in order to allow a viewer or editor to set an
automatically calculated value, it's possible to force an initial content (that
may be persistent if ``fixed`` is true) using the optional ``value`` and/or
``text`` parameters. If the data type is ``string``, the ``value`` is the same
as the ``text``. For a ``date`` or a ``time``, the value is stored in ISO-8601
date format. For other types, the ``value`` is the numeric computable value
of the cell. The ``text``, if provided, is a conventional representation of
the value according to a display format.

Text fields use a particular implementation of the generic ``get_text()``
method. When called from a text field element, this method returns the text of
the element (as it could have been set using the ``text`` property), if any.
If the element doesn't contain any text, this method returns the value "as is",
i.e. without formatting.

The generic ``set_text()`` method allows the applications to change the ``text``
content of the element at any time, while ``set_properties()`` can set or change
any other parameter later.

Document fields [todo]
----------------------



Declared variable fields
------------------------

A text field may be associated to a so-called "variable", that is, according to
ODF 1.1 (§6.3) a particular user-defined field declared once with an unique name
and used at one or several places in the document. However, the behavior of such
a variable is a bit complex knowing that its content is not set once for all.

A variable may appear with a content at one place, and with a different content
at another place. It should always appear with the same data type. However, the
ODF 1.1 specification is self-contradictory about this question; it tells:

`A simple variable should not contain different value types at different places
in a document. However, an implementation may allow the use of different value
types for different instances of the same variable.`

More precisely, ODF allows several kinds of variables, including so-called
`simple`, `user` and `sequence` variables. The present lpOD level 1 API supports
the two first categories. While a `simple` variable may have different values
(and, practically, different types) according to its display fields, a `user`
variable displays the same content everywhere in the document.

In order to associate a field with an existing variable, ``set_field()`` must be
used with the ``content`` parameter set to ``variable``, and an additional
``name`` parameter, set to the unique name of the variable, is required. If
the associated variable is a `user` variable, the ``value`` and ``type``
parameters are not allowed. If the variable is `simple`, then it's possible to
set a specific value and/or type, with the effects described hereafter.

When a field associated to a `simple` variable is inserted using
``set_field()``, its content is set, by default, to the existing content and
type of the variable. If a ``value`` and/or ``text`` parameter is provided, the
field takes this new content, which becomes the default content for subsequent
fields associated to the same variable, but the previous fields keep their
values. The same apply to the field type, if a new ``type`` is provided. Beware,
by `subsequent` and `previous` we mean the fields that precede or follow the
field that is created with a changed content in the order of the document, not
in the order of their creation.

On the other hand, all the fields associated to a `user` variable take the same
value. Each time the content of the variable is changed, all the associated
fields change accordingly. The API doesn't allow the application to change this
content through the insertion of an associated field. If needed, the variable
content may be changed explicitly using another method.

If the lpOD-based application needs to install a variable that doesn't exist,
it must use the document-based ``set_variable()`` method, that takes a mandatory
first argument that is its unique name, a ``type`` (whose default is ``string``)
and of course a ``currency`` parameter if ``type`` is ``currency``. Because
``set_variable()`` doesn't set anything visible in the document, it doesn't take
any positioning or formatting parameter. A ``value`` parameter is needed in
order to set the initial content of the variable.

A declared variable may be retrieved thanks to its unique name, using the
``get_variable()`` document-based method with the name as argument. The returned
object, if any, supports the generic ``get_properties()`` and
``set_properties()`` method, that allow to get or change its ``value``, ``type``
and ``currency`` parameters. In addition, the variable-specific ``get_value()``
and ``set_value()`` methods are allowed as syntax shortcuts avoiding the use
of ``get_properties()`` and ``set_properties()`` to access the stored values.

Text fields [todo]
-------------------

