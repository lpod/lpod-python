.. Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.

   Authors: David Versmisse <david.versmisse@itaapy.com>
            Hervé Cauwelier <herve@itaapy.com>
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


Styles
======

.. contents::

A style controls the formatting and/or layout properties of a family of
content objects. It's identified by its own name and its family.
In the lpOD API, the family has a larger acception than in the OpenDocument
specification. In the underlying XML, the family is indicated sometimes
by the value of an explicit 'style:family' attribute, and sometimes by the
XML tag of the style element itself.

In order to hide the complexity of the ODF data structure, the level 1 API
allows the user to handle any style as a high level *odf_style* object.

Common style features
----------------------

Any style is created through a common ``odf_create_style()`` function with the
the family as its mandatory first argument. A name, that is the identifier of
the style in the given family, is generally required. So, a typical style
creation instruction looks like::

   s = odf_create_style('text', 'MyTextStyleName')

The example above creates a named text style without any property. The
properties are optionally passed as named parameters.

Additional arguments can be required according to the family. An optional
``parent`` argument, whose value is the name of another common style of
the same family (existing or to be created), can be provided, knowing that a
style inherits (but can override) all the properties of its parent. A
``display name`` additional parameter may be provided; if set, this parameter
designates a visible name that may differ from the internal name. It's
possible to copy (instead of inherit) all the properties of an existing style
of the same family, through a ``clone`` option, knowing that ``clone`` and
``parent`` are mutually exclusive options. The code example below produces two
text styles whose properties are the same as "MyTextStyleName", but the first
one will be affected by later changes of the base style while the second one
is independant::

   odf_create_style('text', 'NewStyle1', parent='MyTextStyleName')
   odf_create_style('text', 'NewStyle2', clone='MyTextStyleName')

An effective  style name, unique for the family, is required as soon as the
style is attached to a document, unless it's inserted as a *default style*.
When a style is used as a default style, its name and display name are
meaningless and ignored. The family and the name constitute the absolute
identifier of a style in a document.

The ``odf_create_style()`` function creates a free element, not included in a
document. This element (or a clone of it) is available to be attached later
to a document through a generic, document-based ``insert_style()`` method.

The ``insert_style()`` method requires a style object as its only one mandatory
argument. An optional boolean parameter whose name is ``default`` is allowed;
if provided and set to ``true``, this parameter means that the style is inserted
as a *default style*. A default style is a style that automatically apply to
content elements whose style is not explicitly specified. A document can contain
at most one default style for a style family, so any attachment of a default
style replaces any existing default style of the same family.

All styles can't be used as default styles. Default styles are allowed
for the following families: ``paragraph``, ``text``, ``section``, ``table``,
``table column``, ``table row``, ``table cell``, ``table page``, ``chart``,
``drawing page``, ``graphic``, ``presentation``, ``control`` and ``ruby``.

An existing style may be retrieved in a document using the ``get_style()``
document-based method. This method requires a family as its first argument and
allows a style name as a second, optional argument. If the name is missing,
this method tries to retrieve the default style for the given family, if any.

The following example extracts a paragraph style, so-called "MyParagraph", from
a document and attaches a clone of this style as a default style of another
document; the old default paragraph style of the target document (if any) is
automatically replaced::

   ps = doc1.get_style('paragraph', 'MyParagraphStyle').clone()
   doc2.insert_style(ps, default=true)

While a style is identified by name and family, it owns one or more sets of
properties. A style property is a particular layout or formatting behaviour.
The API provides a generic ``set_properties()`` method which allows the user to
set these properties, while ``get_properties()`` returns the existing properties
as an associative array.

However, some styles have more than one property set.

As an example, a paragraph style owns so-called "paragraph properties"
and/or "text properties" (see below). In such a situation, an additional
``area`` parameter, whose value identifies the particular property set, with
``set_properties()``. Of course, the same ``area`` parameter applies to
``get_properties()``.

Some styles allow the applications to specify a *background*. Such a background
is sometimes characterized by the RGB, 3-bytes hexadecimal code of an arbitrary
color, with a leading "#". However some styles allow the use of backround image
instead of or in combination with a color. In order to deal with these
possibilities, a ``set_background()`` is provided; this method (which works
with some style objects only) is used with a ``color`` and/or an ``url`` named
parameters. The ``color`` value range is #000000-#ffffff, while ``url`` should
be set to the URL of the graphic resource. If ``url`` is set, some additional
optional parameters may be provided, in order to control the way the image is
displayed in the background, namely:

- ``position``: a string that specifies the horizontal and vertical positions
  of the image, through one or two space-separated words (in any order) among
  ``center``, ``left``, ``right``, ``top``, ``bottom`` (default: ``center``);
- ``repeat``: specifies whether a background image is repeated or stretched,
  whose possible values are ``no-repeat`` meaning that the image should be
  displayed once, ``repeat`` to repeat the image in order to fill the whole
  background, and ``stretch`` to extend the image in order to fill the
  whole background;
- ``opacity``: the percentage of opacity;
- ``filter``: an application-specific filter to that is used to load and process
  the graphic file, according to the image format.

To remove the background color or image (i.e. to set the background to the
default, that is transparent), the user just have to call ``set_background()``
with ``color`` and ``url`` set to null.

A style that apply in some way to a rectangular area (ex: shape, frame,
paragraph) other than a page may have visible borders and a shadow. Borders are
specified using ``border xxx`` attributes where ``xxx`` is either ``left``,
``right``, ``top`` or ``bottom``; if all the borders are the same, a single
``border`` property is convenient. The value of a border property is a 3-part
string that describes the thickness, the line style and the line color
(according to the XSL/FO grammar), like "0.1cm solid #000000" for a one
millimeter solid black line. The shadow is specified through a ``shadow``
property whose value is a 3-part string describing the color and the size, like
"#808080 0.18cm 0.18cm".

A style can be inserted as either *common* (or named and visible for the
user of a typical office application) or *automatic*, according to a boolean
``automatic`` option, whose default value is ``false``. A common style may have
a secondary unique name which is its *display name*, which can be set through
an additional option. With the exception of this optional property, and a
few other ones, there is no difference between automatic and common styles.

Of course, a style is really in use when one or more content objects
explicitly reference it through its style property.

The API allows the user to retrieve and select an existing style by name and
family. The display name, if set, may be used as a replacement of the name
for retrieval.

Once selected, a style could be removed from the document through a standard
level 0 element deletion method.

Text styles
------------

A text style can be defined either to control the layout of a text container,
i.e. a paragraph, or to control a text range inside a paragraph. So the API
allows the user to handle two families of text styles, so called *text*
and *paragraph*. For any style in the text or paragraph families, the *text*
class is recommended.

Text family
~~~~~~~~~~~

A text style (i.e. a style whose family is ``text``, whatever its optional
class) is a style which directly apply to characters (whatever the layout
of the containing paragraph). So, it can bear any property directly
related to the font and its representation. The most used properties are
the font name, the font size, the font style (ex: normal, oblique, etc),
the text color, the text background color (which may differ from the
common background color of the paragraph).

A text style can apply to one or more text spans; see the "Text spans"
section. It can be used as the default text style of a document. In addition,
an existing text style may be reused to set the text properties of a paragraph
style (see below).

The example hereafter creates a text style, so called "My Colored Text",
using Times New Roman, 14-sized navy blue bold italic characters with
a yellow background::

   s = odf_create_style('text', 'MyColoredText',
                        'display name'='My Colored Text',
                        font='Times New Roman',
                        size='14pt',
                        weight='bold',
                        style='italic',
                        color='#000080',
                        )
   s.set_background(color='#ffff00')

This new style could be retrieved and changed later using ``get_style()``
then the ``set_properties()`` method of the style object. For example, the
following code modifies an existing text style definition so the font
size is increased to 16pt and the color turns green::

   s = document.get_style('text', 'MyColoredText')
   s.set_properties(size='16pt', color='#00ff00')

The ``set_properties()`` method may be used in order to delete a property,
without replacement; to do so, the target property must be provided with
a null value.

Note that ``set_properties()`` can't change any identifying attribute such
as name, family or display name.

The lpOD level 1 API allows the applications to set any property without
ODF compliance checking. The compliant property set for text styles is
described in the section §15.4 of the OASIS ODF specification. Beware,
some of them are not supported by any ODF text processor or viewer.

The API allows the user to set any attribute using its official name
according to the ODF specification (§15.4). For example, the properties
which control the character name and size are respectively
``fo:font-name`` and ``fo:font-size``. However, the API allows the use of
mnemonic shortcuts for a few, frequently required properties, namely:

- ``font``: font name;
- ``size``: font size (absolute with unit or percentage with '%');
- ``weight``: font weight, which may be 'normal', 'bold', or one of the
  official nine numeric values from '100' to '900' (§15.4.32);
- ``style``: to specify whether to use normal or italic font face; the
  legal values are ``normal``, ``italic`` and ``oblique``;
- ``color``: the color of the characters (i.e. foreground color), provided
  as a RGB, 6-digit hexadecimal string with a leading '#';
- ``underline``: to specify if and how text is underlined; possible values
  are ``solid`` (for a continuous line), ``dotted``, ``dash``,
  ``long dash``, ``dot dash``, ``dot dot dash``, ``wave``, and ``none``;
- ``display``: to specify if the text should by displayed or hidden;
  possible values are ``true`` (meaning visible) ``none`` (meaning hidden)
  or ``condition`` (meaning that the text is to be visible or hidden
  according to a condition defined elsewhere).

A text style may have a background color, but not a background image.

Paragraph family
~~~~~~~~~~~~~~~~

A paragraph style apply to paragraphs at large, i.e. to ODF paragraphs and
headings, which are the common text containers. It controls the layout of both
the text content and the container, so its definition is made of two distinct
parts, the *text* part and the *paragraph* part.

The text part of a paragraph style definition may have exactly the same
properties as a regular text style. The rules are defined by the §15.4 of the
OASIS 1.1 ODF specification, and the API provides the same property shortcuts as
for a text style creation. Practically, this text part defines the default text
style that apply to the text content of the paragraph; any property in this part
may be overriden as soon as one or more text spans with explicit styles are
defined inside the paragraphs.

The creation of a full-featured paragraph style takes two steps. The first one
is a regular ``odf_create_style()`` instruction, with ``paragraph`` as the value
of the family mandatory argument, a name parameter (unless the user just wants
to create a default style) and any number of named paragraph properties. The
second (optional) step consists of appending a *text* part to the new paragraph
style; it can be accomplished, at the user's choice, either by cloning a
previously defined text style, or by explicitly defining new text properties,
through the ``set_properties()`` method with the ``area`` option set to
``text``.

Assuming that a "MyColoredText" text style has been defined according to the
text style creation example above, the following sequence creates a new
paragraph style whose text part is a clone of "MyColoredText", and whose
paragraph part features are the text justification, a first line 5mm indent,
a black, continuous, half-millimiter border line with a bottom-right, one
millimeter grey shadow, with other possible properties inherited from a
"Standard" style::

   ps = odf_create_style('paragraph', 'BorderedShadowed',
                           'display name'='Strange Boxed Paragraph',
                           parent='Standard',
                           align='justify',
                           indent='5mm',
                           border='0.5mm solid #000000',
                           shadow='#808080 1mm 1mm'
                           )
   ts = document.get_style('text', 'MyColoredText')
   ps.set_properties(area='text', ts.clone())

Note that "MyColoredText" is reused by copy, not by reference; so the new
paragraph style will not be affected if "MyColoredText" is changed or deleted
later.

The API allows the user to set any attribute using its official name according
to the ODF specification related to the paragraph formatting properties (§15.5).
However, the API allows the use of mnemonic shortcuts for a few, frequently
required properties, namely:

- ``align``: text alignment, whose legal values are ``start``, ``end``, ``left``, ``right``, ``center``, or ``justify``;
- ``align-last``: to specify how to align the last line of a justified paragraph, legal values are ``start``, ``end``, ``center``;
- ``indent``: to specify the size of the first line indent, if any;
- ``widows``: to specify the minimum number of lines allowed at the top of a page to avoid paragraph widows;
- ``orphans``: to specify the minimum number of lines required at the bottom of a page to avoid paragraph orphans;
- ``together``: to control whether the lines of a paragraph should be kept together on the same page or column, possible values being ``always`` or ``auto``;
- ``margin``: to control all the margins of the paragraph;
- ``margin xxx`` (where xxx is ``left``, ``right``, ``top`` or ``bottom``): to control the margins of the paragraph separately;
- ``border``: a 3-part string to specify the thickness, the line style and the line color (according to the XSL/FO grammar);
- ``border xxx`` (where ``xxx`` is ``left``, ``right``, ``top`` or ``bottom``): the same as ``border`` but to specify a particular border for one side;
- ``shadow``: a 3-part string to specify the color and the size of the shadow;
- ``padding``: the space around the paragraph;
- ``padding xxx`` (where ``xxx`` is ``left``, ``right``, ``top`` or ``bottom``): to specify the space around the paragraph side by side;
- ``keep with next``: to specify whether or not to keep the paragraph and the next paragraph together on a page or in a column, possible values are ``always`` or ``auto``;
- ``break xxx`` (where ``xxx`` is ``before`` or ``after``): to specify if a page or column break must be inserted before or after any paragraph using the style, legal values are ``page``, ``column``, ``auto``.

