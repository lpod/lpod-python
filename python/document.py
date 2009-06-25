# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from copy import deepcopy
from datetime import datetime

# Import from lpod
from container import odf_get_container, odf_new_container_from_template
from container import odf_new_container_from_class, odf_container
from utils import _check_arguments, _generate_xpath_query
from utils import _check_position_or_name, _get_cell_coordinates
from xmlpart import odf_xmlpart, LAST_CHILD
from xmlpart import odf_create_element


#
# odf creation functions
#

def odf_create_section(style):
    _check_arguments(style=style)
    data = '<text:section text:style-name="%s"></text:section>' % style
    return odf_create_element(data)



def odf_create_paragraph(style, text=u''):
    _check_arguments(style=style, text=text)
    data = '<text:p text:style-name="%s">%s</text:p>'
    text = text.encode('utf_8')
    return odf_create_element(data % (style, text))



def odf_create_heading(style, level, text=u''):
    _check_arguments(style=style, level=level, text=text)
    data = '<text:h text:style-name="%s" text:outline-level="%d">%s</text:h>'
    text = text.encode('utf_8')
    return odf_create_element(data % (style, level, text))



def odf_create_frame(name, style, width, height, page=None, x=None, y=None):
    if page is None:
        anchor = 'text:anchor-type="paragraph"'
    else:
        anchor = 'text:anchor-type="page" text:anchor-page-number="%d"' % page
        if x is not None:
            anchor += ' svg:x="%s"' % x
        if y is not None:
            anchor += ' svg:y="%s"' % y
    data = ('<draw:frame draw:name="%s" draw:style-name="%s" '
            'svg:width="%s" svg:height="%s" %s/>')

    return odf_create_element(data % (name, style, width, height, anchor))


def odf_create_image(link):
    return odf_create_element('<draw:image xlink:href="%s"/>' % link)


def odf_create_cell(cell_type='string', currency=None):
    _check_arguments(cell_type=cell_type, currency=currency)
    data = '<table:table-cell office:value-type="%s"/>'
    cell = odf_create_element(data % cell_type)
    if cell_type == 'currency':
        cell.set_attribute('office:currency', currency)
    return cell


def odf_create_row(width=None):
    row = odf_create_element('<table:table-row/>')
    if width is not None:
        for i in xrange(width):
            cell = odf_create_cell()
            row.insert_element(cell, LAST_CHILD)
    return row


def odf_create_column(style):
    data = '<table:table-column table:style-name="%s"/>'
    return odf_create_element(data % style)


def odf_create_table(name, style, width=None, height=None):
    data = '<table:table table:name="%s" table:style-name="%s"/>'
    table = odf_create_element(data % (name, style))
    if width is not None or height is not None:
        width = width if width is not None else 1
        height = height if height is not None else 1
        for i in xrange(height):
            row = odf_create_row(width)
            table.insert_element(row, LAST_CHILD)
    return table


def odf_create_item():
    return odf_create_element('<text:list-item/>')


def odf_create_list(style):
    return odf_create_element('<text:list text:style-name="%s"/>' % style)


def odf_create_style(name, family='paragraph'):
    """family can be:
         paragraph, text, section, table, tablecolumn, table-row, table-cell,
         table-page, chart, default, drawing-page, graphic, presentation,
         control or ruby.
    """
    _check_arguments(family=family)
    data = '<style:style style:name="%s" style:family="%s"/>'
    return odf_create_element(data % (name, family))


def odf_create_style_text_properties():
    return odf_create_element('<style:text-properties/>')


def odf_create_note(text, note_class='footnote', id=None):
    """note_class = {footnote|endnote}
    """
    _check_arguments(text=text, note_class=note_class)
    data = ('<text:note text:note-class="%s">'
              '<text:note-citation>%s</text:note-citation>'
              '<text:note-body/>'
            '</text:note>')
    text = text.encode('utf_8')
    note = odf_create_element(data % (note_class, text))

    if id is not None:
        note.set_attribute('text:id', id)

    return note


def odf_create_annotation(author, text, date=None):
    # TODO allow paragraph and text styles
    _check_arguments(author=author, text=text, date=date)
    data = ('<office:annotation>'
               '<dc:creator>%s</dc:creator>'
               '<dc:date>%s</dc:date>'
               '<text:p>%s</text:p>'
            '</office:annotation>')
    author = author.encode('utf_8')
    if date is None:
        date = datetime.now()
    date = date.strftime('%Y-%m-%dT%H:%M:%S')
    text = text.encode('utf_8')
    return odf_create_element(data % (author, date, text))


#
# The odf_document object
#

