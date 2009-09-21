################################
Level 1 Functional specification
################################

**WORKING DRAFT**

.. contents::

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


Basic text containers
=====================

Paragraphs
-----------

A paragraph element inherits all the basic element features introduced above,
and owns the following ones.

All the visible text content of a document is hold in paragraphs (and in
*headings*, which are special paragraphs, cf. later in this documentation).
A paragraph is basically a text container associated with a layout style.

The text content may be directly hold as the text of the paragraph element;
however, a paragraph can contain sub-paragraph elements so-called *spans*
(introduced later in this documentation).
 

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
as well. As a consequence, a heading may be regarded as a subclass of the
paragraph class.

However, a heading is a special paragraph which owns additional properties
related to its hierarchical level and its numbering. As an consequence, some
heading-specific methods are provided, and the constructor function is
``odf_create_heading()``. The ``text`` and ``style`` parameters are allowed
like with ``odf_create_paragraph()``. In addition, this constructor gets more
optional parameters:

- ``level`` which indicates the hierarchical level of the heading (default 1,
  i.e. the top level);

- ``restart numbering``, a boolean which, if true, indicates that the numbering
  should be restarted at the current heading (default false);

- ``start value`` to restart the heading numbering of the current level at a
  given value;

- ``suppress numbering``, a boolean which, if true, indicates that the heading
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
potentially numbered. By default, the numbering is related to the whole
document starting to 1. However, optional properties allow the user to change
this behaviour.

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
a heading. It's a sub-paragraph text container whose essential function is to
associate a particular feature to a limited text run instead of a whole
paragraph.

There are several kinds of text spans.

- Style spans: a text span can be defined in order to apply a special style to
  a part of the content of a paragraph/heading. As a consequence, it's
  associated to a text style.
- Hyperlinks: a hyperlink can be defined in order to associate a part of the
  content of a paragraph/heading to another content element in the current
  document or to an external resource.

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
is ignored. The following instructions create two text spans with a so-called
"HighLight" style; the first one applies the given style to any "The lpOD
Project" substring while the second one does it once on fixed length substring
at a given position, ``p`` being the target paragraph::

   p.set_span(filter='The lpOD Project', style='HighLight')
   p.set_span(position=3, length=5, style='HighLight')

A hyperlink span is created through ``set_hyperlink()``, which waits for the
same positioning parameters (by regex or by position and length). However,
there is no style, and a ``url`` parameter (whose value is any kind of path
specification that is supported by the application) is required instead.
A hyperlink span can't contain any other span, while a style span can contain
one or more spans. As a consequence, the only one way to provide a hyperlink
span with a text style consists of embedding it in a style span.

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
``p`` container (note that the ``length`` parameter is omitted, meaning that
the hyperlink will run up to the end)::

   p.set_hyperlink(position=-5, url='http://here.org')

The sequence hereafter show the way to set a style span and a hyperlink for
the same text run. The style span is created first, then it's used as the
context to create a hyperlink span that spreads over its whole content::

   s = p.set_span(filter='The lpOD Project', style='Outstanding')
   s.set_hyperlink(position=0, url='http://www.lpod-project.org')

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

Tables
-------

An ``odf_table`` object is a structured container that holds two sets
of objects, a set of *rows* and a set of *columns*, and that is
optionally associated with a table style.

The basic information unit in a table is the *cell*. Every cell is
contained in a row. Table columns don't contain cells; an ODF column
holds information related to the layout of a particular column at the
display time, not content data.

A cell can directly contain one or more paragraphs. However, a cell
may be used as a container for high level containers, including lists,
tables, sections and frames.

Every table is identified by a name (which must be unique for the
document) and may own some optional properties.

Table creation and retrieval
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A table is created using ``odf_create_table()`` with a mandatory name
as its first argument and the following optional parameters:

- ``width``, ``length``: the initial size of the new table
  (rows then columns), knowing that it's zero-sized by default
  (beware: because cells are contained in rows, no cell in created if
  as long as ``width`` is less than 1);
- ``style``: the name of a table style, already existing or to be
  defined;
- ``cell style``: the style to use by default for every cell in the table;
- ``protected``: a boolean that, if true, means that the table should
  be write-protected when the document is edited through a user-oriented,
  interactive application (of course, such a protection doesn't prevent
  an lpOD-based tool from modifying the table)(default is false);
- ``protection key``: a (supposedly encrypted) string that represents
  a password; if this parameter is set and if ``protected`` is true,
  a end-user interactive application should ask for a password that matches
  this string before removing the write-protection (beware, such a protection
  is *not* a security feature);
