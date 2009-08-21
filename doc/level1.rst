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
- Draw pages

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

   A style controls the formatting and/or layout properties of a family of
   content objects. It's identified by its own name and its family.
   In the lpOD API, the family has a larger acception than in the OpenDocument
   specification. In the ODF specification, the family is indicated sometimes
   by the value of an explicit 'style:family' attribute, and sometimes by the
   XML tag of the style element itself.
   
   In order to hide the complexity of the ODF data structure, the level 1 API
   allows the user to handle any style as a high level odf_style object.
   
   Any style is created through a common odf_create_style() function with the
   name and the family as its mandatory arguments. Additional arguments can
   be required according to the family. An optional 'parent' argument, whose
   value is the name of another common style of the same family (existing or
   to be created), can be provided, knowing that a style inherits (but can
   override) all the properties of its parent at the display time.
   
   The odf_create_style() function creates a free element, not included in a
   document. This element (or a clone of it) is available to be attached later
   to a document through a generic, document-based insert_style() method.
   
   A style can be inserted as either 'common' (or named and visible for the
   user of a typical office application) or 'automatic', according a boolean
   'common' option, whose default value is true. A common style may have a
   secondary unique name which is its 'display name', which can be set through
   an additional option. With the exception of this optional property, and a
   few other ones, there is no difference between automatic and common styles.
   
   Of course, a style is really in use when one or more content objects
   explicitly reference it through its style property.
   
   The API allows the user to retrieve and select an existing style by name and
   family. The display name, if set, may be used as a replacement of the name
   for retrieval.
   
   Once selected, a style could be removed from the document through a standard
   level 0 element deletion method.

- Text styles

   A text style can be defined either to control the layout of a text container,
   i.e. a paragraph, or to control a text range inside a paragraph. So the API
   allows the user to handle two families of text styles, so called 'text'
   and 'paragraph'. For any style in the text or paragraph families, the 'text'
   class is recommended.
   
   - Text family
   
      A text style (i.e. a style whose family is 'text', whatever its optional
      class) is a style which directly apply to characters (whatever the layout
      of the containing paragraph). So, it can bear any property directly
      related to the font and its representation. The most used properties are
      the font name, the font size, the font style (ex: normal, oblique, etc),
      the text color, the text background color (which may differ from the
      common background color of the paragraph).
      
      A text style can apply to one or more text spans; see the "Text spans"
      section.
      
      The example hereafter creates a text style, so called "My Blue Text",
      using Times New Roman, 14-sized navy blue bold italic characters with
      a yellow background::
      
         s = odf_create_style('MyBlueText',
                              display-name='My Blue Text',
                              family='text',
                              font='Times New Roman',
                              size='14pt',
                              weight='bold',
                              style='italic',
                              color='#000080',
                              background-color='#ffff00'
                              )
      
      The lpOD level 1 API allows the applications to set any property without
      ODF compliance checking. The compliant property set for text styles is
      described in the section 15.4 of the OASIS 1.1 ODF specification. Beware,
      some of them are not supported by any ODF text processor or viewer.
      
      The API allows the user to set any attribute using its official name
      according to the ODF specification (§15.4). For example, the properties
      which control the character name and size are respectively
      "fo:font-name" and "fo:font-size". However, the API allows the use of
      mnemonic shortcuts for a few, frequently required properties, namely:
      
         - font: font name;

         - size: font size (absolute with unit or percentage with '%');

         - weight: font weight, which may be 'normal', 'bold', or one of the
         official nine numeric values from '100' to '900' (§15.4.32);

         - style: to specify whether to use normal or italic font face; the
         legal values are 'normal', 'italic' and 'oblique';

         - color: the color of the characters (i.e. foreground color), provided
         as a RGB hexadecimal string with a leading '#';

         - background-color: the color of the text background, provided in the
         same format as the foreground color;

         - underline: to specify if and how text is underlined; possible values
         are 'solid' (for a continuous line), 'dotted', 'dash', 'long-dash',
         'dot-dash', 'dot-dot-dash', 'wave', and 'none';

         - display: to specify if the text should by displayed or hidden;
         possible values are 'true' (meaning visible) 'none' (meaning hidden)
         or 'condition' (meaning that the text is to be visible or hidden
         according to a condition defined elsewhere).

   - Paragraph family
   
      A paragraph style apply to paragraphs at large, i.e. to ODF paragraphs
      and headings, which are the common text containers. It controls the
      layout of both the text content and the container, so its definition
      is made of two distinct parts, the "text" part and the "paragraph" part.
      
      The text part of a paragraph style definition may have exactly the same
      properties as a regular text style. The rules are defined by the §15.4
      of the OASIS 1.1 ODF specification, and the API provides the same
      property shortcuts as for a text style creation.
      
      The creation of a full-featured paragraph style takes two steps. The
      first one is a regular odf_create_style() instruction, with a mandatory
      unique name and 'paragraph' as the value of the 'family' mandatory
      named parameter, and any number of named paragraph properties. The second
      (optional) step consists of appending a 'text' part to the new paragraph
      style; it can be accomplished, at the user's choice, either by copying
      a previously defined text style, or by explicitly defining new text
      properties, through the text_properties() method, belonging to the style
      class.
      
      The text properties of a paragraph style are default text properties;
      they may be overriden by text styles if one or more styled text spans are
      defined inside the paragraphs.
      
      Assuming that a "MyBlueText" text style has been defined according to
      the text style creation example above, the following sequence creates
      a new paragraph style whose text part is a clone of "MyBlueText", and
      whose paragraph part features are the text justification, a first line
      5mm indent, a black, continuous, half-millimiter border line with a
      bottom-right, one millimeter grey shadow::
   
         ps = odf_create_style('YellowBorderedShadowed',
                                 display-name='Strange Boxed Paragraph',
                                 family='paragraph',
                                 parent='Standard',
                                 align='justify',
                                 indent='5mm',
                                 border='0.5mm solid #000000',
                                 shadow='#808080 1mm 1mm'
                                 )
         ts = document.get_style('MyBlueText', family='text')
         ps.text_properties(ts)
         
      Note that "MyBlueText" is reused by copy, not by reference; so the new
      paragraph style will not be affected if "MyBlueText" is changed or
      deleted later.
      
      The API allows the user to set any attribute using its official name
      according to the ODF specification related to the paragraph formatting
      properties (§15.5). However, the API allows the use of mnemonic shortcuts
      for a few, frequently required properties, namely:
      
         - align: text alignment, whose legal values are 'start', 'end',
         'left', 'right', 'center', or 'justify';

         - align-last: to specify how to align the last line of a justified
         paragraph, legal values are 'start', 'end', 'center';

         - indent: to specify the size of the first line indent, if any;

         - widows: to specify the minimum number of lines allowed at the top
         of a page to avoid paragraph widows;

         - orphans: to specify the minimum number of lines required at the
         bottom of a page to avoid paragraph orphans;

         - together: to control whether the lines of a paragraph should be kept
         together on the same page or column, possible values being 'always'
         or 'auto';

         - margin: to control all the margins of the paragraph;

         - margin-xxx (where xxx is 'left', 'right', 'top' or 'bottom'):
         to control the margins of the paragraph separately;

         - border: a 3-part string to specify the thickness, the line style and
         the line color (according to the XSL/FO grammar);

         - border-xxx (where xxx is 'left', 'right', 'top' or 'bottom'):
         the same as 'border' but to specify a particular border for one side;

         - shadow: a 3-part string to specify the color and the size of the
         shadow;

         - background-color: the hexadecimal color code of the background, with
         a leading '#', or the word 'transparent';

         - padding: the space around the paragraph;

         - padding-xxx (where xxx is 'left', 'right', 'top' or 'bottom'): to
         specify the space around the paragraph side by side;

         - keep-with-next: to specify whether or not to keep the paragraph and
         the next paragraph together on a page or in a column, possible values
         are 'always' or 'auto';

         - page-break-xxx (where xxx is 'before' or 'after'): to specify if
         a page or column break must be inserted before or after any paragraph
         using the style, legal values are 'page', 'column', 'auto'.

