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


################################
Level 1 Functional specification
################################

.. contents::
   :local:

Common features and conventions
===============================

All the lpOD level 0 features are available through the level 1 API, so the
applications can create, retrieve or delete any element.  They can create,
select, update or delete any attribute or sub-element in a previously retrieved
element.

The API provides functions and methods.

Object creation
---------------

Functions are mainly used as object constructors, in order to create new ODF
elements that could be later attached to a document. The name of an object
constructor is like ``odf_create_xxx()`` where "xxx" is the object type.
These constructors return "free" ODF elements, i.e. elements which don't belong
yet to any document; these elements may be attached later through a document or
context based method. However, some very specific objects may be created "in
place", through ``set_xxx()`` element specific methods that create the objects
and directly append them to the calling element.

Once created, an object may be changed through the ``set_text()`` and
``set_attribute()`` level 0 methods; however, the level 1 features allow the
user to set the most used properties using a more friendly way.

Object property handling
------------------------

The level 1 ``set_attribute()`` method extends the level 0 one by allowing
the user, in some situations, to forget the ODF namespaces. Knowing that every
ODF attribute name belong to a namespace, if ``set_attribute()`` is
called from an ODF element with an attribute name without namespace prefix, the
method transparently concatenates the given name to the namespace prefix of the
calling object. ``get_attribute()`` use the same behaviour. As a consequence,
the prefix may be safely omitted with attributes whose namespace is the same as
the namespace of the target element. In addition, knowing that an XML attribute
name can't contain blank spaces, these methods automatically replace every
space by a dash. For example, assuming ``p`` is a paragraph (which belongs to
the "text" namespace), the three instructions below (that return the style of
the given paragraph) are equivalent::

   p.get_attribute('text:style-name')
   p.get_attribute('style-name')
   p.get_attribute('style name')

There is an exception regarding a particular attribute, which is the style name.
When ``get_attribute()`` or ``set_attribute()`` is called with an attribute
name without prefix and ending with "style", the namespace prefix is inserted as
usual, but in addition a "-name" string is silently appended. Knowing that
attributes like "xxx-style-name" are very frequently used, this feature provides
a "xxx style" shortcut.  As a consequence, the following instruction does the
same as each one of the previous example::

  p.get_attribute('style')

A ``get_attributes()`` method is provided, that returns all the attributes of
the calling element (with their real ODF names) and their values as a array
of named items. The ``set_attributes()`` method allows the user to change or
create several attributes a a time; it checks and transforms the given
attribute names in the same way as ``set_attribute()``.

Some ODF elements own a ``set_properties()`` method, which could sound redundant
with ``set_attributes()``. However, ``set_properties()`` may set element
properties that imply element-specific transformations or constructs, makes some
consistency checks, and allow the user to provide property names that aren't
directly translated in simple attributes using the same name transformation
rules as ``set_attributes()``. The same logic apply to ``get_properties()``,
when defined.

In the present specification, some element properties or attributes may be
named using multiple-word designations (ex: ``display name``, ``page layout``)
that include spaces or dashes. Knowing that such designations are not easy to
use as variable names in every programming language, spaces and dashes should
be replaces by underscore ("_") characters in the lpOD executable
implementations.

Method scopes
-------------

Some methods are document-based, other are context-based, and other are
element-specific.

A document-based method is a method that makes sense at the document level
only. As an example, ``insert_style()`` is document-based knowing that a style
is always defined at the document level.

A context-based method is designed in order to allow the user to insert, search,
process or delete content elements either in the whole document body, or in a
particular branch in the content tree. For example ``insert_element()`` is
context-based because it allows the insertion of an element in any context. Of
course, a context is always an ODF element, but context-based methods are
available whatever the element type (however, a context-based method can raise
an error, for example when it's used to execute an operation that is not legal
for the current context).

The level 1 ``insert_element()`` method supports all the features of the level 0
version, but it accepts the additional parameters ``before`` and ``after``,
whose value is an ODF element. The element to be inserted takes place
immediately *after* the reference element provided through the ``after``
parameter (if set). Alternatively, the insertion will take place *before* any
element which is provided through the ``after`` parameter. These parameters are
intended to hide the low level XML jargon, and they are, of course, optional and
mutually exclusive.

On the other hand, ``append_element()`` always attaches an element after the
last child of the context element.

An element-specific method works with specific ODF elements only, according to
their particular role. For example ``set_header()`` is provided with ODF master
pages, because a header is an extension of a page style element, while
``set_background()`` is available with objects where a background definition
makes sense (such as page layouts or paragraph styles).


Common element-specific functions and methods
=============================================

Any ODF element in the level 1 API inherits all the features of the underlying
XML element.

Every ODF element comes with methods that directly return its parent, next
sibling, previous sibling, and the list of its children. These methods (which
are provided by the underlying XML API) are available whatever the element type.

Any element provides a ``clone`` method, which creates a new instance of the
element with all its children; this instance is free and can be inserted later
in any place in the same document or in another document. An element may be
removed through a ``delete`` method from its parent element; the deletion
removes the element itself and all its children.

Some elements are created without any predefined attachment, i.e. as a free
elements, by specific constructor functions whose name is like
``odf_create_xxx()``, where ``xxx`` is the kind of element to be created.
A free element can be inserted later at the right place. Other elements, whose
definition doesn't make sens out of a specific context, are directly created in
place, through context-based methods whose name is ``set_xxx()``. Beware, every
``set_xxx()`` method creates or replaces something in the calling element, but
some of them don't create new elements.

Any element is able to be serialized and exported as an XML, UTF8-encoded
string. Symmetrically, an element can be created from an application- provided
XML string. As a consequence, lpOD-based applications can remotely transmit or
receive any kind of ODF content.

The level 1 API is not validating, so the user is responsible of the ODF
compliance (the API doesn't automatically prevent the applications from
inserting an element at the wrong place or to set non-ODF elements).

Any element can be retrieved according to its sequential position in a given
context or its text content (if defined), through methods like
``get_xxx_by_position()`` and ``get_xxx_by_content()`` where "xxx" is the
element type (i.e. "paragraph", "heading", etc). For example::

  element = context.get_xxx_by_position(p)
  element = context.get_xxx_by_content(regex)

It's possible to get the list of elements of a known type in the context, using
``get_xxx_list()``.

The two lines above retrieve an element among the children of context element.
The first one selects the child element at the given ``p`` position.
The given position is an integer; the first position is zero; negative positions
are counted back from the last (-1 is the last position).
The second instruction retrieves the first element whose text content matches a
given ``regex`` regular expression. Knowing that the regexp could be matched by
more than one element, the same method is available in a list context.

Addtional retrieval methods are available according to the element type.

Every search method operates in context, knowing that the context could be the
whole document as well as a particular element (section, table, etc).