- ``display``: boolean, tells that the table should be visible; default is true;
- ``print``: boolean, tells that the table should be printable; however, the
  table is not printable if ``display`` is false, whatever the value of
  ``print``; default is true;
- ``print ranges``: the cell ranges to be printed, if some areas are not to
  be printed; the value of this parameter is a space-separated list of cell
  ranges expressed in spreadsheet-style format (ex: "E6:K12").

Once created, a table may be incorporated somewhere using ``insert_element()``.

A table may be retrieved in a document according to its unique name using
the context-based ``get_table_by_name()`` with the name as argument. It may
be selected by its sequential position in the list of the table belonging
to the context, using ``get_table_by_position()``, with a zero-based numeric
argument (possibly counted back from the end if the argument is negative).
In addition, it's possible to retrieve a table according to its content,
through ``get_table_by_content()``; this method returns the first table (in
the order of the document) whose text content matches the given argument,
which is regarded as a regular expression.

Table content retrieval
~~~~~~~~~~~~~~~~~~~~~~~
A table object provides methods that allow to retrieve any column, row or cell
using its logical position. A position may be expressed using either zero-based
numeric coordinates, or alphanumeric, spreadsheet-like coordinates. For example
the top left cell should be addressed either by [0,0] or by "A1". On the other
hand, numeric coordinates only allow the user to address an object relatively to
the end of the table; for example, [-1,-1] designates the last cell of the last
row whatever the table size.

Table object selection methods return a null value, without error, when the
given address is out of range.

The number of rows and columns may be got using ``get_size()``.

An individual cell is selected using ``get_cell()`` with either a pair of
numeric arguments corresponding to the row then the columns, or an alphanumeric
argument whose first character is a letter. The second argument, if provided,
is ignored as soon as the first one begins with a letter; if only one numeric
argument is provided, the column number is assumed to be 0.

The two following instructions are equivalent and return the second cell of the
second row in a table (assuming that ``t`` is a previously selected table)::

   c = t.get_cell('B2')
   c = t.get_cell(1, 1)

``get_row()`` allows the user to select a table row as an ODF element. This
method requires a zero-based numeric value.

``get_column()`` works according to the same logic and returns a table column
ODF element.

The full set of row and column objects may be selected using the table-based
``get_row_list()`` and ``get_column_list()`` methods. By default these methods
return repectively the full list of rows or columns. They can be restricted to
a specified range of rows or columns. The restriction may be expressed through
two numeric, zero-based arguments indicating the positions of the first and the
last item of the range. Alternatively, the range may be specified using a more
"spreadsheet-like" syntax, in only one alphanumeric argument representing the
visible representation of the range through a GUI; this argument is the
concatenation of the visible numbers of the starting and ending elements,
separated by a ":", knowing that "1" is the visible number of the row zero
while "A" is the visible number or the column zero. As a consequence, the two
following instructions are equivalent and return a list including the rows from
5 to 10 belonging to the table ``t``::

   rows = t.get_row_list(5, 10)
   rows = t.get_row_list('6:11')

According to the same logic, each of the two instruction below returns the
columns from 8 to 15::

   cols = t.get_column_list(8, 15)
   cols = t.get_column_list('I:P') 

Once selected, knowing that cells are contained in rows, a row-based
``get_cell()`` method is provided. When called from a row object,
``get_cell()`` requires the same parameters as the table-based ``get_column()``
method. For example, the following sequence returns the same cell as in the
previous example::

   r = t.get_row(1)
   c = r.get_cell(1)

Cell range selection
~~~~~~~~~~~~~~~~~~~~

The API can extract rectangular ranges of cells in order to allow the
applications to store and process them out of the document tree, through
regular 2D tables. The range selection is defined by the coordinates of the
top left and the bottom right cells of the target area. The selection is
done using the table-based ``get_cells()`` method, with two possible syntaxes,
i.e. the spreadsheet-like one and the numeric one. The first one requires an
alphanumeric argument whose first character is a letter and that includes a
':', while the second one requires four numeric arguments. As an example, the
two following instructions, which are equivalent, return a bi-dimensional array
corresponding to the cells of the ``B2:D15`` area of a table::

   cells = t.get_cells("B2:D15")
   cells = t.get_cells(1,1,14,3)

Note that, after such a selection, ``cells[0,0]`` contains the "B2" cell of
the ODF table.

If ``get_cells()`` is called without argument, the selection covers the whole
table.

