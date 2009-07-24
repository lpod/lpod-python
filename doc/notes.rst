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


Done::

    odf_document document

    document = odf_get_document(uri)
    document = odf_new_document_from_class(odf_class)
    document = odf_new_document_from_template(template_uri)

    content = document.get_xmlpart('content')
      => odf_content

    meta = document.get_xmlpart('meta')
      => odf_meta

    styles = document.get_xmlpart('styles')
      => odf_styles


    odf_element elt = odf_create_paragraph(style)

      => '<text:p text:style-name="$style"></text:p>'

    odf_element elt = odf_create_paragraph(style, text)

      => '<text:p text:style-name="$style">$text</text:p>'

    odf_element elt = odf_create_heading(style, level)

      => '<text:h text:style-name="$style" text:level="$level"></text:h>'

    odf_element elt = odf_create_heading(style, level, text)

      => '<text:h text:style-name="$style" text:level="$level">$text</text:h>'


    odf_content content

    content.get_paragraph_list()
    content.get_paragraph_list(style)
    content.get_paragraph_list(context)
    content.get_paragraph_list(style, context)

      => '//text:p[@text:style-name="$style"]'

    content.get_paragraph(position)
    content.get_paragraph(position, context)

      => assert position >= 1
      => '//text:p[%s]' % position

    content.get_heading_list()
    content.get_heading_list(style)
    content.get_heading_list(level)
    content.get_heading_list(context)
    content.get_heading_list(style, level)
    content.get_heading_list(style, level, context)

      => assert level >= 1
      => '//text:h[@text:style-name="%s"]' % style
      => '//text:h[@text:level="%s"]' % level

    content.get_heading(position)
    content.get_heading(position, level)
    content.get_heading(position, context)
    content.get_heading(position, level, context)

      => assert position >= 1
      => assert level >= 1
      => '//text:h[@text:level="%s"][%s]' % (level, position)


    body = content.get_text_body()
      body => odf_element

    body.insert_paragraph(element)
    body.insert_paragraph(element, context)

    body.insert_heading(element)
    body.insert_heading(element, context)


    odf_styles styles

    styles.get_style(name)


Not yet::

  Styles:

      => only paragraph styles for now (family=paragraph)
      => search algorithm:
        - same part, automatic styles
        - same part, named styles
        - styles part, named styles
        - default style of the same family


Info::

  Hint: preload the body, etc. for fast access to default contexts.

TODO
----

- Move implementation to specific classes:

  - odf_content **DONE**
  - odf_meta **DONE**
  - odf_styles  ?
  - odf_settings ?


Image
-----

Info::

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

Done::

    odf_element <= odf_create_frame(name, style, width, height,
                                    page=None, x=None, y=None)
    if page is None => anchor = paragraph

    document.insert_frame(frame, context)


Not yet::

    odf_element <= odf_create_image(link)

    document.insert_image(element, context)
    (here the context is a frame)
      or
    document.insert_image(element)
    => We create automatically a frame


Frame
-----

Done::

    get_frame_list
    get_frame_by_position
    get_frame_by_name


Table
-----

Info::

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

Done::

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

    cell style: table:style-name="ce1"

    repetition: table:number-columns-repeated="..."

    cell representation: <text:p>...</text:p>

    /!\ expanding cells to easily address and modify them

Not Yet::

    formula: table:formula="of:AVERAGE([.D4:.E5])"

    possibly an annotation


List
----

Info::

    <text:list text:style-name="Standard">
      <text:list-item>
        ...
      </text:list-item>
    </text:list>

Done::

    odt_element <= odt_create_item()
    odt_element <= odf_create_list(style)

    document.insert_list(element, context, xmlposition)
    document.insert_item(element, list, xmlposition)

Sections
--------

Not Yet::

    odf_document.get_section_by_name(name)
    odf_document.get_section_by_name(name, context)

Done::

    odf_document.get_section_by_position(position)
    odf_document.get_section_by_position(position, context)

    odf_document.get_section_external_resource(name)
    odf_document.get_section_external_resource(name, context)


Footnotes and Endnotes
----------------------

Done::

    get_note_list(class, context)
    get_note(id, context)
    The citation is not reliable


Annotations
-----------
Info::

    No name or id
    Search by creator
    Search by date or date range

Done::

    get_annotation_list(author, start_date, end_date...)
    insert_annotation(author, date, offset, text, style)

Meta
----

Done::

  - Regroup keywords in a list ``get_statistique``
  - User-defined metadata (type: boolean, date, float, string and time)

Not Yet::

  - User-defined metadata (type: grandma author nickname)

Common
------

Not Yet::

    odf_document.get_external_uri(name, context)

Styles
-------

Done::

  Basic style framework **DONE**
  Add length along with offset to move text inside a text:span or text:a
  element.

  variables fields and user (constant) fields

     - insert value and find its preceding "set" to adjust its representation
       afterwards
     - modify value (insert a "set" or insert/update a "get/set")

Not Yet::

  More high level API for:

  - style type: font face, default style...
  - style family: font family, text, paragraph, graphics, number...
  - style parent (inheritance)
  - [style class: ... ?]

  named styles, automatic styles

  - style families
  - style objects

  Manifest

  At a higher level, a method to apply a style on patterns of text, e.g.
  highlight the given pattern with a yellow background style.


XPath Requirements
==================

::

    //text:p
    //text:p[4]
    //text:section[4]/text:p[5]
    //text:p[@text:style-name="Note"]
    //draw:frame[@draw:name="image1"]/draw:image
    //text:p[@text:style-name="Note"][4]
