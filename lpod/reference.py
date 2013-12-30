# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2013 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Hervé Cauwelier <herve@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>
#
# This file is part of Lpod (see: http://lpod-project.net).
# Lpod is free software; you can redistribute it and/or modify it under
# the terms of either:
#
# a) the GNU General Public License as published by the Free Software
#    Foundation, either version 3 of the License, or (at your option)
#    any later version.
#    Lpod is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#    along with Lpod.  If not, see <http://www.gnu.org/licenses/>.
#
# b) the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
#

# Import from lpod
from element import odf_element, odf_create_element, register_element_class


def _get_referenced(body, start, end, no_header, clean, as_xml, as_list):
        if body is None or start is None or end is None:
            return None
        content_list = body.get_between(start, end, as_text=False,
                                no_header=no_header, clean=clean)
        if as_list:
            return content_list
        referenced = odf_create_element('office:text')
        for chunk in content_list:
            referenced.append(chunk)
        if as_xml:
            return referenced.serialize()
        else:
            return referenced



class odf_reference_mark(odf_element):
    """A point reference.
    A point reference marks a position in text and is represented by a single
    <text:reference-mark> element.
    """

    def get_name(self):
        return self.get_attribute('text:name')


    def set_name(self, name):
        """Set the text:name attribute.

        Arguments:

            name -- unicode
        """
        return self.set_attribute('text:name', name)


    def get_referenced_text(self):
        "Only usefull for for subclasses."
        return u''



class odf_reference_mark_end(odf_reference_mark):
    """The <text:reference-mark-end> element represents the end of a range
    reference.
    """

    def get_referenced_text(self):
        """Return the text between reference-mark-start and reference-mark-end.
        """
        name = self.get_name()
        args = {'name': name}
        request = (u"//text()"
            u"[preceding::text:reference-mark-start[@text:name='%(name)s'] "
            u"and following::text:reference-mark-end[@text:name='%(name)s']]"
            ) % args
        result = ' '.join(self.xpath(request))
        return result



class odf_reference_mark_start(odf_reference_mark_end):
    """The <text:reference-mark-start> element represents the start of a
    range reference.
    """

    def delete(self, child=None, keep_tail=True):
        """Delete the given element from the XML tree. If no element is given,
        "self" is deleted. The XML library may allow to continue to use an
        element now "orphan" as long as you have a reference to it.

        For odf_reference_mark_start : delete the reference-end tag if exists.

        Arguments:

            child -- odf_element

            keep_tail -- boolean (default to True), True for most usages.
        """
        if child is not None:  # act like normal delete
            return super(odf_reference_mark_start, self).delete(child,
                                                                keep_tail)
        name = self.get_name()
        parent = self.get_parent()
        if parent is None:
            raise ValueError, "cannot delete the root element"
        body = self.get_document_body()
        if not body:
            body = parent
        end = body.get_reference_mark_end(name=name)
        if end:
            end.delete()
        # act like normal delete
        return super(odf_reference_mark_start, self).delete()


    def get_referenced(self, no_header=False, clean=True, as_xml=False,
                       as_list=False):
        """Return the document content between the start and end tags of the
        reference. The content returned by this method can spread over several
        headers and paragraphs.
        By default, the content is returned as an <office:text> odf element.


        Arguments:

            no_header -- boolean (default to False), translate existing headers
                         tags <text:h> into paragraphs <text:p>.

            clean -- boolean (default to True), suppress unwanted tags. Striped
                     tags are : 'text:change', 'text:change-start',
                     'text:change-end', 'text:reference-mark',
                     'text:reference-mark-start', 'text:reference-mark-end'.

            as_xml -- boolean (default to False), format the returned content as
                      a XML string (serialization).

            as_list -- boolean (default to False), do not embed the returned
                       content in a <office:text'> element, instead simply
                       return a raw list of odf elements.
        """
        name = self.get_name()
        parent = self.get_parent()
        if parent is None:
            raise ValueError, "need some upper document part"
        body = self.get_document_body()
        if not body:
            body = parent
        end = body.get_reference_mark_end(name=name)
        start = self
        return _get_referenced(body, start, end, no_header, clean, as_xml,
                               as_list)