- List styles

   A list style is a set of styles that control the formatting properties of
   the list items a every hierachical level. As a consequence, a list style
   is a named container including a particular style definition for each level.
   
   The API allows the user to create a list style (if not previously existing
   in the document), and to create, retrieve and update it for any level.
   
   A new list style, available for later insertion in a document, is created
   through the odf_create_list_style() function. The only one mandatory
   ment is the style name, which should be unique as a list style name in the
   document. An optional display name argument is allowed; if provided, the
   display name should be unique as well. Once created, a list style can be
   inserted in a document through the generic insert_style() method. 
   

- Outline style

   According to the ODF 1.1 specification, "the outline style is a list style
   that is applied to all headings within a text document where the heading's
   paragraph style does not define a list style to use itself". In other words,
   it's a list of default styles for headings according to their respective
   hierarchical levels.
   
   The outline style should define a style for each heading level in use in the
   document.
   
   The API allows the user to initialize the outline style (if not previously
   existing in the document), and to create, retrieve and update it for any
   level.
   
   A get_outline_style() method allows the user to get access to the outline
   style structure. This returned object bears the other outline style related
   methods. If the outline style is not initialized yet, get_outline_style()
   returns a null value. If needed, the outline style can be initialized
   through odf_create_outline_style() followed by insert_style().
   Of course, it's possible to replace the creation method by cloning the
   outline style of another document or a style database. The creation method
   doesn't require any argument and its only purpose is to create an empty
   structure available for later outline level style definitions.
   
   From the outline style object, the user can get or set any outline level
   style, identified by its hierarchical level. As an example, the following
   code retrieves the default style for the level 4 headings::
   
      os = document.get_outline_style()
      l4style = os.get_level_style(4)
   
   The API allows the user to set style attributes for any level, knowing that
   a level is identified by a positive integer starting from 1. With the
   current version of the lpOD level 1 API, a few outline level style
   attributes are supported, namely:
   
      - 'prefix': a string that should be displayed before the heading number;
      - 'suffix': a string that should be displayed before the heading number;
      - 'format': the number display format (ex: '1', 'A');
      - 'display levels': the number of levels whose numbers are displayed at
      the current level;
      - 'start value': the first number of a heading at this level;
      - 'style': the name of the style to use to format the number (that is a
      regular text style).
   
   These attributes (or some of them) can be set or changed through a common
   outline style based method set_level_style(), taking a level number at its
   first argument and one or more attribute/value pairs, as in the following
   example::
   
      os = document.get_outline_style()
      os.set_level_style(1, start=5, prefix='(', suffix=')', format='A')
      
   According to the example above, the default numbering scheme for level 1
   headings will be (A), (B), (C), and so on.
   
   Attributes and properties which are not explicitly supported through
   predefined parameter names in the present version of the API could always
   be set through the element-oriented methods of the level 0 API, knowing
   that get_level_style() returns a regular element.

   [See: http://dita.xml.org/wiki/research-document-structure-in-odf]
   
- Graphic styles TODO

- Data formatting TODO

- Page styles TODO

  .. figure:: figures/lpod_page_style.*
     :align: center

Metadata
========

- Pre-defined
- User defined

Application settings
====================

TODO