class odf_document(object):

    def __init__(self, container):
        if not isinstance(container, odf_container):
            raise TypeError, "container is not an ODF container"
        self.container = container

        # Cache of XML parts
        self.__xmlparts = {}


    def __get_xmlpart(self, part_name):
        parts = self.__xmlparts
        part = parts.get(part_name)
        if part is None:
            container = self.container
            part = odf_xmlpart(part_name, container)
            parts[part_name] = part
        return part


    def __get_element_list(self, qname, style=None, attributes=None,
                           frame_style=None, context=None, part='content'):
        _check_arguments(style=style, context=context)
        part = self.__get_xmlpart(part)
        if attributes is None:
            attributes = {}
        if style:
            attributes['text:style-name'] = style
        if frame_style:
            attributes['draw:style-name'] = frame_style
        query = _generate_xpath_query(qname, attributes=attributes,
                context=context)
        if context is None:
            return part.get_element_list(query)
        return context.get_element_list(query)


    def __get_element(self, qname, position=None, attributes=None,
                      context=None, part='content'):
        _check_arguments(position=position, context=context)
        part = self.__get_xmlpart(part)
        if attributes is None:
            attributes = {}
        query = _generate_xpath_query(qname, attributes=attributes,
                                      position=position, context=context)
        if context is None:
            result = part.get_element_list(query)
        else:
            result = context.get_element_list(query)
        if not result:
            return None
        return result[0]


    def __insert_element(self, element, context, xmlposition):
        _check_arguments(element=element, context=context,
                         xmlposition=xmlposition)
        if context is not None:
            context.insert_element(element, xmlposition)
        else:
            # We insert it in the last office:text
            content = self.__get_xmlpart('content')
            office_text = content.get_element_list('//office:text')[-1]
            office_text.insert_element(element, LAST_CHILD)


    def clone(self):
        clone = object.__new__(self.__class__)
        for name in self.__dict__:
            if name == 'container':
                setattr(clone, name, self.container.clone())
            elif name == '_odf_document__xmlparts':
                # TODO odf_xmlpart.clone
                setattr(clone, name, {})
            else:
                value = getattr(self, name)
                value = deepcopy(value)
                setattr(clone, name, value)
        return clone


    def save(self, uri=None, packaging=None, pretty=False):
        # Synchronize data with container
        for part_name, part in self.__xmlparts.items():
            if part is not None:
                self.container.set_part(part_name, part.serialize(pretty))

        # Save the container
        self.container.save(uri, packaging)


    #
    # Sections
    #

    def get_section_list(self, style=None, context=None):
        return self.__get_element_list('text:section', style=style,
                                       context=context)


    def get_section(self, position, context=None):
        return self.__get_element('text:section', position, context=context)


    def insert_section(self, element, context=None, xmlposition=LAST_CHILD):
        self.__insert_element(element, context, xmlposition)


    #
    # Paragraphs
    #

    def get_paragraph_list(self, style=None, context=None):
        return self.__get_element_list('text:p', style=style,
                                       context=context)


    def get_paragraph(self, position, context=None):
        return self.__get_element('text:p', position, context=context)


    def insert_paragraph(self, element, context=None,
                         xmlposition=LAST_CHILD):
        self.__insert_element(element, context, xmlposition)


    #
    # Headings
    #

    def get_heading_list(self, style=None, level=None, context=None):
        if level is not None:
            _check_arguments(level=level)
            attributes = {'text:outline-level': level}
        else:
            attributes = None
        return self.__get_element_list('text:h', style=style,
                                       attributes=attributes,
                                       context=context)


    def get_heading(self, position, level=None, context=None):
        if level is not None:
            _check_arguments(level=level)
            attributes = {'text:outline-level': level}
        else:
            attributes = None
        return self.__get_element('text:h', position, attributes=attributes,
                                  context=context)


    def insert_heading(self, element, context=None, xmlposition=LAST_CHILD):
        self.__insert_element(element, context, xmlposition)


    #
    # Frames
    #

    def get_frame_list(self, style=None, context=None):
        return self.__get_element_list('draw:frame', frame_style=style,
                                       context=context)


    def get_frame(self, position=None, name=None, context=None):
        _check_position_or_name(position, name)
        attributes = {'draw:name': name} if name is not None else {}
        return self.__get_element('draw:frame', position,
                                  attributes=attributes,
                                  context=context)


    def insert_frame(self, element, context=None, position=LAST_CHILD):
        self.__insert_element(element, context, position)


    #
    # Images
    #

    def insert_image(self, element, context=None, xmlposition=LAST_CHILD):
        # XXX If context is None
        #     => auto create a frame with the good dimensions
        if context is None:
            raise NotImplementedError

        self.__insert_element(element, context, xmlposition)


    def get_image(self, position=None, name=None, context=None):
        # Automatically get the frame
        frame = self.get_frame(position, name, context)
        return self.__get_element('draw:image', context=frame)


    #
    # Tables
    #

    def get_table_list(self, style=None, context=None):
        return self.__get_element_list('table:table', style=style,
                                       context=context)


    def get_table(self, position=None, name=None, context=None):
        _check_position_or_name(position, name)
        attributes = {'table:name': name} if name is not None else {}
        return self.__get_element('table:table', position,
                                  attributes=attributes, context=context)


    def insert_table(self, element, context=None, xmlposition=LAST_CHILD):
        self.__insert_element(element, context, xmlposition)


    #
    # Columns
    #

    def insert_column(self, element, context, xmlposition=LAST_CHILD):
        context.insert_element(element, xmlposition)


    #
    # Rows
    #

    def insert_row(self, element, context, xmlposition=LAST_CHILD):
        context.insert_element(element, xmlposition)


    def get_row_list(self, style=None, context=None):
        return self.__get_element_list('table:table-row', style=style,
                                       context=context)


    #
    # Cells
    #

    def insert_cell(self, element, context, xmlposition=LAST_CHILD):
        context.insert_element(element, xmlposition)


    def get_cell_list(self, style=None, context=None):
        return self.__get_element_list('table:table-cell', style=style,
                                       context=context)


    # Warning: This function gives just a "read only" odf_element
    def get_cell(self, name, context):
        # The coordinates of your cell
        x, y = _get_cell_coordinates(name)

        # First, we must find the good row
        cell_y = 0
        for row in self.get_row_list(context=context):
            repeat = row.get_attribute('table:number-rows-repeated')
            repeat = int(repeat) if repeat is not None else 1
            if cell_y + 1 <= y and y <= (cell_y + repeat):
                break
            cell_y += repeat
        else:
            raise IndexError, 'I cannot find cell "%s"' % name

        # Second, we must find the good cell
        cell_x = 0
        for cell in self.get_cell_list(context=row):
            repeat = cell.get_attribute('table:number-columns-repeated')
            repeat = int(repeat) if repeat is not None else 1
            if cell_x + 1 <= x and x <= (cell_x + repeat):
                break
            cell_x += repeat
        else:
            raise IndexError, 'i cannot find your cell "%s"' % name

        return cell


    #
    # Lists
    #

    def insert_list(self, element, context=None, xmlposition=LAST_CHILD):
        self.__insert_element(element, context, xmlposition)


    def insert_item(self, element, context, xmlposition=LAST_CHILD):
        context.insert_element(element, xmlposition)


    #
    # Notes
    #

    def get_note_list(self, note_class=None, context=None):
        _check_arguments(note_class=note_class)
        if note_class is not None:
            attributes = {'text:note-class': note_class}
        else:
            attributes = None
        return self.__get_element_list('text:note', attributes=attributes,
                                       context=context)


    def get_note(self, id, context=None):
        attributes = {'text:id': id}
        return self.__get_element('text:note', attributes=attributes,
                                  context=context)


    def insert_note(self, element, context=None, xmlposition=LAST_CHILD):
        self.__insert_element(element, context, xmlposition)


    def insert_note_body(self, element, context):
        body = context.get_element_list('//text:note-body')[-1]
        body.insert_element(element, LAST_CHILD)


    #
    # Annotations
    #

    def get_annotation_list(self, author=None, start_date=None,
                            end_date=None, context=None):
        """XXX end date is not included (as expected in Python).
        """
        _check_arguments(author=author, start_date=start_date,
                         end_date=end_date)
        annotations = []
        for annotation in self.__get_element_list('office:annotation',
                                               context=context):
            dc_creator = annotation.get_element('//dc:creator')
            creator = unicode(dc_creator.get_text(), 'utf_8')
            if author != creator:
                continue
            dc_date = annotation.get_element('//dc:date')
            date = datetime.strptime(dc_date.get_text(), '%Y%m%dT%H:%M:%S')
            if date >= start_date and date < end_date:
                annotations.append(annotation)
        return annotations


    def insert_annotation(self, element, context, offset=0):
        """Offset is the position in the paragraph where the annotation is
        inserted.
        Hence the context is mandatory and the XML position makes no sense.
        """
        _check_arguments(element=element, context=context, offset=offset)
        text = context.get_text()
        before, after = text[:offset], text[offset:]
        context.set_text(before)
        context.append(element)
        element.set_text(after, after=True)


    #
    # Styles
    #

    def get_style_list(self, family='paragraph', context=None):
        _check_arguments(family=family, context=context)
        attributes = {'style:family': family}
        return self.__get_element_list('style:style', attributes=attributes,
                                       context=context, part='styles')


    def get_style(self, name, family='paragraph'):
        _check_arguments(family=family)
        attributes = {'style:name': name,
                      'style:family': family}
        return self.__get_element('style:style', attributes=attributes,
                                  part='styles')


    def insert_style(self, element):
        _check_arguments(element=element)
        styles = self.__get_xmlpart('styles')
        office_styles = styles.get_element_list('//office:styles')[-1]
        office_styles.insert_element(element, LAST_CHILD)


    def insert_style_properties(self, element, context):
        _check_arguments(element=element, context=context)
        context.insert_element(element, LAST_CHILD)



#
# odf_document factories
#

def odf_get_document(uri):
    """Return an "odf_document" instance of the ODF document stored at the
    given URI.
    """
    container = odf_get_container(uri)
    return odf_document(container)



def odf_new_document_from_template(template_uri):
    """Return an "odf_document" instance using the given template.
    """
    container = odf_new_container_from_template(template_uri)
    return odf_document(container)



def odf_new_document_from_class(odf_class):
    """Return an "odf_document" instance of the given class.
    """
    container = odf_new_container_from_class(odf_class)
    return odf_document(container)
