#####################
Level 0 API reference
#####################

0.0 Physical access & persistence
=================================

odf_container
-------------
	
The odf_container represents the physical Open Document package, whatever
the storage option. The package consists of either a zip compressed archive
including XML and non-XML parts, of a flat, uncompressed XML file.

An odf_container instance can be created by several ways:

1) from scratch by the lpOD API;

2) from a previously stored ODF template package;

3) from an existing ODF package.


Constructors
~~~~~~~~~~~~~

odf_get_container(uri)
	Instantiates an odf_container object which is an read-write interface to
	an existing ODF package corresponding to the given URI. The package may
	be an ODF-compliant zip or an ODF-compliant flat XML file.

odf_new_container({document_class})
	Returns a new odf_container corresponding to the given ODF document class
	(i.e. presently text, spreadsheet, presentation, or drawing).
	
odf_new_container_from_template(uri)
	Returns a new odf_container instantiated from an existing ODF template
	package. Same as odf_get_container(), but the template package is read-only.

Methods

clone()
	Returns a new odf_container that is a copy of the current instance.

del_part(part_name)
	Deletes a part in the container. The target part is selected
	according to the same rules as with get_part().
	
	This part deletion apply to the odf_container object but not
	immediately to the physical underlying package. It's made
	persistent by the next save() call, like any other change
	regarding an odf_package.
	
	Returns true if success, null otherwise.

get_part(part_name)
	Extracts and returns a part, i.e. either a member file of the package,
	if the physical container is a regular ODF zip archive, or a subset of
	the XML content, if the package is a flat XML file. The extracted part
	is returned as raw data; it's not parsed or interpreted in any way.
	
	The part to be extracted depends on the given part_name and is selected
	according to the following rules:
	
	If part_name is "content", "styles", "meta" or "settings", then the
	selected part is the "part_name.xml" member file in case of zip archive
	or the "office:document-part_name" in case of flat XML file.
	
	For any other part, the given part_name must be either the explicit
	path/name of the needed resource in the zip package, or the full name
	of the needed element in the XML flat file. With flat XML packages,
	it's assumed that the root element is always <office:document> and
	the selected part_name is always a direct child of the root element.
	
	The return value is null if the given part_name doesn't match an
	existing part.

set_part(part_name, data)
	Creates or replace a part in the current odf_container using external
	raw data.
	
	The target part_name is selected according to the same rules as with
	get_part().
	
	As with del_part(), the change apply to the odf_container object in
	memory but it doesn't affect the corresponding persistent package
	before the next call of the save() method.
	
	The provided data is used "as is", without any package consistency
	check. If the current odf_container is a flat XML package, the user
	is responsible of the XML well-formedness and ODF compliance of this
	material.


    odf_container container

    container = odf_new_container_from_class({text, spreadsheet, presentation,
                                              drawing})
    container = odf_new_container_from_template(template_uri)

    container = odf_get_container(uri)

    odf_container copy = container.clone()
    str data = container.get_part(part_name)
    container.set_part(part_name, data)
    container.del_part(part_name)


TODO
^^^^

::

    container.save()
    container.save(packaging)
    container.save(uri)
    container.save(uri, packaging)

with ``packaging = {flat, zip}``


Level 0.1
---------
::

    odf_xmlpart part

    part = odf_xmlpart(part_name, container)

    part.events
    part.container
    part.serialize()

    list l_elt = part.get_element_list("//xpath...")

    odf_element elt = l_elt[0]

    elt.get_element_list("//xpath...")

    value = elt.get_attribute(name)
    elt.set_attribute(name, value)

    unicode text = elt.get_text()
    elt.set_text(text)

    odf_element e2 = odf_create_element('<element[...]')
    elt.insert_element(e2, {previous_sibling, next_sibling, first_child,
                            last_child, <N>})
    e3 = elt.copy()

    elt.delete()