A row object has its own ``get_cell()`` method. The row based version of
``get_cells()`` returns, of course, a one-column table of cell objects. When
used without argument, it selects all the cells of the row. It may be called
with either a pair of numeric arguments that represent the start and the end
positions of the cell range, or an alphanumeric argument (whose the numeric
content is ignored and should be omitted) corresponding to the start and end
columns in conventional spreadsheet notation. The following example shows two
ways to select the same cell range (beginning at the 2nd position and ending
at the 26th one) in a previously selected row::

   cells = r.get_cells('B:Z')
   cells = r.get_cells(1, 25)

If the user needs to select a range of cells as a list instead of a 2D array,
the ``get_cell_list()`` method should preferred. This method requires the same
arguments as ``get_cells()`` exists in table- and row-based versions.

**Note**: The range selection feature provided by the level 1 API is a
building block for the lpOD level 2 business-oriented cell range objects.

Row and column customization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The objects returned by ``get_row()`` and ``get_column()`` can be customized
using the standard ``set_attribute()`` or ``set_attributes()`` method. Possible
attributes are:

- ``style``: the name of the applicable style (which should be at display time
  a valid row or column style);
- ``cell style``: the default style which apply to each cell in the column or
  row unless this cell has no defined style attribute;
- ``visibility``: specifies the visibility of the row or column; legal values
  are ``visible``, ``collapse`` and ``filter``.				 

Table expansion
~~~~~~~~~~~~~~~

A table may be expanded vertically and horizontally, using its ``add_row()`` and
``add_column()`` methods.

``add_row()`` allows the user to insert one or more rows at a given position in
the table. The new rows are copies of an existing one. Without argument, a
single row is just appended as the end. A ``number`` named parameter provides
the number of rows to insert.

An optional ``before`` named parameter may be provided; if defined, the value
of this parameter must be a row number (in numeric, zero-based form) in the
range of the table; the new rows are created as clones of the row existing at
the given position then inserted at this position, i.e. *before* the original
reference row. A ``after`` parameter may be provided instead of ``before``;
it produces a similar result, but the new rows are inserted *after* the
reference row. Note that the two following instructions produce the same
result::

   t.add_row(number=1, after=-1)
   t.add_row()

The ``add_column()`` does the same thing with columns as ``add_rows()`` for
rows. However, because the cells belong to rows, it works according to a very
different logic. ``add_column()`` inserts new column objects (clones of an
existing column), the it goes through all the rows and inserts new cells
(cloning the cell located at the reference position) in each one.

Of course, it's possible to use ``insert_element()`` in order to insert a row,
a column or a cell externally created (or extracted from an other table from
another document), provided that the user carefully checks the consistency of
the resulting contruct. As an example, the following sequence appends a copy
of the first row of ``t1``after the 5th row of ``t2``::

   to_be_inserted = t1.get_row(0).clone();
   t2.insert_element(to_be_inserted, after=t2.get_row(5))

Row and column group handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The content expansion and content selection methods above work with the table
body. However it's possible to manage groups of rows or columns. A group may
be created with existing adjacent rows or columns, using ``set_row_group()``
and ``set_column_group()`` respectively. These methods take two mandatory
arguments, which are the numeric positions of the starting and ending elements
of the group. In addition, an optional ``display`` named boolean parameter
may be provided (default=true), instructing the applications about the
visibility of the group.

Both ``set_row_group()`` and ``set_column_group()`` return an object which can
be used later as a context object for any row, column or cell retrieval or
processing. An existing group may be retrieved according to its numeric
position using ``get_row_group()`` or ``get_column_group()`` with the position
as argument, or without argument to get the first (or the only one) group.

A group can't bring a particular style; it's just visible or not. Once created,
its visibility may be turned on and off by changing its ``display`` value
through ``set_attribute()``.

A row group provides a ``add_row()`` method, while a column group provides a
``add_column()`` method. These methods work like their table-based versions,
and they allow the user to expand the content of a particular group.

A group can contain a *header* (see below).

Table headers
~~~~~~~~~~~~~

One or more rows or columns in the beginning of a table may be organized as
a *header*. Row and columns headers are created using the ``set_row_header()``
and ``set_columns_header()`` table-based methods, and retrieved using
``get_row_header()`` and ``get_column_header()``. A row header object brings its
own ``add_row()`` method, which works like the table-based ``add_row()`` but
appends the new rows in the space of the row header. The same logic applies to
column headers which have a ``add_column()`` method.

A table can't directly contain more than one row header and one column header.
However, a column group can contain a column header, while a row group can
contain a row header. So the header-focused methods above work with groups as
well as with tables.

