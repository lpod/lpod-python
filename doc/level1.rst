#################
Level 1 coverage
#################

Common features
===============

The API can create, retrieve or delete any element.
It can create, get, update or delete any attribute or sub-element in a
previously retrieved element. Regarding an attribute, the same method is used in
order to create or update, while an element creation require an explicit method.

For any method that require more than 2 arguments, all the arguments but the
first one are named.

The calling object is either the document, or the context element.

Common element-specific methods
===============================

Any ODF element in the level 1 API inherits all the features of the underlying
XML element.

Every ODF element comes with methods that directly return its parent, next
sibling, previous sibling, and the list of its children. These methods (which
are provided by the underlying XML API) are available whatever the element type.

Any element provides a delete and a copy method. The deletion removes the
element itself and all its children. The copy creates a new instance of the
element with all its children; this instance is free and can be inserted later
in any place in the same document or in another document.

Some elements are created without any predefined attachment, i.e. as a free
elements; they can be inserted later at the right place. Other elements, whose
definition doesn't make sens out of a specific context, are directly created in
place.

Any element is able to be serialized and exported as an XML, UTF8-encoded string. Symmetrically, an element can be created from an application- provided XML string. As a consequence, lpOD-based applications can remotely transmit or receive any kind of ODF content.

The level 1 API is not validating, so the user is responsible of the ODF
compliance (the API doesn't automatically prevent the applications from
inserting an element at the wrong place).

Any element can be retrieved according to its sequential position in a given
context or its text content (if defined). For example::

    element = context.get_xxx_by_position(p)
    element = context.get_xxx_by_content(regex)

The two lines above retrieve an element among the children of a given 'context'
element. The first one selects the child element at the given ``p`` position.
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

- Paragraphs
   A paragraph element inherits all the basic element features introduced
   above, and owns the following ones.

   - Creation and attachment
       A paragraph can be created with a given style and a given text content.
       The default content is an empty string. There is not default style; a
       paragraph can be created without explicit style, as long as the default
       paragraph style of the document is convenient for the application. The
       style and the text content can be set or changed later.

   - Retrieval
       Like any element, a paragraph can be retrieved in a given context
       according to its sequential position or its text content.

       In addition, it's possible to select the paragraphs that use a given
       style.

       - Text processing
          The traditional string editing methods (i.e. regex-based search &
          replace functions) are available against the text content of a
          paragraph.

       - Multiple spaces and intra-paragraph breaks
          According to the ODF specification, a sequence of multiple spaces is
          regarded as a single space, so multiple spaces must be represented by
          an appropriate ODF element. In the same way, tabulation marks and
          line breaks can't be directly included in the text content, and must
          be replaced by appropriate ODF elements. This API transparently does
          the job: it allows the user to put in a paragraph a text strings
          containing multiple spaces, tab stops ("\t") and/or line breaks
          ("\n").

- Headings
   All the features that apply to paragraphs, as described above, apply to
   headings as well.

   However, a heading is a special paragraph which owns additional properties
   related to its hierarchical level and its numbering. As an consequence, some
   heading-specific methods are provided.

   - Heading level
      A heading owns a special property which indicates its hierarchical level
      in the document. A "level" property can be set at creation time or later
      and changed at any time. A heading without a level attribute is assumed to
      be at level 1, which is the top level. The level may be any positive
      integer value (while the ODF spec doesn't set an explicit limit, we don't
      recommend levels beyond 10).

   - Heading numbering
      Whatever the visibility of the numbers, all the headings of a given level
      are potentially numbered. By default, the numbering is related to the
      whole document starting to 1. However, optional properties allow the user
      to change this behaviour.

      An arbitrary, explicit numbering value can be set, so the automatic
      numbering restarts from this value from the target heading element and
      apply to the following headings at the same level.

      The automatic numbering can be inhibited through an optional property
      which prevents the current heading from being numbered.

      In addition, the API allows the users to provide a heading with an
      arbitrary hidden number. A hidden number is a static, user-provided value
      available for applications that can't dynamically calculate the numbering,
      but safely ignored by applications that support dynamic numbering in text
      documents.

- Text spans
    A text span, in the lpOD scope, is a delimited area included in a paragraph
    or a heading. There are several kinds of text spans.

    - Styling spans
       A text span can be defined in order to apply a special style to a part
       of the content of a paragraph/heading. As a consequence, it's
       associated to a text style.

    - Hyperlinks
       A hyperlink can be defined in order to associate a part of the content
       of a paragraph/heading to the URI of an external resource.

    Unlike paragraphs and headings, spans are created "in place", i.e. their
    creation methods create and directly insert them in the document.

    For styling and hyperlinking spans, the user has to provide the text
    container (i.e. the paragraph or the heading element) and a regular
    expression. The spans can apply repeatedly to every substring in the
    container that match the regex. Optionally, it's possible to set a span of a
    given length at a given position in the element; in this case, the user has
    to provide length and position options instead of a regex string.

    Text spans can be nested without limits. However, a styling or hyperlinking
    span is always entirely included in the area of its starting point
    (paragraph or text span).

Text marks and indices
======================