class odf_reference(odf_element):
    """A reference to a content marked by a reference mark.
    The odf_reference element (<text:reference-ref>) represents a field that
    references a <text:reference-mark-start> or <text:reference-mark> element.
    Its text:reference-format attribute specifies what is displayed from the
    referenced element. Default is 'page'
    Actual content is not updated except for the 'text'
    format by the update() method.


    Consider using: lpod.paragraph.insert_reference()

    Values for text:reference-format :
        The defined values for the text:reference-format attribute supported by
        all reference fields are:
        'chapter': displays the number of the chapter in which the referenced
        item appears.
        'direction': displays whether the referenced item is above or below the
        reference field.
        'page': displays the number of the page on which the referenced item
        appears.
        'text': displays the text of the referenced item.
        Additional defined values for the text:reference-format attribute
        supported by references to sequence fields are:
        'caption': displays the caption in which the sequence is used.
        'category-and-value': displays the name and value of the sequence.
        'value': displays the value of the sequence.

        References to bookmarks and other references support additional values,
        which display the list label of the referenced item. If the referenced
        item is contained in a list or a numbered paragraph, the list label is
        the formatted number of the paragraph which contains the referenced
        item. If the referenced item is not contained in a list or numbered
        paragraph, the list label is empty, and the referenced field therefore
        displays nothing. If the referenced bookmark or reference contains more
        than one paragraph, the list label of the paragraph at which the
        bookmark or reference starts is taken.

        Additional defined values for the text:reference-format attribute
        supported by all references to bookmark's or other reference fields are:

        'number': displays the list label of the referenced item. [...]
        'number-all-superior': displays the list label of the referenced item
        and adds the contents of all list labels of superior levels in front of
        it. [...]
        'number-no-superior': displays the contents of the list label of the
        referenced item.

    """

    format_allowed = ('chapter', 'direction', 'page', 'text', 'caption',
        'category-and-value', 'value', 'number', 'number-all-superior',
        'number-no-superior')


    def get_name(self):
        return self.get_attribute('text:ref-name')


    def set_name(self, name):
        """Set the text:ref-name attribute.

        Arguments:

            name -- unicode
        """
        return self.set_attribute('text:ref-name', name)


    def get_format(self):
        return self.get_attribute('text:reference-format')


    def set_format(self, ref_format=''):
        """Set the text:reference-format attribute.

        Arguments:

            ref_format -- unicode
        """
        if not ref_format or ref_format not in self.format_allowed:
            ref_format = 'page'
        self.set_attribute('text:reference-format', ref_format)


    def update(self):
        """Update the content of the reference text field. Currently only
        'text' format is implemented. Other values, for example the 'page' text
        field, may need to be refreshed through a visual ODF parser.
        """
        ref_format = self.get_format()
        if ref_format != 'text':
            return
        body = self.get_document_body()
        if not body:
            body = self.get_root()
        name = self.get_name()
        reference = body.get_reference_mark(name=name)
        if not reference:
            return
        content = reference.get_referenced_text()
        self.set_text(content)



def odf_create_reference(name, ref_format=''):
    """Create a reference to a content marked by a reference mark. An actual
    reference mark with the provided name should exist.
    Consider using: lpod.paragraph.insert_reference()

    The text:ref-name attribute identifies a <text:reference-mark> or
    <text:referencemark-start> element by the value of that element's text:name
    attribute.
    If ref_format is 'text', the current text content of the reference_mark is
    retrieved.
    insert_reference
    Arguments:

        name -- unicode : name of the reference mark

        ref_format -- unicode : format of the field. Default is 'page', allowed
                        values are 'chapter', 'direction', 'page', 'text',
                        'caption', 'category-and-value', 'value', 'number',
                        'number-all-superior', 'number-no-superior'.
    """
    element = odf_create_element('text:reference-ref')
    element.set_name(name)
    element.set_format(ref_format)
    return element



def strip_references(element):
    """Remove all the 'text:reference-ref' tags of the element, keeping inner
    sub elements (for example the referenced valus if format is 'text').
    Nota : using the .delete() on the reference mark will delete inner content.
    """
    strip = ('text:reference-ref',)
    return element.strip_tags(strip)



def odf_create_reference_mark(name):
    """A point reference. A point reference marks a position in text and is
    represented by a single <text:reference-mark> element.
    Consider using the wrapper: lpod.paragraph.set_reference_mark()

    Arguments:

        name -- unicode
    """
    element = odf_create_element('text:reference-mark')
    element.set_name(name)
    return element



def odf_create_reference_mark_start(name):
    """The <text:reference-mark-start> element represent the start of a range
    reference.
    Consider using the wrapper: lpod.paragraph.set_reference_mark()

    Arguments:

        name -- unicode
    """
    element = odf_create_element('text:reference-mark-start')
    element.set_name(name)
    return element



def odf_create_reference_mark_end(name):
    """The <text:reference-mark-end> element represent the end of a range
    reference.
    Consider using the wrappers: lpod.paragraph.set_reference_mark() and
    lpod.paragraph.set_reference_mark_end()

    Arguments:

        name -- unicode
    """
    element = odf_create_element('text:reference-mark-end')
    element.set_name(name)
    return element



def remove_all_reference_marks(element):
    """Remove all the 'text:reference-mark', 'text:reference-mark-start', and
    'text:reference-mark-end' tags of the element, keeping inner sub elements.
    Nota : using the .delete() on the reference mark will delete inner content.
    """
    strip = ('text:reference-mark', 'text:reference-mark-start',
             'text:reference-mark-end')
    return element.strip_tags(strip)



def remove_reference_mark(element, position=0, name=None):
    """Remove the 'text:reference-mark', 'text:reference-mark-start', and
    'text:reference-mark-end' tags of the element, identified by name or
    position, keeping inner sub elements.
    Nota : using the .delete() on the reference mark will delete inner content.
    """
    start = element.get_reference_mark(position=position, name=name)
    end = element.get_reference_mark_end(position=position, name=name)
    target = []
    if start:
        target.append(start)
    if end:
        target.append(end)
    element.strip_elements(target)




register_element_class('text:reference-mark', odf_reference_mark)
register_element_class('text:reference-mark-start', odf_reference_mark_start)
register_element_class('text:reference-mark-end', odf_reference_mark_end)
register_element_class('text:reference-ref', odf_reference)
