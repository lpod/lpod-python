#################
Level 1 coverage
#################

.. contents::

Common features
===============

All the lpOD level 0 features are available through the level 1 API, so the
applications can create, retrieve or delete any element.  They can create,
select, update or delete any attribute or sub-element in a previously retrieved
element.

The API provides functions and methods.

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

An element-specific method works with specific ODF elements only, according to
their particular role. For example ``set_header()`` is provided with ODF master
pages, because a header is an extension of a page style element, while
``set_background()`` is available with objects where a background definition
makes sense (such as page layouts or paragraph styles).

Common element-specific methods
===============================

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
elements; they can be inserted later at the right place. Other elements, whose
definition doesn't make sens out of a specific context, are directly created in
place.

Any element is able to be serialized and exported as an XML, UTF8-encoded
string. Symmetrically, an element can be created from an application- provided
XML string. As a consequence, lpOD-based applications can remotely transmit or
receive any kind of ODF content.

The level 1 API is not validating, so the user is responsible of the ODF
compliance (the API doesn't automatically prevent the applications from
inserting an element at the wrong place).

Any element can be retrieved according to its sequential position in a given
context or its text content (if defined), through methods like
``get_xxx_by_position()`` and ``get_xxx_by_content()`` where "xxx" is the
element type (i.e. "paragraph", "heading", etc). For example::

  element = context.get_xxx_by_position(p)
  element = context.get_xxx_by_content(regex)

It's possible to get the list of elements of a known type in the context, using
``get_xxx_list()``.

The two lines above retrieve an element among the children of a given 'context'
element. The first one selects the child element at the given ``p`` position.
The given position is an integer; the first position is zero; negative positions are counted back from the last (-1 is the last position).
The second instruction retrieves the first element whose text content matches a
given ``regex`` regular expression. Knowing that the regexp could be matched by
more than one element, the same method is available in a list context.

Addtional retrieval methods are available according to the element type.

Every search method operates in context, knowing that the context could be the
whole document as well as a particular element (section, table, etc).


Basic text containers
=====================

Paragraphs
-----------

A paragraph element inherits all the basic element features introduced above,
and owns the following ones.

Creation and attachment
~~~~~~~~~~~~~~~~~~~~~~~
A paragraph can be created with a given style and a given text content. The
default content is an empty string. There is not default style; a paragraph can
be created without explicit style, as long as the default paragraph style of the
document is convenient for the application. The style and the text content can
be set or changed later.

A paragraph is created (as a free element) using the ``odf_create_paragraph()``
function, with a ``text`` and a ``style`` optional parameters. It may be
attached later through the standard ``append_element()`` or
``insert_element()`` method::

   p = odf_create_paragraph(text='My first paragraph', style='TextBody')
   document.append_element(p)

Retrieval
~~~~~~~~~
Like any element, a paragraph can be retrieved in a given context using
``get_paragraph_by_position()`` or ``get_paragraph_by_content()``, and
``get_paragraph_list()`` returns all the paragraphs in the context.

The ``get_paragraph_list()`` with a ``style`` named parameter restricts the
search in order to get the paragraphs which use a given style.

Text processing
~~~~~~~~~~~~~~~
The traditional string editing methods (i.e. regex-based search & replace
functions) are available against the text content of a paragraph.

``search()`` in a element-based method which takes a search string (or a
regular expression) as argument a,d returns the position of the first substring
matching the argument in the text content of the element. A null return value
means no match. This method works with the direct text content of the calling
element, not with the children, so it makes sense with paragraphs, headings and
text spans only.

``replace()`` is a context-based method. It takes two arguments, the first one
being a search string like with ``search()``, the second one a text which will
replace any substring matching the search string. The return value of the
method is the total number of matches. If the second argument is an empty
string, every matching substring is just deleted without replacement. If the
second argument is missing, then nothing is changed, and the method just counts
the number of matches. This method is context-based, so it recursively works on
all the paragraphs, headers and spans below the calling element; the calling
element may be any ODF element, including the elements that can't directly own a
text content. It may be called at the document level.

Multiple spaces and intra-paragraph breaks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
According to the ODF specification, a sequence of multiple spaces is regarded
as a single space, so multiple spaces must be represented by an appropriate
ODF element. In the same way, tabulation marks and line breaks can't be
directly included in the text content, and must be replaced by appropriate
ODF elements. This API transparently does the job: it allows the user to put
in a paragraph a text strings containing multiple spaces, tab stops ("\t")
and/or line breaks ("\n").

Headings
---------
All the features that apply to paragraphs, as described above, apply to headings
as well.

However, a heading is a special paragraph which owns additional properties
related to its hierarchical level and its numbering. As an consequence, some
heading-specific methods are provided, and the constructor function is
``odf_create_heading()``. The ``text`` and ``style`` parameters are allowed
like with ``odf_create_paragraph()``. In addition, this constructor gets more
optional parameters:

- ``level`` which indicates the hierarchical level of the heading (default 1,
  i.e. the top level);

- ``restart-numbering``, a boolean which, if true, indicates that the numbering
  should be restarted at the current heading (default false);

- ``start-value`` to restart the heading numbering of the current level at a
  given value;

- ``suppress-numbering``, a boolean which, if true, indicates that the heading
  must not be numbered (default false).

See below for explanations about level and numbering.

In addition, the layout of the headings depends partly on the paragraph style
that individually apply to each one, and partly on the outline style of the
document (see the "Outline style" section in the present document).

Heading level
~~~~~~~~~~~~~
A heading owns a special property which indicates its hierarchical level in the
document. A "level" property can be set at creation time or later and changed at
any time. A heading without a level attribute is assumed to be at level 1, which
is the top level. The level may be any positive integer value (while the ODF
spec doesn't set an explicit limit, we don't recommend levels beyond 10).

Heading numbering
~~~~~~~~~~~~~~~~~~
Whatever the visibility of the numbers, all the headings of a given level are
potentially numbered. By default, the numbering is related to the whole document
starting to 1. However, optional properties allow the user to change this
behaviour.

An arbitrary, explicit numbering value can be set, so the automatic numbering
restarts from this value from the target heading element and apply to the
following headings at the same level.

The automatic numbering can be inhibited through an optional property which
prevents the current heading from being numbered.

In addition, the API allows the users to provide a heading with an arbitrary
hidden number. A hidden number is a static, user-provided value available for
applications that can't dynamically calculate the numbering, but safely ignored
by applications that support dynamic numbering in text documents.

Text spans
----------
A text span, in the lpOD scope, is a delimited area included in a paragraph or
a heading. There are several kinds of text spans.

- Style spans: a text span can be defined in order to apply a special style to
  a part of the content of a paragraph/heading. As a consequence, it's
  associated to a text style.
- Hyperlinks: a hyperlink can be defined in order to associate a part of the
  content of a paragraph/heading to the URI of an external resource.

Unlike paragraphs and headings, spans are created "in place", i.e. their
creation methods create and directly insert them in an existing container.

A style span is created through a ``set_span()`` method  from the object that
will contain the span. This object is a paragraph, a heading or an existing
styling span. The method must be called with a ``style`` named parameter whose
value should be the name of any text style (common or automatic, existing or to
be created in the same document). ``set_span()`` may uses a string or a regular
expression, which may match zero, one or several times to the text content of
the calling object, so the spans can apply repeatedly to every substring that
matches. The string is provided through a ``filter`` parameter. Alternatively,
``set_span()`` may be called with given ``position`` and ``length`` parameters,
in order to apply the span once whatever the content. Note that ``position`` is
an offset that may be a positive integer (starting to 0 for the 1st position),
or a negative integer (starting to -1 for the last position) if the user prefers
to count back from the end of the target. If the ``length`` parameter is omitted
or set to 0 the span runs up to the end of the target content. If ``position``
is out of range, nothing is done; if ``position`` is OK, extra length (if any)
is ignored. 

A hyperlink span is created through ``set_hyperlink()``, which waits for the
same positioning parameters (by regex or by position and length). However,
there is no style, and a ``uri`` parameter (whose value is any kind of URI
that is supported by the application) is required instead. A hyperlink span
can't contain any other span, while a style span can contain one or more spans.
As a consequence, the only one way to provide a hyperlink soan with a text style
consists of embed it in a style span.

The objects that can directly contain text spans are paragraphs, headings and
style spans. However, ``set_span()`` and ``set_hyperlink()`` may be called
from any higher level containers that can contain paragraphs or headings,
including the whole document. The span creation process may work recursively and
repeatedly in all the paragraphs, and spans below the calling ODF element. Both
return the list of the created span objects; a span object is an ODF element
itself. However, it's possible to prohibit this behaviour with a boolean
``norecurse`` parameter; if this option is set to ``true``, it prevents
``set_span()`` or ``set_hyperlink()`` from searching and processing the children
of the calling ODF element; of course, nothing is done when ``norecurse`` is the
current object is not able to directly able to contain text spans.

As an example, the instruction below applies the "HighLight" text style to
every "ODF" and "OpenDocument" substring in the ``p`` context::

   p.set_span(filter='ODF|OpenDocument', style='HighLight')

The following example associates an hyperlink in the last 5 characters of the
``p`` container::

   p.set_hyperlink(position=-5, length=5, uri='http://here.org')

