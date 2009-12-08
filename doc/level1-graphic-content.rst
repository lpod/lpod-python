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


Graphic content
===============

.. contents::
   :local:

Frames
------

A frame is a rectangular container that may contain text boxes and images. It
may contain other kinds of elements that are not presently covered by the lpOD
level 1 specification.

A frame is created using ``odf_create_frame()`` with the following properties:

- ``name``: the optional name of the object (for the end-user);

- ``id``: an arbitrary string, that is the unique identifier of the frame;

- ``style``: the name of a graphic style for the frame;

- ``position``, the coordinates of the frame, as a list of 2 strings
   containing the X and Y positions (each string specifies the number
   and the unit, ex. "1cm", "2pt"), knowing that the default values are 0;

- ``size``: the size, provided either in absolute values as the position, as
   percentages, or using the special keywords ``scale`` or ``scale-min`` (see
   ODF §9.3 for details); both absolute and relative values may be provided as
   a string, separated by a space, if needed, like "10cm 12%";

- ``z index``: an optional sequence number that allows the user to assign a
   particular order of rendering, knowing that frames are rendered by default
   according to their sequential position in the document tree;

- ``class``: an optional presentation class (see the "Class" subsection in
   ODF §9.6.1).

A frame may be inserted in place through the standard ``insert_element()``
method, but the behavior depends on the context.

In a text document, a frame may be attached at the document level, as long as
it's anchored to a page; as an consequence, a ``page`` parameter must be
provided with the page number.

Simply put, with the exception above, a frame is anchored to the calling
context element. The ODF elements that may insert a frame in the present
lpOD API are *draw pages*, *paragraphs*, *tables*, and *cells*.

In a presentation or drawing document, the calling element is typically a draw
page.

When ``insert_element()`` is called from a paragraph, an optional ``offset``
parameter, specifying the position in the text where the frame will be inserted,
may be provided (the default position is the beginning of the paragraph).

An existing frame may be selected using ``get_frame()`` with the identifier.

It's possible, of course, to populate a frame using ``insert_element()`` or
``append_element()`` from the frame itself. However, the API provides frame-
specific methods in order to directly create and incorporate the most common
objects in a frame context, namely *text boxes* and *images*. These methods are
respectively:

- ``set_text_box()``, which requires no argument, but which may be called with
   a list of existing ODF elements that could become a valid content for a
   text box (paragraphs, item lists, etc); this method returns an object that
   may be later used to insert additional content;

- ``set_image()``, which creates an image element that will cover the whole
   area of the frame (the parameters are the same as with ``odf_create_image()``
   introduced later); alternatively, if ``set_image()`` is called with an
   existing ODF image element as argument, this element is incoporated as is
   without creation; ``set_image()`` returns the new (or newly inserted) ODF
   image element.

Images
------

An image element may be created out of any document with ``odf_create_image()``.
This constructor requires only one named parameter, that is either ``url`` or
``content``. The first one is a link to an external graphic resource, while the
second one is the binary content of an image in BASE64 encoding.

An image may be used as a text container. It's possible to incorporate text
containers (typically paragraphs or item lists) in an image object (in order
to display the text in the foreground). To do so, the user can use the generic
``insert_element()`` or ``append_element()`` method from the image object,
with the needed text container as argument.

An image should be incorporated in a document through a *frame* (see above).


Drawing Shapes
--------------

Common Drawing Shape Attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The currently covered shapes are ``line``, ``rectangle``, ``ellipse``, and ``connector``.

A shape is created using an ``odf_create_xxx()`` constructor, where ``xxx`` is of course replaced by a shape name from the list above, that returns an ``odf_shape`` object.

The common properties that may be set through shape constructor named parameters are:

- ``name``: an optional name, that should be unique;
- ``id``: an optional identifier, that must be unique;
- ``style``: the name of the graphic style of the shape;
- ``text style``: the style that is used to format the text that can be added
  to this shape, if any (if defined, must be a paragraph style);
- ``layer``: the optional name of the layer in the layer set of the document, if
  the graphics are layered.

Note that, while the ``name`` property is not specified as unique in the standard, OpenOffice.org prevents the end-user from providing non-unique names to drawing shapes. On the other hand, OpenOffice.org doesn't currently neither uses nor preserves the ``id`` property in text documents, but needs it to implement the connectors in presentation documents. So, we presently recommend the use of ``name``, with unique values, as soon as the applications need persistent shape identifiers.

A shape may be provided with a title and a description (which are non-displayed but persistent metadata), through the ``set_title()`` and ``set_description()`` methods. These informative data may be retrieved using ``get_title()`` and ``get_description()``.

For some shapes, the following properties must be provided:

- ``position``, the coordinates of the frame, as a list of 2 strings
   containing the X and Y positions (each string specifies the number
   and the unit, ex. "1cm", "2pt"), knowing that the default values are 0;

- ``size``: the size, provided using the same format and rules as the position,
  knowing that the default values are "1cm".

However, the ``position`` and ``size`` properties don't apply to some particular shapes, such as lines (see below).

A shape becomes visible when it's inserted somewhere using the generic ``insert_element()`` method.

In a text document, a frame may be attached at the document level, as long as
it's anchored to a page; as an consequence, a ``page`` parameter must be
provided with the page number. Without this ``page`` property, lpOD anchors the shape to the first page by default.

Simply put, with the exception above, a shpe is anchored to the calling
context element.

Optionally, a regular text paragraph may be embedded in a shape. Unlike the name, the title and the description, this paragraph will be visible. There is no shape-specific method for that; the generic ``insert_element()`` method, called from the ``odf_shape`` object, allows the user to insert a paragraph in a shape. The given paragraph may have its own style, whose properties override those of the shape
``text style``.

Rectangles and Ellipses
~~~~~~~~~~~~~~~~~~~~~~~

Rectangles and ellipses are created with ``odf_create_rectangle()`` and ``odf_create_ellipse()``, respectively, using the common properties described above, including ``size`` and ``position``.

Lines and Connectors
~~~~~~~~~~~~~~~~~~~~

A line is created using ``odf_create_line()``, with the standard shape parameters with the exception of ``size`` and ``position``.

The size and the position are defined by line-specific ``start`` and ``end`` properties, each one representing the coordinates of an extremity, in the same format as the ``position`` property of some other shapes.

A connector is created using ``odf_create-connector()``. It may be defined with the same parameters as a line, but can support a more sophisticated configuration, through the following specific properties:

- ``connected shapes``: the name of the start and end shapes that are linked
  through the connector (as a pair of strings);
- ``glue points``: the numbers of the glue points in the start and end shapes, respectively (glue points are designated points on the area of a drawing object to which a connector shape can connect, see ODF 1.1 §9.2.19).


Animations [todo]
-----------------

Charts [todo]
-------------


