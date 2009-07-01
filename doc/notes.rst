Notes
#####


Level 0
=======

Level 0.0
---------
::

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


TODO
----

    - Move implementation to specific classes: odf_content, odf_meta,
      odf_styles, odf_settings
    - Define API in odf_document, but then call the implementation in the
      part instance.


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



    get_image_list
    get_image_by_position
    get_image_by_name



Frame
-----
::

    get_frame_list
    get_frame_by_position
    get_frame_by_name



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

        In a cell, we cannot have a cell or a line. But we can have
        paragraphs, sections, ...


    odt_element <= odf_create_cell()
    odt_element <= odf_create_row(width=None)
    odt_element <= odf_create_column()

    odt_element <= odf_create_table(name, style, width=None, height=None)

    document.insert_table(element, context=None, xmlposition=None)

    document.insert_row(table, context, xmlposition)
    document.insert_column(table, context, xmlposition)
    document.insert_cell(row, context, xmlposition)

    Getting a cell from its table, its line, its column

    cell type: office:value-type="{boolean, currency, date, float,
                                   percentage, string, time}"

    boolean: office:boolean-value="{true,false}"

    currency: office:currency="EUR"

    date: office:date-value="2009-06-22"

    datetime: office:date-value="2009-06-22T12:43:17"

    float: office:value="3.14"

    percentage: office:value="0.5"

    string: office:string-value="toto"

    time: office:time-value="PT12H33M00S"

    formula: table:formula="of:AVERAGE([.D4:.E5])"

    cell style: table:style-name="ce1"

    repetition: table:number-columns-repeated="..."

    cell representation: <text:p>...</text:p>

    possibly an annotation

    /!\ expanding cells to easily address and modify them


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

    document.insert_list(element, context, xmlposition)
    document.insert_item(element, list, xmlposition)



Sections
--------
::

    odf_document.get_section_by_position(position)
    odf_document.get_section_by_position(position, context)

    odf_document.get_section_by_name(name)
    odf_document.get_section_by_name(name, context)

    odf_document.get_section_external_resource(name)
    odf_document.get_section_external_resource(name, context)


Footnotes and Endnotes
----------------------
::

    get_note_list(class, context)

    get_note(id, context)

    The citation is not reliable


Annotations
-----------
::

    No name or id
    Search by creator
    Search by date or date range


    get_annotation_list(author, start_date, end_date...)


    insert_annotation(author, date, offset, text, style)


Meta
----

    - Easy
    - Regroup keywords in a list
    - User-defined metadata (type: boolean, date, float, string and time)


Common
------
::

    odf_document.get_external_uri(name, context)


TODO
====

named styles, automatic styles
style families
style objects

manifest?


Make this use case:
  - Read a directory
    for each file =>
        if image => insert it
        if csv => make a table

Abstract gio (instead of itools)

element attributes API

XPath Requirements
==================

::

    //text:p
    //text:p[4]
    //text:section[4]/text:p[5]
    //text:p[@text:style-name="Note"]
    //draw:frame[@draw:name="image1"]/draw:image
    //text:p[@text:style-name="Note"][4]