Level 1
=======
::

    odf_document document

    document = odf_get_document(uri)
    document = odf_new_document_from_class(odf_class)
    document = odf_new_document_from_template(template_uri)

    document.get_paragraph_list()
    document.get_paragraph_list(style)
    document.get_paragraph_list(context)
    document.get_paragraph_list(style, context)

      => '//text:p[@text:style-name="$style"]'

    document.get_heading_list()
    document.get_heading_list(style)
    document.get_heading_list(level)
    document.get_heading_list(context)
    document.get_heading_list(style, level)
    document.get_heading_list(style, level, context)

      => assert level >= 1
      => '//text:h[@text:style-name="%s"]' % style
      => '//text:h[@text:level="%s"]' % level

    document.get_paragraph(position)
    document.get_paragraph(position, context)

      => assert position >= 1
      => '//text:p[%s]' % position

    document.get_heading(position)
    document.get_heading(position, level)
    document.get_heading(position, context)
    document.get_heading(position, level, context)

      => assert position >= 1
      => assert level >= 1
      => '//text:h[@text:level="%s"][%s]' % (level, position)

    document.get_style(name)

      => only paragraph styles for now (family=paragraph)
      => search algorithm:
        - same part, automatic styles
        - same part, named styles
        - styles part, named styles
        - default style of the same family

    odf_element elt = odf_create_paragraph(style)

      => '<text:p text:style-name="$style"></text:p>'

    odf_element elt = odf_create_paragraph(style, text)

      => '<text:p text:style-name="$style">$text</text:p>'

    odf_element elt = odf_create_heading(style, level)

      => '<text:h text:style-name="$style" text:level="$level"></text:h>'

    odf_element elt = odf_create_heading(style, level, text)

      => '<text:h text:style-name="$style" text:level="$level">$text</text:h>'

    document.insert_paragraph(element)
    document.insert_paragraph(element, context)

    document.insert_heading(element)
    document.insert_heading(element, context)

Hint: preload the body, etc. for fast access to default contexts.



Styles
-------

- style type: font face, default style...
- style family: font family, text, paragraph, graphics, number...
- style parent (inheritance)
- [style class: ... ?]


Image
-----

::

    odf_element <= odf_create_frame(name, style, width, height,
                                    page=None, x=None, y=None)
    if page is None => anchor = paragraph

    document.insert_frame(frame)
    document.insert_frame(frame, context)

    odf_element <= odf_create_image(link)

    document.insert_image(element, context)
    (here the context is a frame)
      or
    document.insert_image(element)
    => We create automatically a frame


    name must be unique
    => "draw:frame"

    <draw:frame draw:name="Logo" draw:style-name="Centered Image"
                draw:z-index="1" svg:height="53mm" svg:width="91mm"
                text:anchor-page-number="1" text:anchor-type="page">
        <draw:image xlink:href="Pictures/image.png"/>
    </draw:frame>

    text:anchor-type = {page|paragraph}
      if page => text:anchor-page-number="..."
                 svg:x="..." \
                               give the position
                 svg:y="..." /

      if paragraph => nothing



Table
-----

::

  No column in odf, just lines
  The columns are only used to define the style for a group of cells

      <table:table table:name="..." table:style-name="...">
        <table:table-column table:style-name="..."/>
        <table:table-column table:style-name="..."/>

        <table:table-row>

          <table:table-cell office:value-type="String">

          </table:table-cell>


        </table:table-row>

      </table:table>

      In a cell, we cannot have a cell or a line. But we can have paragraphs,
      sections, ...


  odt_element <= odf_create_cell()
  odt_element <= odf_create_row(width=None)
  odt_element <= odf_create_column()

  odt_element <= odf_create_table(name, style, width=None, height=None)

  document.insert_table(element, context=None, position=None)

  document.insert_row(table, context, position)
  document.insert_column(table, context, position)
  document.insert_cell(row, context, position)


List
----
::

  odt_element <= odt_create_item()
  odt_element <= odf_create_list(style)

  <text:list text:style-name="Standard">
    <text:list-item>
      ...
    </text:list-item>
  </text:list>

  document.insert_list(element, context, position)
  document.insert_item(element, list, position)





TODO
====

named styles, automatic styles
style families:

manifest?

Make this use case:
  - Read a directory
    for each file =>
        if image => insert it
        if csv => make a table


Element manipulation:

    - Insert a sub-element at a given position: note, annotation, field...
    - Replace some text of the element by a sub-element: hyperlink, automatic
      style...
    - Searching text without couting text:span, text:a, etc. (like a raw
      search on element.get_content())
    - Returning the lowest odf_element containing the whole text (if the text
      is across several span/a, return the p) in the document or the given
      context, and the offset where the text begins in the content.
    - Returning the nearest odf_element containing the whole text or the start
      of the text (if across several span/a) in the odf_element and its
      sub-elements (the "p" element in the above case), and the offset where
      the text begins in the content.
    - Insert a new element at this position, and it may include removing all
      or part of the text and replacing it in the new element


XPath Requirements
==================

::

    //text:p
    //text:p[4]
    //text:section[4]/text:p[5]
    //text:p[@text:style-name="Note"]
    //draw:frame[@draw:name="image1"]/draw:image
    //text:p[@text:style-name="Note"][4]