- Position bookmarks

   A position bookmark is a location mark somewhere in a text container,
   which is identified by a unique name, but without any content.

   A bookmark is created "in place", in a given element at a given position.
   The name and the target element are mandatory arguments. By default, the
   bookmark is put before the first character of the content.

   The position can be explicitly provided by the user. Alternatively, the
   user can provide a regular expression, so the bookmark is set before the
   first substring that matches the expression::

       document.create_bookmark("BM1", paragraph, text="xyz")
       document.create_bookmark("BM2", paragraph, position=4)

   The first instruction above sets a bookmark before the first substring
   matching the given expression (here ``xyz``), which is processed as a regular
   expression. The second instruction sets a bookmark in the same paragraph at a
   given (zero-based), so before the 5th character.

   In order to put a bookmark according to a regex that could be matched more
   than once in the same paragraph, it's possible to combine the position and
   text options, so the search area begins at the given position.

   A bookmark can be retrieved by its unique name. The ODF element then can be
   obtained as the parent of the bookmark element. However, if the bookmark
   is located inside a span, its parent is the span element instead of a
   regular paragraph. So another method is provided, that returns the main
   text container of the bookmark. In the following example, the first line
   returns the parent of a given bookmark (whatever the kind of element),
   while the second one returns the paragraph (or heading) where the bookmark
   is located::

       context.get_bookmark("BM1").parent
       context.get_paragraph_by_bookmark("BM1")

   Another method allows the user to get the offset of a given bookmark in
   the host ODF element. Beware: this offset is related to the text of the
   parent element (which could be a text span).

>>>>>>> Added note related stuff:doc/level1.rst
- Range bookmarks

   A range bookmark is an identified text range which can spread across
   paragraph frontiers. It's a named content area, not dependant of the
   document tree structure. It starts somewhere in a paragraph and stops
   somewhere in the same paragraph or in a following one. Technically,
   it's a pair of special position bookmarks, so called bookmark start
   and bookmark end, owning the same name.

   The API allows the user to create a range bookmark and name it through
   an existing content, as well as to retrieve and extract it according to
   its name.

   Provided methods allow the user to get

       - the pair of elements containing the bookmark start and the
       bookmark end (possibly the same);

       - the text content of the bookmark (without the structure).

   A retrieved range bookmark can be safely removed through a single
   method.

   A range bookmark can be safely processed only if it's entirely
   contained in the calling context. A context that is not the whole
   document can contain a bookmark start or a bookmark end but not both.
   In addition, a bookmark spreading across several elements gets
   corrupt if the element containing its start point or its end point
   is later removed.

- Tables of content TODO
- Indices TODO
- Notes
   Generally speaking, a note is an object whose main function is to allow
   the user to set some text content out of the main document body but
   to structurally associate this content to a specific location in the
   document body. The content of a note is stored in a sequence of one or
   more paragraphs and/or item lists.

   The lpOD API supports three kinds of notes, so-called footnotes, endnotes
   and annotations. Footnotes and endnotes have the same structure and differ
   only by their display location in the document body, while annotations are
   specific objects.
   
   - Footnote and endnote creation
      
      Footnotes and endnotes are created through the same method. The user
      must provide a note identifier, i.e. an arbitrary code name (not
      visible in the document), unique in the scope of the document, and
      a class option, knowing that a note class is either 'footnote' or
      'endnote'.
      
      These notes are created as free elements, so they can be inserted
      later in place (and replicated for reuse in several locations one
      or more documents). As a consequence, creation and insertion are done
      through two distinct functions, i.e. odf_create_note() and
      insert_note(), the second one being a context-related method.
      
      While the identifier and the class are mandatory as soon as a note is
      inserted in a document, these parameter are not required at the
      creation time. They can be provided (or changed) through the
      insert_note() method.
      
      The insert_note() method allows the user to insert the note in the
      same way as a position bookmark (see above). As a consequence, its
      first arguments are the same as those of the create bookmark method.
      However, insert_note() requires additional arguments providing the
      identifier and the citation mark (if not previously set), and the
      citation mark, i.e. the symbol which will be displayed in the document
      body as a reference to the note. Remember that the note citation
      is not an identifier; it's a designed to be displayed according to
      a context-related logic, while the identifier is unique for the
      whole document. 
      
      Regarding the identifier,
      the user can provide either an explicit value, or an function that
      is supposed to return an automatically generated unique value. If
      the class option is missing, the API automatically selects 'footnote'.
      
   - Footnote and endnote content

      A note is a container whose body can be filled with one or more
      paragraphs or item lists at any time, before or after the insertion
      in the document. As a consequence, a note can be used as a regular
      context for paragraph or list appending or retrieval operations.
      
      Note that neither the OpenDocument schema nor the lpOD level 1 API
      prevents the user from including notes into a note body; however
      the lpOD team doesn't recommend such a practice.

   - Annotation creation

      Annotations don't have identifiers and are directly linked to a given
      offset in a given text container.
   
- Change tracking TODO

Structured containers
=====================

- Tables
- Lists

  .. figure:: figures/lpod_list.*
     :align: center



- Data pilot (pivot) tables TODO
- Sections
- Draw pages TODO

  .. figure:: figures/lpod_drawpage.*
     :align: center


Fields and forms
================

- Declared fields and variables
- Text fields

Graphic content
===============

- Frames
- Shapes TODO
- Images
- Animations TODO
- Charts TODO

Styles
======

- Text styles
- Graphic styles TODO
- Page styles TODO

  .. figure:: figures/lpod_page_style.*
     :align: center

- Data formatting styles
- text:outline-style
   see: http://dita.xml.org/wiki/research-document-structure-in-odf

Metadata
========

- Pre-defined
- User defined

Application settings
====================

TODO