The sequence hereafter show the way to set a style span and a hyperlink for
the same text run. The style span is created first, then it's used as the
context to create a hyperlink span that spreads over its whole content::

   s = p.set_span('The lpOD Project', style='Outstanding')
   s.set_hyperlink(position=0, uri='http://www.lpod-project.org')

Text marks and indices
======================

Position bookmarks
------------------
A position bookmark is a location mark somewhere in a text container, which is
identified by a unique name, but without any content.

A bookmark is created "in place", in a given element at a given position.  The
name and the target element are mandatory arguments. By default, the bookmark is put before the first character of the content.

The position can be explicitly provided by the user. Alternatively, the user can provide a regular expression, so the bookmark is set before the first substring that matches the expression::

  document.create_bookmark("BM1", paragraph, text="xyz")
  document.create_bookmark("BM2", paragraph, position=4)

The first instruction above sets a bookmark before the first substring matching
the given expression (here ``xyz``), which is processed as a regular expression. The second instruction sets a bookmark in the same paragraph at a given (zero-based), so before the 5th character.

In order to put a bookmark according to a regex that could be matched more than
once in the same paragraph, it's possible to combine the position and text
options, so the search area begins at the given position.

A bookmark can be retrieved by its unique name. The ODF element then can be
obtained as the parent of the bookmark element. However, if the bookmark is
located inside a span, its parent is the span element instead of a regular
paragraph. So another method is provided, that returns the main text container
of the bookmark. In the following example, the first line returns the parent of
a given bookmark (whatever the kind of element), while the second one returns
the paragraph (or heading) where the bookmark is located::

  context.get_bookmark("BM1").parent
  context.get_paragraph_by_bookmark("BM1")

Another method allows the user to get the offset of a given bookmark in the host ODF element. Beware: this offset is related to the text of the parent element (which could be a text span).

Range bookmarks
----------------
A range bookmark is an identified text range which can spread across paragraph
frontiers. It's a named content area, not dependant of the document tree
structure. It starts somewhere in a paragraph and stops somewhere in the same
paragraph or in a following one. Technically, it's a pair of special position
bookmarks, so called bookmark start and bookmark end, owning the same name.

The API allows the user to create a range bookmark and name it through an
existing content, as well as to retrieve and extract it according to its name.

Provided methods allow the user to get

- the pair of elements containing the bookmark start and the bookmark end
  (possibly the same);
- the text content of the bookmark (without the structure).

A retrieved range bookmark can be safely removed through a single method.

A range bookmark can be safely processed only if it's entirely contained in the
calling context. A context that is not the whole document can contain a bookmark
start or a bookmark end but not both.  In addition, a bookmark spreading across
several elements gets corrupt if the element containing its start point or its
end point is later removed.

Tables of content [todo]
========================

Indices [todo]
=======================

Notes
=======================
Generally speaking, a note is an object whose main function is to allow the user
to set some text content out of the main document body but to structurally
associate this content to a specific location in the document body. The content
of a note is stored in a sequence of one or more paragraphs and/or item lists.

The lpOD API supports three kinds of notes, so-called footnotes, endnotes and
annotations. Footnotes and endnotes have the same structure and differ only by
their display location in the document body, while annotations are specific
objects.

Footnote and endnote creation
-----------------------------

Footnotes and endnotes are created through the same method. The user must
provide a note identifier, i.e. an arbitrary code name (not visible in the
document), unique in the scope of the document, and a class option, knowing that
a note class is either 'footnote' or 'endnote'.

These notes are created as free elements, so they can be inserted later in place
(and replicated for reuse in several locations one or more documents). As a
consequence, creation and insertion are done through two distinct functions,
i.e. ``odf_create_note()`` and ``insert_note()``, the second one being a
context-related method.

While the identifier and the class are mandatory as soon as a note is inserted
in a document, these parameters are not required at the creation time. They can
be provided (or changed) through the insert_note() method.

The ``insert_note()`` method allows the user to insert the note in the same way
as a position bookmark (see above). As a consequence, its first arguments are
the same as those of the create bookmark method.  However, ``insert_note()``
requires additional arguments providing the identifier and the citation mark
(if not previously set), and the citation mark, i.e. the symbol which will be
displayed in the document body as a reference to the note. Remember that the
note citation is not an identifier; it's a designed to be displayed according
to a context-related logic, while the identifier is unique for the whole
document.

Regarding the identifier, the user can provide either an explicit value, or an
function that is supposed to return an automatically generated unique value. If
the class option is missing, the API automatically selects 'footnote'.

Footnote and endnote content
-----------------------------

A note is a container whose body can be filled with one or more paragraphs or
item lists at any time, before or after the insertion in the document. As a
consequence, a note can be used as a regular context for paragraph or list
appending or retrieval operations.