A pararaph style may have a background color or image.

List styles
------------

A list style is a set of styles that control the formatting properties of
the list items at every hierachical level. As a consequence, a list style
is a named container including a particular style definition for each level;
in other words a list style is a set of list level styles.

The API allows the user to create a list style (if not previously existing
in the document), and to create, retrieve and update it for any level.

A new list style, available for later insertion in a document, is created
through the ``odf_create_style()`` function. The only mandatory argument is
the style family, which is ``list``. However, a name is generally required as
the second argument, knowing that a style list can't presently be used as a
default style; an error is raised at any attempt to attach a nameless list
style using ``insert_style()``. An optional display name argument is allowed
(if the style list is about to be used as a common style); if  provided, the
display name should be unique as well.

An existing list style object provides a set_level_style() method,
allowing the applications to set or change the list style properties for a
given level. This method requires the level number as its first argument,
then a ``type`` named parameter. The level is a positive (non zero) integer
value that identifies the hierarchical position. The type indicates what kind
of item mark is should be selected for the level; the possible types are
``number``, ``bullet`` or ``image``.

If the ``bullet`` type is selected, the affected items will be displayed after
a special character (the "bullet"), which must be provided as a "character"
named argument, whose value is an UTF-8 character.

If the ``image`` type is selected, the URL of an image resource must be
provided; the affected items will be displayed after a graphical mark whose
content is an external image.

A ``number`` list level type means that any affected list item will be marked
with a leading computed number such as "1", "i", "(a)", or any auto-
incremented value, whose formatting will be controlled according to other
list level style properties (or to the default behaviour of the viewer for
ordered lists). With the ``number`` type, its possible to provide ``prefix``
and/or ``suffix`` options, which provide strings to be displayed before and
after the number. Other optional parameters are:

- ``style``: the text style to use to format the number;
- ``display levels``: the number of levels whose numbers are displayed at the
  current level (ex: if display-levels is 3, so the displayed number could
  be something like "1.1.1");
- ``format``: the number format (typically "1" for a simple number display),
  knowing that if this parameter is null the number is not visible;
- ``start value``: the first number of a list item of the current level.

The following example shows the way to create a new list style then
to set some properties for levels 1 to 3, each one with a different type::

   ls = odf_create_style('list', 'ListStyle1')
   ls.set_level_style(1, type='number', prefix=' ', suffix='. ')
   ls.set_level_style(2, type='bullet', character='-')
   ls.set_level_style(3, type='image', url='bullet.jpg')

The ``set_level_style()`` method returns an ODF element, representing the list
level style definition, and which could be processed later through any element-
or style-oriented function.

An individual list level style may be reloaded through ``get_level_style()``,
with the level number as its only one argument; it returns a regular ODF element
(or *null* if the given level is not defined for the calling list style).

It's possible to reuse an existing list level style definition at another level
in the same list style, or at any level in another list style, or in another
document. To do so, the existing level style (previously extracted by any mean,
including the ``get_level_style()`` method) must be provided as a special
``clone`` parameter to set_level_style(). The following example reuses the
level 3 style of "ListStyle1" to define or change the level 5 style of
"ListStyle2"::

   ls1 = document.get_style('list', 'ListStyle1')
   source = ls1.get_level_style(3)
   ls2 = document.get_style('list', 'ListStyle2')
   ls2.set_level_style(5, clone=source)

The object returned by ``set_level_style()`` or ``get_level_style()`` is
similar to an ODF style object, without the name and the family. So the generic
``set_properties()`` method may be used later in order to set any particular
property for any list level style. Possible properties are described in section
§14.10 of the ODF specification.

Every list level style definition in a list style is optional; so it's not
necessary to define styles for levels that will not be used in the target
document. The ``set_level_style()`` method may be used with an already defined
level; in such a situation, the old level style is replaced by the new one. So
it's easy to clone an existing list style then modify it for one or more levels.

