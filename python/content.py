# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library

# Import from lpod
from utils import get_value
from xmlpart import odf_element, odf_xmlpart, FIRST_CHILD


class odf_content(odf_xmlpart):

    def get_body(self):
        return self.get_element('//office:body/*[1]')


    #
    # Sections
    #

    def get_section_list(self, style=None, regex=None, context=None):
        return self._get_element_list('text:section', style=style,
                                      regex=regex, context=context)


    def get_section_by_position(self, position, context=None):
        return self._get_element('text:section', position=position,
                                 context=context)


    #
    # Paragraphs
    #

    def get_paragraph_list(self, style=None, regex=None, context=None):
        return self._get_element_list('text:p', style=style, regex=regex,
                                      context=context)


    def get_paragraph_by_position(self, position, context=None):
        return self._get_element('text:p', position=position,
                                 context=context)


    def get_paragraph_by_content(self, regex, context=None):
        return self._get_element('text:p', regex=regex, context=context)


    #
    # Span
    #

    def get_span_list(self, style=None, context=None):
        return self._get_element_list('text:span', style=style,
                                      context=context)


    def get_span_by_position(self, position, context=None):
        return self._get_element('text:span', position=position,
                                 context=context)


    def get_span_by_content(self, regex, context=None):
        return self._get_element('text:span', regex=regex,
                                 context=context)


    #
    # Headings
    #

    def get_heading_list(self, style=None, level=None, context=None):
        return self._get_element_list('text:h', style=style, level=level,
                                       context=context)


    def get_heading_by_position(self, position, level=None, context=None):
        return self._get_element('text:h', position=position, level=level,
                                 context=context)


    def get_heading_by_content(self, regex, level=None, context=None):
        return self._get_element('text:h', regex=regex, level=level,
                                 context=context)


    #
    # Frames
    #

    def get_frame_list(self, style=None, context=None):
        return self._get_element_list('draw:frame', draw_style=style,
                                      context=context)


    def get_frame_by_name(self, name, context=None):
        return self._get_element('draw:frame', draw_name=name,
                                 context=context)


    def get_frame_by_position(self, position, context=None):
        return self._get_element('draw:frame', position=position,
                                 context=context)


    def get_frame_by_title(self, regex, context=None):
        raise NotImplementedError


    def get_frame_by_description(self, regex,  context=None):
        raise NotImplementedError


    #
    # Images
    #

    def get_image_list(self, style=None, href=None, context=None):
        """Get all image elements matching the criteria. Style is the style
        name. Set link to False to get only internal images, and True to
        get only external images (not in the container). Href is a regex to
        find all images with their path matching.

        Arguments:

            style -- str

            link -- bool

            href -- unicode regex

            context -- odf_element

        Return: list of odf_element
        """
        return self._get_element_list('draw:image', style=style, href=href,
                                      context=context)


    def get_image_by_name(self, name, context=None):
        # The frame is holding the name
        frame = self._get_element('draw:frame', draw_name=name,
                                  context=context)
        if frame is None:
            return None
        return frame.get_element('draw:image')


    def get_image_by_position(self, position, context=None):
        return self._get_element('draw:image', position=position,
                                 context=context)


    def get_image_by_path(self, regex, context=None):
        return self._get_element('draw:image', href=regex, context=context)


    #
    # Tables
    #

    def get_table_list(self, style=None, regex=None, context=None):
        return self._get_element_list('table:table', style=style,
                                      regex=regex, context=context)


    def get_table_by_name(self, name, context=None):
        return self._get_element('table:table', table_name=name,
                                 context=context)


    def get_table_by_position(self, position, context=None):
        return self._get_element('table:table', position=position,
                                 context=context)


    def get_table_by_content(self, regex, context=None):
        return self._get_element('table:table', regex=regex, context=context)


    #
    # Notes
    #

    def get_note_list(self, note_class=None, context=None):
        """Return the list of all note element, or only the ones of the given
        class.

        Arguments:

            note_class -- 'footnote' or 'endnote'

            context -- odf_element

        Return: list of odf_element
        """
        return self._get_element_list('text:note', note_class=note_class,
                                      context=context)


    def get_note_by_id(self, note_id, context=None):
        return self._get_element('text:note', text_id=note_id,
                                 context=context)


    #
    # Annotations
    #

    def get_annotation_list(self, creator=None, start_date=None,
                            end_date=None, context=None):
        """XXX end date is not included (as expected in Python).
        """
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
        """Return the style uniquely identified by the name/family pair. If
        the argument is already a style object, it will return it.

        Arguments:

            name_or_element -- unicode or odf_element

            family -- str

        Return: odf_element or None if not found
        """
        if type(name_or_element) is unicode:
            context = self.get_category_context('automatic')
            return self._get_element('style:style',
                                     style_name=name_or_element,
                                     family=family, context=context)
        elif isinstance(name_or_element, odf_element):
            if not name_or_element.is_style():
                raise ValueError, "element is not a style element"
            return name_or_element
        raise TypeError, "style name or element expected"


    # TODO get_parent_style that also searches in styles part if not found
    # in content


    #
    # Variables
    #

    # XXX This is a good place for this function ???
    def get_variable_decls(self):
        variable_decls = self.get_element('//text:variable-decls')
        if variable_decls is None:
            from document import odf_create_variable_decls

            # Variable only in a "text" document ?
            body = self.get_body()
            body.insert_element(odf_create_variable_decls(), FIRST_CHILD)
            variable_decls = body.get_element('//text:variable-decls')

        return variable_decls


    def get_variable_list(self, context=None):
        return self._get_element_list('text:variable-decl', context=context)


    def get_variable_decl(self, name, context=None):
        return self._get_element('text:variable-decl', text_name=name,
                                 context=context)


    def get_variable_sets(self, name, context=None):
        return self._get_element_list('text:variable-set', text_name=name,
                                      context=context)


    def get_variable_value(self, name, value_type=None, context=None):
        variable_sets = self.get_variable_sets(name, context)

        # Nothing ?
        if not variable_sets:
            return None

        # Get the last value
        return get_value(variable_sets[-1], value_type)


    #
    # User fields
    #

    # XXX This is a good place for this function ???
    def get_user_field_decls(self):
        user_field_decls = self.get_element('//text:user-field-decls')
        if user_field_decls is None:
            from document import odf_create_user_field_decls
            body = self.get_body()
            body.insert_element(odf_create_user_field_decls(), FIRST_CHILD)
            user_field_decls = body.get_element('//text:user-field-decls')

        return user_field_decls


    def get_user_field_list(self, context=None):
        return self._get_element_list('text:user-field-decl', context=context)


    def get_user_field_decl(self, name, context=None):
        return self._get_element('text:user-field-decl', text_name=name,
                                 context=context)


    def get_user_field_value(self, name, value_type=None, context=None):
        user_field_decl = self.get_user_field_decl(name, context)

        # Nothing ?
        if user_field_decl is None:
            return None

        return get_value(user_field_decl, value_type)


    #
    # Draw Pages
    #
    def get_draw_page_list(self, style=None, context=None):
        return self._get_element_list('draw:page', draw_style=style,
                                      context=context)


    def get_draw_page_by_name(self, name, context=None):
        return self._get_element('draw:page', draw_name=name,
                                 context=context)


    def get_draw_page_by_position(self, position, context=None):
        return self._get_element('draw:page', position=position,
                                 context=context)


    #
    # Links
    #

    def get_link_list(self, name=None, title=None, context=None):
        if name or title:
            raise NotImplementedError
        return self._get_element_list('text:a', context=context)


    def get_link_by_name(self, name, context=None):
        # XXX unicity guaranteed?
        return self._get_element('text:a', office_name=name, context=context)


    #
    # Bookmarks
    #

    def get_bookmark_list(self, context=None):
        return self._get_element_list('text:bookmark', context=context)


    def get_bookmark_by_name(self, name, context=None):
        return self._get_element('text:bookmark', text_name=name,
                                 context=context)


    def get_bookmark_start_list(self, context=None):
        return self._get_element_list('text:bookmark-start', context=context)


    def get_bookmark_start_by_name(self, name, context=None):
        return self._get_element('text:bookmark-start', text_name=name,
                                 context=context)


    def get_bookmark_end_list(self, context=None):
        return self._get_element_list('text:bookmark-end', context=context)


    def get_bookmark_end_by_name(self, name, context=None):
        return self._get_element('text:bookmark-end', text_name=name,
                                 context=context)


    #
    # Reference marks
    #

    def get_reference_mark_list(self, context=None):
        return self._get_element_list('text:reference-mark', context=context)


    def get_reference_mark_by_name(self, name, context=None):
        return self._get_element('text:reference-mark', text_name=name,
                                 context=context)


    def get_reference_mark_start_list(self, context=None):
        return self._get_element_list('text:reference-mark-start',
                                      context=context)


    def get_reference_mark_start_by_name(self, name, context=None):
        return self._get_element('text:reference-mark-start', text_name=name,
                                 context=context)


    def get_reference_mark_end_list(self, context=None):
        return self._get_element_list('text:reference-mark-end',
                                      context=context)


    def get_reference_mark_end_by_name(self, name, context=None):
        return self._get_element('text:reference-mark-end', text_name=name,
                                 context=context)