Note that neither the OpenDocument schema nor the lpOD level 1 API prevents the
user from including notes into a note body; however the lpOD team doesn't
recommend such a practice.

Annotation creation [tbc]
-------------------------

Annotations don't have identifiers and are directly linked to a given offset in
a given text container.

Change tracking [todo]
----------------------

Structured containers
=====================

Tables [todo]
-------------

Lists [todo]
------------

  .. figure:: figures/lpod_list.png
     :align: center

Data pilot (pivot) tables [todo]
--------------------------------

Sections [todo]
---------------

Draw pages [todo]
-----------------

  .. figure:: figures/lpod_drawpage.png
     :align: center


Fields and forms
================

Declared fields and variables [todo]
------------------------------------

Text fields [todo]
-------------------

Graphic content
===============

Frames [todo]
-------------

Shapes [todo]
-------------

Images [todo]
-------------

Animations [todo]
-----------------

Charts [todo]
-------------

Styles
======

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
with some style objects only) is used with a ``color`` and/or an ``uri`` named
parameters. The ``color`` value range is #000000-#ffffff, while ``uri`` should
be set to the URI of the graphic resource. If ``uri`` is set, some additional
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
with ``color`` and ``uri`` set to null.

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
"fo:font-name" and "fo:font-size". However, the API allows the use of
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
~~~~~~~~~~~~~~~~~~

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

Assuming that a "MyBlueText" text style has been defined according to the text
style creation example above, the following sequence creates a new paragraph
style whose text part is a clone of "MyBlueText", and whose paragraph part
features are the text justification, a first line 5mm indent, a black,
continuous, half-millimiter border line with a bottom-right, one millimeter grey
shadow, with other possible properties inherited from a "Standard" style::

   ps = odf_create_style('paragraph', 'BorderedShadowed',
                           'display name'='Strange Boxed Paragraph',
                           parent='Standard',
                           align='justify',
                           indent='5mm',
                           border='0.5mm solid #000000',
                           shadow='#808080 1mm 1mm'
                           )
   ts = document.get_style('text', 'MyColoredtext')
   ps.set_properties(area='text', ts)

Note that "MyColoredText" is reused by copy, not by reference; so the new paragraph
style will not be affected if "MyColoredText" is changed or deleted later.

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

If the ``image`` type is selected, the URI of an image resource must be
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
   ls.set_level_style(3, type='image', uri='bullet.jpg')

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
parameter names in the present version of the API could always be set through
the element-oriented methods of the level 0 API, knowing that get_level_style()
returns a regular element.


Graphic styles [todo]
---------------------

Numeric data formatting styles [tbc]
------------------------------------

Numeric styles in general are formatting styles that apply to computable values,
generally stored in fields or table cells. The covered data types are number,
currency, percentage, boolean, date and time.

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

A page style definition, so-called *master page*, is "*a template for pages in
a document*". It directly defines the static content "*that is displayed on all
pages*" that use it (such as headers and footers). In addition, a
*master page* is associated to a *page layout*, defined as a separate object
that describes "*the physical properties or geometry of a page, for example,
page size, margins, header height, and footer height*". The same *page layout*
may be used through several *page masters*.

A page style, as defined here, mainly applies to *text documents*. In such
documents, the pages are not statically defined; they are dynamically generated
by the viewing/printing applications according to their content (which changes
each time a piece of content is inserted, deleted or moved. As a consequence,
a *master page* is not used in the same way as, say, a paragraph style or a
list style, because there is no persistent text page object which could
directly contain a reference to a page style. A master page is essentially
referred to through page breaks. For example, each time a forced page break is
inserted, it's possible to specify the *master page* of the following page. In
addition, any *master page* may own a property that tells what should be the
*master page* to use after the current page (for example, a "Right page" style
may de defined in order to ensure that any page using it will be followed by
a page that will use a "Left page" style and vice-versa).

*Master page* objects apply to presentation and drawing documents, that use
statically defined draw pages, so the page style logic strongly differs, so
the *master page* object is not the exactly same for any document class.
The present section describes the page styling API for *text documents only*.

   .. figure:: figures/lpod_page_style.png
      :align: center

Master pages
~~~~~~~~~~~~~

A master page is created and retrieved the same way as other styles.

To create a master page through the generic ``odf_create_style()`` function,
the family argument is ``master page`` and it's followed by an arbitrary name.
A master page may, like other styles, have a display name distinct from its
name. In addition, a full master page definition allows the following named
parameters:

- ``page layout``: the unique name of a *page layout*, existing or to be defined
  in the same document;
- ``next``: the master page to apply to the following page, as soon as the
  current page is entirely filled, knowing that the current master page is used
  for the next page by default.

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


Metadata
========

Pre-defined [todo]
------------------

User defined [todo]
-------------------

Application settings [todo]
===========================