A table header doesn't bring particular properties; it's just a construct
allowing the author to designate rows and columns that should be automatically
repeated on every page if the table doesn't fit on a single page.

The ``get_xxx()`` table-based retrieval methods ignore the content of the
headers. However, it's always possible to select a header, then to used it as
the context object to select an object using its coordinates inside the header.
For example, the first instruction below gets the first cell of a table body,
while the third and third instructions select the first cell of a table header::

   c1 = table.get_cell(0,0)
   header = table.get_header()
   c2 = header.get_cell(0,0)

Individual cell property handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A cell owns both a *content* and some *properties* which may be processed
separately.

The cell content is a list of one or more ODF elements. While this content is
generally made of a single paragraph, it may contain several paragraphs and
various other objects. The user can attach any content element to a cell using
the standard ``insert_element()`` method. However, for the simplest (and the
most usual) cases, it's possible to use ``set_text()``. The cell-based
``set_text()`` method diffs from the level 0 ``set_text()``: it removes the
previous content elements, if any, then creates a single paragraph with the
given text as the new content. In addition, this method accepts an optional
``style`` named parameter, allowing the user to set a paragraph style for the
new content. To insert more content (i.e. additional paragraphs and/or other
ODF elements), the needed objects have to be created externally and attached
to the cell using ``insert_element()``. Alternatively, it's possible to remove
the existing content (if any) and attach a full set of content elements in a
single instruction using ``set_content()``; this last cell method takes a list
of arbitrary ODF elements and appends them (in the given order) as the new
content.

The ``get_content()`` cell method returns all the content elements as a list.
For the simplest cases, the cell-based ``get_text()`` method directly returns
the text content as a flat string, without any structural information and
whatever the number and the type of the content elements.

The properties may be accessed using ``set_properties()`` and
``get_properties()``; ``set_properties()`` works with the following optional
named parameters:

- ``style``: the name of a cell style;
- ``type``: the cell value type, which may be one of the ODF supported data
   types, used when the cell have to contain a computable value (omitted with
   text cells);
- ``value``: the numeric computable value of the cell, used when the ``type`` is
   defined;
- ``currency``: the international standard currency unit identifier (ex: EUR,
   USD), used when the ``type`` is ``currency``;