Outline style
--------------

According to the ODF specification, "*the outline style is a list style that
is applied to all headings within a text document where the heading's paragraph
style does not define a list style to use itself*".

Practically, the outline style is a particular list style which controls the
layout of a particular hierarchical list. In other words, it's a list
of default styles for headings according to their respective hierarchical
levels.

The outline style, like any list style, should define a style for each level
in use in the document.

The API allows the user to initialize the outline style (if not previously
existing in the document), and to create, retrieve and update it for any level.

The ``get_style()`` method allows the user to get access to the outline
style structure; to do so, ``outline`` must be provided in place of the family
argument. The returned object is a nameless list style; it may be
cloned in order to be reused as the outline style for another document, or as
an ordinary list style (provided that it's later named). If the outline style
is not initialized yet, ``get_outline_style()`` returns a null value.

If needed, the outline style can be created through ``odf_create_style()``
with ``outline`` as the style family and without name, then attached using
``insert_style()``. The style for each individual level may be set, retreived
and changed at any time using the object-based ``set_level_style()`` and
``get_level_style()`` methods.

The API allows the user to set style attributes for any level, knowing that a
level is identified by a positive integer starting from 1. With the current
version of the lpOD level 1 API, a few outline level style attributes are
supported, namely:

- ``prefix``: a string that should be displayed before the heading number;
- ``suffix``: a string that should be displayed before the heading number;
- ``format``: the number display format (ex: ``1``, ``A``);
- ``display levels``: the number of levels whose numbers are displayed at
  the current level;
- ``start value``: the first number of a heading at this level;
- ``style``: the name of the style to use to format the number (that is a
  regular text style).

As an example, the following code retrieves the default style for the level 4
headings::

   os = document.get_style('outline')
   head4 = os.get_level_style(4)

The next example sets some properties for any level 1 heading, namely a
numbering starting from 5 and the use of capital letters between parentheses
as numbers::

   os = document.get_style('outline')
   os.set_level_style(1, start-value=5, prefix='(', suffix=')', format='A')

According to the example above, the default numbering scheme for level 1
headings will be (E), (F), (G), and so on.

Attributes and properties which are not explicitly supported through predefined
parameter names in the present version of the API could always be set hrough
the element-oriented methods of the level 0 API, knowing that get_level_style()
returns a regular element.

Table-related styles
--------------------

The API supports 4 kinds of styles that control various table formatting
properties. While a table style specifies the global formatting properties of
a table, row, column and cell styles allow a specific layout control for each
table component.

Table styles
~~~~~~~~~~~~

A table style specifies the external size, borders and background of a table.
It may be created through ``odf_create_style()`` with the following parameters:

- ``width``: the table width (in length, not in columns), provided either in
   absolute values or as a percentage of the page width; both absolute and
   relative values may be provided as a string, separated by a space, if needed;
- ``margin``: to control all the margins of the table;
- ``margin xxx`` (where xxx is ``left``, ``right``, ``top`` or ``bottom``): to
   control the margins of the table separately;
- ``align``: to specifiy the table alignment scheme, with ``left``, ``right``,
   ``center``, ``margins`` as possible values;
- ``together``: to control whether the rows of the table should be kept together
   on the same page or column, possible values being ``always`` or ``auto``;
- ``keep with next``: to specify whether or not to keep the paragraph and the
   next paragraph together on a page or in a column, possible values are
   ``always`` or ``auto``; default is ``auto``;
- ``break xxx`` (where ``xxx`` is ``before`` or ``after``): to specify if a page
   or column break must be inserted before or after any paragraph using the
   style, legal values are ``page``, ``column``, ``auto``; default is ``auto``;
- ``display``: boolean property that specifies if a table is visible or not;
   default is ``true``.

The table styles support the ``set_background()`` method and may have a
``shadow`` property. However, while a table covers a rectangular area, the
``border xxx`` properties are not defined at the table style level; the borders
are cell properties.

Cell styles
~~~~~~~~~~~

A cell style is created using ``odf_create_style()`` with ``table cell`` as the
family. A ``data style`` may provided as an optional parameter, which is
recommended as soon as the style is about to be used for numeric cells.

Once created, a cell style may be customized using ``set_properties()``. See
§15.11 in the ODF specification for the full list of possible properties.
However, ``set_properties()``, when used from a cell style object, allows the
following shortcuts for the most used attributes:

- ``border``, ``border top``, ``border left``, ``border right``,
   ``border bottom``, in the same way as other rectangular area styles;
- ``shadow``: idem.

The ``set_background()`` method is allowed (with ``color`` or ``uri``).

Column styles
~~~~~~~~~~~~~

A column style is created using ``odf_create_style()`` with ``table column`` as
the family. It may be customized using ``set_properties()``.

The most necessary property is ``width``, wich may be an absolute width (i.e.
a string containing the number and the length unit), a relative length (i.e.
a string containing a number followed by a "*"), or both (space-separated).
See §15.9.1 in the ODF specification for details about the relative widths.

The ``break xxx`` parameters (where ``xxx`` is ``before`` or ``after``), are
allowed to specify if a page or column break must be inserted before or after
any column using the style, legal values are ``page``, ``column``, ``auto``;
default is ``auto``.

Row styles [todo]
~~~~~~~~~~~~~~~~~

Graphic styles [todo]
---------------------

Numeric data formatting styles [tbc]
------------------------------------

Numeric styles in general are formatting styles that apply to computable values,
generally stored in fields or table cells. The covered data types are ``float``,
``currency``, ``percentage``, ``boolean``, ``date``, ``time``.

Number style [todo]
~~~~~~~~~~~~~~~~~~~
Currency style [todo]
~~~~~~~~~~~~~~~~~~~~~
Percentage style [todo]
~~~~~~~~~~~~~~~~~~~~~~~
Boolean style [todo]
~~~~~~~~~~~~~~~~~~~~
Date style [todo]
~~~~~~~~~~~~~~~~~
Time style [todo]
~~~~~~~~~~~~~~~~~

Page styles
------------

A page style definition, so-called *master page*, is *"a template for pages in
a document"*. It directly defines the static content "*that is displayed on all
pages*" that use it (such as headers and footers). In addition, a
*master page* is associated to a *page layout*, defined as a separate object
that describes "*the physical properties or geometry of a page, for example,
page size, margins, header height, and footer height*". The same *page layout*
may be used through several *page masters*.

In *text documents*, the pages are not statically defined; they are dynamically
generated by the viewing/printing applications according to their content
(which changes each time a piece of content is inserted, deleted or moved. As a
consequence, a *master page* is not used in the same way as, say, a paragraph
style or a list style, because there is no persistent text page object which
could directly contain a reference to a page style. A master page is essentially
referred to through page breaks. For example, each time a forced page break is
inserted, it's possible to specify the *master page* of the following page. In
addition, any *master page* may own a property that tells what should be the
*master page* to use after the current page (for example, a "Right page" style
may de defined in order to ensure that any page using it will be followed by
a page that will use a "Left page" style and vice-versa).

   .. figure:: figures/lpod_page_style.*
      :align: center

*Master page* objects (and the corresponding *page layouts*) apply to
presentation and drawing documents, too. However, the page style model is very
different (and much more complicated) for these documents than for text
documents. This model uses master pages, page layouts, and two additional
style-related objects, namely *presentation page layouts* and
*presentation page styles*.

Drawing and presentation documents use statically defined draw pages. As a
consequence, the link between every draw page and its master page and other
style-related objects is static and specified through explicit properties of
the draw page.

Master pages
~~~~~~~~~~~~~

A master page is created and retrieved the same way as other styles.

To create a master page through the generic ``odf_create_style()`` function,
the family argument is ``master page`` and it's followed by an arbitrary name.
A master page may, like other styles, have a display name distinct from its
name. In addition, a full master page definition allows the following named
parameters:

- ``layout``: the unique name of a *page layout*, existing or to be defined
  in the same document (see later the lpOD specifications about the page layout
  objects);
- ``next``: the master page to apply to the following page, as soon as the
  current page is entirely filled, knowing that the current master page is used
  for the next page by default.

As any other ODF element, a master page object inherits the generic
``insert_element()`` and ``append_element()`` methods that allow the user to
attach any other ODF element to it. Beware that such attachments are unchecked,
and that the user should not integrate any kind of element in a master page.

A unique name is required at insert time; ``insert_style()`` raises an error at
any attempt to attach a nameless master page to a document. On the other hand,
``insert_style()`` can attach a master page without layout name, but the
visible result is not predictable and depends on the default page layout of
the printing application.

The ``parent`` parameter is not allowed in master page creation, as long as
there is no explicit inheritance mechanism in the ODF specification for this
kind of styles. However an existing master page definition is always reusable
using the ``clone`` option.

Page headers and footers
~~~~~~~~~~~~~~~~~~~~~~~~~

Page headers and footers are optional components of master pages; they are just
containers for almost any kind of document content elements (such as regular
paragraphs, tables, images and so on). They are created "in place" using special
master page methods, namely ``set_header()`` and ``set_footer()``. Each of
these methods returns an ODF element that can be used later as a context to
append content elements. The following example creates a page style with a
header and a footer, each one containing a single paragraph::

   mp = odf_create_style('master page', 'MyNewPageStyle')
   h = mp.set_header()
   h.append_element(odf_create_paragraph(text='Header text', style='Standard')
   f = mp.set_footer()
   f.append_element(odf_create_paragraph(text='Footer text', style='Standard')

It's possible to call ``set_header()`` and ``set_footer()`` with one or more
existing ODF elements as arguments, so the given elements are directly
put in the header or footer.

Every ``set_header()`` or ``set_footer()`` removes and replaces any previously
existing header/footer. It's always possible to retrieve the header or the
footer using ``get_header()`` or ``get_footer()``, and to remove them using
``delete_header()`` and ``delete_footer()``.

Note that the header and footer extensions of a master page don't include any
layout information; the style of the header and footer of a master page is
specified through the header and footer extensions of the corresponding page
layout.

Background objects
~~~~~~~~~~~~~~~~~~~

A page master doesn't include any direct page background specification, knowing
that the background color and/or the background image are defined by the
*page layout* that is used by the page master (see below).

However, it's possible to attach *frames* to a master page (through
``insert_element()`` and ``append_element()``). Frames are containers for
various kinds of content elements, including graphical ones, so they provide a
practical way to compose backgrounds. However, the user should check the
compatibility with the target displaying/printing applications according to
the document type. Simply put, frames attached to master pages are common in
presentation documents, not in text document.

Page layouts
~~~~~~~~~~~~~

Page layouts are generally invisible for the end users, knowing that a typical
ODF-compliant text processor regards them as extensions of the main page styles,
namely master pages. However, a page layout is defined through the lpOD API
using the same logic as other style objects. It may be created using
``odf_create_style()`` with ``page layout`` as the family argument and a
unique name (mandatory when the object is attached to a document). The
``display name`` optional parameter is ignored for this kind of style. On the
other hand, a specific ``page usage`` parameter, whose legal values are
``all``, ``left``, ``right``, ``mirrored`` (default: ``all``) allows the
user to specify the type of pages that the page layout should generate.

The list of other possible properties that may be set with page layouts through
``odf_create_style()`` is described in section §15.2 of the ODF specification;
some of these properties may be set using the following lpOD mnemonics:

- ``height`` and ``width``: the page size values, in regular ODF-compliant
  notation (ex: '21cm');
- ``number format``, ``number prefix``, and ``number suffix``: the format,
  prefix and suffix which define the default number representation for page
  styles, which is used to display page numbers within headers and footers
  (see the "Number styles" section in the present documentation);
- ``paper tray``: to specify the paper tray to use when printing the document;
  it's a proprietary information knowing that the paper tray names depend on
  the printer model; however, this property, if defined, may be safely set to
  ``default``, so the default tray specified in the printer configuration
  settings will be used.
- ``orientation``: specifies the orientation of the printed page, may be
  ``portrait`` or ``landscape`` (default: ``portrait``);
- ``margin xxx`` (where xxx is ``left``, ``right``, ``top`` or ``bottom``):
  to control the margins of the page;
- ``border xxx`` (where ``xxx`` is ``left``, ``right``, ``top`` or ``bottom``):
  a 3-part string to specify the thickness, the line style and the line color
  (according to the XSL/FO grammar);
- ``border``: a 3-part string to specify the thickness, the line style and the
  line color (according to the XSL/FO grammar), for all the four borders;
- ``footnote height``: defines the maximum amount of space on the page that a
  footnote can occupy.

Page layout objects support the ``set_background()`` method, allowing to set
a background color or a background image.

A page layout object may have a header and/or a footer extension, respectively
set using ``set_header()`` and/or ``set_footer()``. These methods, when used
with a page layout object, allow the applications to extend the page layout in
order to specify layout informations that control the header and the footer of
the master page(s) that use the page layout. Of course, the layout properties
are not the same as the content properties. Knowing that headers and footers
may have different margins and borders than the page body, ``set_header()`` and
``set_footer()`` accept the same margin- and border-related named parameters
as ``odf_create_style()`` when used to create a page layout. On the other hand,
``set_header()`` and ``set_footer()`` return ODF elements that support the
generic ``set_background()`` method; so it's possible to call use this method
separately from the page layout main object and from both its header and
footer extensions, allowing the user to set specific backgrounds in the 3 parts
of the affected page.

A page layout style may specify a columned page. A ``set_columns()`` method,
called from a page layout object, does the job with the number of columns as
a first mandatory argument and a ``gap`` optional name parameter that specifies
the gap between columns. By default, all columns have the same width. It's
possible to set extra properties in order to specify each column individually
and to define a separator line between columns, through the low-level (lpOD 1)
API.

Drawing page styles
~~~~~~~~~~~~~~~~~~~

A drawing page style is an optional style specification that may be used in
presentation and drawing documents in order to set some presentation dynamic
properties and/or a particular background.

Such a style is created using ``odf_create_style()`` with ``drawing page`` as
the family. Many style properties may be set with the constructor or later
with ``set_properties()``; some are related to the page background while others
regard the dynamic behaviour of the pages (transition effets, display duration).
The first category consists of the full set of fill properties which are used
to define drawing object fill characteristics, while the second category
includes the full set of presentation page dynamic. These properties are
described in the sections 15.14 and 15.36 of the ODF 1.1 specification.

The attribute names and the possible values should be used as they are described
in the ODF standard; the lpOD API doesn't presently provide non-standard
shortcuts or mnemonics.

The example below creates a drawing page style which specifies that the pages
using it will appear with a slow cross-fade transition, then will be displayed
during 12 seconds each; these pages will have a monochrome background filled
with a green color::

   dps = odf_create_style('drawing page', 'MyDrawPageStyle',
                        'presentation:transition-type'='automatic',
                        'presentation:transition-speed'='slow',
                        'presentation:duration'='PT00H00M12S',
                        'smil:type'='fade',
                        'smil:subtype'='crossfade'
                        'draw:fill'='solid',
                        'draw:fill-color'='#00ff00'
                        )


Presentation page layouts
~~~~~~~~~~~~~~~~~~~~~~~~~

A presentation page layout (whose use is optional with a draw page) is not
really a style. However, it's described  and designed as a style in the ODF
specification, so it's processed as a style through the lpOD API. Practically,
a presentation page layout typically comes from a template presentation
document and consists of a set of placeholders, each one specifying the class
and the coordinates of a shape (see §14.15 then §9.6 in the ODF specification
for details), knowing that a placeholder indicates a location in a page where
the user must fill in some information.

Like other styles, a presentation page layout is identified by a ``name`` and
owns an optional ``display name``. It's created by the ``odf_create_style()``
generic style constructor, with ``presentation page layout`` as family name.
Remember that this family is *not* related by any mean to the ``page layout``
family.

Once created, a presentation page layout is populated using its element-specific
``set_placeholder()`` method. This method can either append a previously created
(and free) placeholder object, or create and append a new placeholder.

A placeholder may be created through ``odf_create_placeholder()`` with the
following parameters:

- ``object``: the class of the shape which should appear at the placeholder's
   position, knowing that the possible values are those of the §9.6.1 in the
   ODF specification, namely ``title``, ``outline``, ``subtitle``, ``text``,
   ``graphic``, ``object``, ``chart``, ``table``, ``orgchart``, ``page``,
   ``notes``, ``handout``;
- ``position``, the coordinates of the placeholder, as a list of 2 strings
   containing the X and Y positions (each string specifies the number
   and the unit, ex. "1cm", "2pt");
- ``size``: the absolute size of the placeholder, provided in the same format
   as the position, in length or percentage.

Once created, a placeholder may be integrated with the generic
``insert_element()`` or  ``append_element()`` called from a presentation page
layout object. With a placeholder object as its only one argument, the
``set_placeholder()`` method does the same job as ``append_element()``, but,
of course, it works from presentation page layout objects only. On the other
hand, when called with an string (the object class) as its first argument, and
the position and size named parameters, ``set_placeholder()`` creates and
directly appends the placeholder. It always returns the new placeholder element.


