# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library

# Import from lpod
from utils import _check_arguments
from utils import _check_position_or_name, _get_cell_coordinates
from xmlpart import odf_element, odf_xmlpart, LAST_CHILD


class odf_content(odf_xmlpart):

    def get_text_body(self):
        raise NotImplementedError


    def get_spreadsheet_body(self):
        raise NotImplementedError


    def get_presentation_body(self):
        raise NotImplementedError


    def insert_element(self, element, context, xmlposition=LAST_CHILD,
                       offset=0, length=None):
        # TODO Do not check validity of insertions
        _check_arguments(element=element, context=context,
                         xmlposition=xmlposition, offset=offset)
        qname = element.get_name()
        if qname in ('text:section', 'text:p', 'text:h', 'draw:frame',
                     'table:table', 'text:list'):
            context.insert_element(element, xmlposition)
        elif qname in ('text:note', 'office:annotation', 'text:span'):
            if context.get_name() not in ('text:p', 'text:h'):
                # XXX Image captions, footnote on a footnote...
                raise ValueError, "context must be a paragraph"
            text = context.get_text()
            before, after = text[:offset], text[offset:]
            context.set_text(before)
            element.set_text(after, after=True)
            context.insert_element(element, xmlposition=LAST_CHILD)
        # TODO span, xlink, etc. use offset and length to match the sentence
        # to put into the tag.
        elif qname == 'text:list-item':
            if context.get_name() != 'text:list':
                raise ValueError, "context must be a list"
            context.insert_element(element, xmlposition)
        elif qname == 'draw:image':
            if context.get_name() != 'draw:frame':
                raise ValueError, "context must be a frame"
            context.insert_element(element, xmlposition)
        elif qname == 'style:style':
            # XXX we'll probably have add_style/remove_style/...
            if context.get_name() != 'office:automatic-styles':
                raise ValueError, "context must be the styles container"
            context.insert_element(element, xmlposition)
        # From now on report explicit errors
        elif qname in ('table:table-cell', 'table:table-row',
                       'table:table-column'):
            context.insert_element(element, xmlposition)
            # TODO raise ValueError, "use the odf_table API"
        elif qname.startswith('style:') and qname.endswith('-properties'):
            if context.get_name() != 'style:style':
                raise ValueError, "context must be a style"
            context.insert_element(element, xmlposition)
            # TODO raise ValueError, "use the style API"
        else:
            raise ValueError, 'element "%s" is not (yet) supported' % qname


    #
    # Sections
    #

    def get_section_list(self, style=None, context=None):
        return self._get_element_list('text:section', style=style,
                                      context=context)


    def get_section(self, position, context=None):
        return self._get_element('text:section', position=position,
                                 context=context)


    #
    # Paragraphs
    #

    def get_paragraph_list(self, style=None, context=None):
        return self._get_element_list('text:p', style=style, context=context)


    def get_paragraph(self, position, context=None):
        return self._get_element('text:p', position=position,
                                 context=context)


    #
    # Span
    #

    def get_span_list(self, style=None, context=None):
        return self._get_element_list('text:span', style=style,
                                      context=context)


    def get_span(self, position, context=None):
        return self._get_element('text:span', position=position,
                                 context=context)


    #
    # Headings
    #

    def get_heading_list(self, style=None, level=None, context=None):
        return self._get_element_list('text:h', style=style, level=level,
                                       context=context)


    def get_heading(self, position, level=None, context=None):
        return self._get_element('text:h', position=position, level=level,
                                 context=context)


    #
    # Frames
    #

    def get_frame_list(self, style=None, context=None):
        return self._get_element_list('draw:frame', style=style,
                                      context=context)


    def get_frame(self, name=None, position=None, context=None):
        _check_position_or_name(position, name)
        return self._get_element('draw:frame', frame_name=name,
                                 position=position, context=context)


    #
    # Images
    #

    def get_image_list(self, style=None, context=None):
        return self._get_element_list('draw:image', style=style,
                                      context=context)


    def get_image(self, name=None, position=None, context=None):
        _check_position_or_name(position, name)
        # The frame is holding the name
        frame = self.get_frame(name=name, position=position, context=context)
        return frame.get_element('draw:image')


    #
    # Tables
    #

    def get_table_list(self, style=None, context=None):
        return self._get_element_list('table:table', style=style,
                                      context=context)


    def get_table(self, name=None, position=None, context=None):
        _check_position_or_name(position, name)
        return self._get_element('table:table', table_name=name,
                                 position=position, context=context)


    #
    # Rows
    #

    def get_row_list(self, style=None, context=None):
        return self._get_element_list('table:table-row', style=style,
                                      context=context)


    #
    # Cells
    #

    def get_cell_list(self, style=None, context=None):
        return self._get_element_list('table:table-cell', style=style,
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
    # Notes
    #

    def get_note_list(self, note_class=None, context=None):
        return self._get_element_list('text:note', note_class=note_class,
                                      context=context)


    def get_note(self, text_id, context=None):
        return self._get_element('text:note', text_id=text_id,
                                 context=context)


    def insert_note_body(self, element, context):
        body = context.get_element_list('//text:note-body')[-1]
        body.insert_element(element, LAST_CHILD)


    #
    # Annotations
    #

    def get_annotation_list(self, creator=None, start_date=None,
                            end_date=None, context=None):
        """XXX end date is not included (as expected in Python).
        """
        _check_arguments(creator=creator, start_date=start_date,
                         end_date=end_date)
        annotations = []
        for annotation in self._get_element_list('office:annotation',
                                                 context=context):
            if creator is not None and creator != annotation.get_creator():
                continue
            date = annotation.get_date()
            if start_date is not None and date < start_date:
                continue
            if end_date is not None and date >= end_date:
                continue
            annotations.append(annotation)
        return annotations


    def get_annotation(self, creator=None, start_date=None, end_date=None,
                       context=None):
        annotations = self.get_annotation_list(creator=creator,
                                               start_date=start_date,
                                               end_date=end_date,
                                               context=context)
        if annotations:
            return annotations[0]
        return None


    #
    # Styles
    #

    def get_category_context(self, category):
        if category is None:
            return None
        elif category == 'automatic':
            return self.get_element('//office:automatic-styles')
        raise ValueError, ('category must be None, "named", "automatic" '
                           'or "master"')


    def get_style_list(self, family=None, category=None):
        return self._get_element_list('style:style', family=family)


    def get_style(self, name_or_element, family):
        if isinstance(name_or_element, odf_element):
            if not name_or_element.is_style():
                raise ValueError, "element is not a style element"
            return name_or_element
        elif type(name_or_element) is str:
            context = self.get_category_context('automatic')
            return self._get_element('style:style',
                                     style_name=name_or_element,
                                     family=family, context=context)
        raise TypeError, "style name or element expected"


    # TODO get_parent_style that also searches in styles part if not found
    # in content