- ``formula``: a calculation formula whose result is a computable value (the
   grammar and syntax of the formula is application-specific and not ckecked
   by the lpOD API (it's stored as flat text and not interpreted);
- ``protected``: boolean (default false), tells the applications that the cell
   can't be edited.

All the existing properties may be retrieved using the cell ``get_properties()``
which returns a list of named parameters.

Cell span extension
~~~~~~~~~~~~~~~~~~~

A cell may be expanded in so it covers one or more adjacent columns and/or rows.
The cell-based ``set_span()`` method allows the user to control this expansion.
It takes ``rows`` and ``columns`` as parameters, specifying the number of rows
and the number of columns covered. The following example selects the "B4" cell
then expands it over 4 columns and 3 rows::

   cell = table.get_cell('B4')
   cell.set_span(rows=3, columns=4)

The existing span of a cell may be get using ``get_span()``, which returns the
``rows`` and ``columns`` values.

This method changes the previous span of the cell. The default value for each
parameter is 1, so a ``set_span()`` without argument reduces the cell at its
minimal span.

When a cell is covered due to the span of another cell, it remains present and
holds its content and properties. However, it's possible to know at any time if
a given cell is covered or not through the boolean ``is_covered()`` cell method.
In addition, the span values of a covered cell are automatically set to 1, and
``set_span()`` is forbidden with covered cells.

Note that the API doesn't support cell spans that spread across table header
or group boundaries.

Item lists
----------

A list is a structured object that contains an optional list header followed by
any number of list items. The list header, if defined, contains one or more
paragraphs that are displayed before the list. A list item can contain
paragraphs, headings, or lists. Its properties are ``style``, that is an
appropriate list style, and ``continue numbering``, a boolean value that, if
true, means that *if the numbering style of the preceding list is the same as the current list, the number of the first list item in the current list is the number of the last item in the preceding list incremented by one* (default=false).

  .. figure:: figures/lpod_list.png
     :align: center

A list is created using ``odf_create_list()``, then inserted using
``insert_element()`` as usual.

A list header is created "in place" with ``set_header()``, called from a list
element; this method returns an ODF element that can be used later as a context
to append paragraphs in the header. Alternatively, it's possible to call the
list-based ``set_header()`` with one or more existing paragraphs as arguments,
so these paragraphs are immediately incorporated in the new list header. Note
that every use of ``set_header()`` replaces any existing header by a new one.

Regular list items are created in place (like the optional list header) using
``add_item()`` wich creates one or more new items and inserts them at a
position which depends on optional parameters, according to the same kind
of logic than the tabble-based ``add_row()`` method. Without any argument, a
single item is appended at end of the list. An optional ``before`` named
parameter may be provided; if defined, the value of this parameter must be a
row number (in numeric, zero-based form) in the range of the list; the new
items are inserted *before* the original item that existed at the given
position. Alternatively, a ``after`` parameter may be provided instead of
``before``; it produces a similar result, but the new items are inserted
*after* the given position. If a additional ``number`` parameter is provided
with a integer value, the corresponding number of identical items are
inserted in place.

By default, a new item is created empty. However, as a shortcut for the most
common case, it's possible to directly create it with a text content. To do
so, the text content must be provided through a ``text`` parameter; an
optional ``style`` parameter, whose value is a regular paragraph style, may
provided too. The new item is then created with a single paragraph as content
(that is the most typical situation).

Another optional ``start value`` parameter may be set in order to restart the
numbering of the current list at the given value. Of course, this start value
apply to the first inserted item if ``add_item()`` is used to create many items
in a single call.

``add_item()`` returns the newly created list of item elements. In addition,
an existing item may be selected in the list context using ``get_item()`` with
its numeric position. A list item is an ODF element, so any content element
may be attached to it using ``insert_element()``.

Note that, unlike headings, list items don't have an explicit level property.
All the items in an ODF list have the same level. Knowing that a list may be
inside an item belonging to another list, the hierarchy is represented by the
structural list imbrication, not by item attributes.

Data pilot (pivot) tables [todo]
--------------------------------

Sections [todo]
---------------

Draw pages
----------

Draw pages are structured containers belonging to presentation or drawing
documents. They shouldn't appear in text or spreadsheet documents.

A draw page can contain forms, drawings, frames, presentation animations, and/or
presentation notes (§9.1.4 in the ODF specification).

  .. figure:: figures/lpod_drawpage.png
     :align: center

*[Unfinished diagram]*

A draw page is created using ``odf_create_draw_page()`` and integrated through
``insert_element()``. Note that a draw page should be inserted at the document
body level, knowing that it's a top level content element.

A draw page must have an identifier (unique for the document) and may have the
following parameters, to be set at creation time or later:

- ``name``: an optional, but unique if provided, name (which may be made visible
   for the end-users);

- ``style``: the name of a drawing page style (existing or to be defined);

- ``master``: the name of a master page whose structure is appropriate for
   draw pages (beware, a master page defined for a text document don't always
   fit for draw pages);

- ``layout``: the name of a *presentation page layout* as defined
   in §14.15 of the ODF specification (if such a layout is used); beware, such
   objects are neither similar nor related to general *page layouts* as defined
   in §14.3 (a general page layout may be used through a *master page* only,
   and should never be directly connected to a draw page) (sorry, this confusing
   vocabulary is not a choice of the lpOD team;-)

The following example creates a draw page with these usual parameters and
integrates it as the last page of a presentation document::

   dp = odf_create_draw_page('xyz1234',
                           name='Introduction',
                           style='DrawPageOneStyle',
                           master='DrawPageOneMaster',
                           layout='DrawPageOneLayout
                           )
   document.append_element(dp)

All these parameters may retrieved or changed later using ``get_properties()``
and ``set_properties()`` with draw page objects.

An existing draw page may be retrieved in the document through
``get_draw_page()`` with the identifier as argument.

Populating a draw page doesn't require element-specific methods, knowing that:

- all the fixed parts, the layout and the background are defined by the
   associated ``style``, ``master`` and ``layout``;
- all the content objects are created separately and attached to the draw page
   using the regular ``insert_element()`` or ``append_element()`` method from
   the draw page object.

Fields and forms
================

Declared fields and variables [todo]
------------------------------------

Text fields [todo]
-------------------

Graphic content
===============

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
   a string, separated by a space, if needed;

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


Shapes [todo]
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

-``width``: the table width (in length, not in columns), provided either in
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

Cell styles [todo]
~~~~~~~~~~~~~~~~~~

Row and column styles [todo]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

   .. figure:: figures/lpod_page_style.png
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


Metadata
========

Pre-defined [todo]
------------------

User defined [todo]
-------------------

Application settings [todo]
===========================

