# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2013 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          Romain Gauthier <romain@itaapy.com>
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

# Import from the Standard Library
import re

# Import from lpod
from element import odf_text
from element import odf_element, odf_create_element


_rsplitter = re.compile(u'(\n|\t|  +)', re.UNICODE)
_rspace = re.compile(u'^  +$', re.UNICODE)



def _guess_decode(text):
    """Try to decode text using common encoding
    """
    done = False
    for encoding in ('utf-8', 'iso8859-1', 'ascii'):
        try:
            decoded = text.decode(encoding)
            done = True
            break
        except UnicodeDecodeError:
            continue
    if done:
        return decoded
    else:
        raise UnicodeDecodeError



def _get_formatted_text(element, context, with_text=True):
    document = context.get('document', None)
    rst_mode = context.get('rst_mode', False)

    result = []
    if with_text:
        objects = element.xpath('*|text()')
    else:
        objects = element.get_children()
    for obj in objects:
        if type(obj) is odf_text:
            result.append(obj)
        else:
            tag = obj.get_tag()
            # Good tags with text
            if tag in ('text:a', 'text:p'):
                result.append(_get_formatted_text(obj, context,
                                                 with_text=True))
            # Try to convert some styles in rst_mode
            elif tag == 'text:span':
                text = _get_formatted_text(obj, context, with_text=True)
                if not rst_mode:
                    result.append(text)
                    continue
                if not text.strip():
                    result.append(text)
                    continue
                style = obj.get_style()
                if style is None:
                    result.append(text)
                    continue
                if document:
                    style = document.get_style("text", style)
                    properties = style.get_properties()
                else:
                    properties = None
                if properties is None:
                    result.append(text)
                    continue
                # Compute before, text and after
                before = ''
                for c in text:
                    if c.isspace():
                        before += c
                    else:
                        break
                after = ''
                for c in reversed(text):
                    if c.isspace():
                        after = c + after
                    else:
                        break
                text = text.strip()
                # Bold ?
                if properties.get('fo:font-weight') == 'bold':
                    result.append(before)
                    result.append('**')
                    result.append(text)
                    result.append('**')
                    result.append(after)
                    continue
                # Italic ?
                if properties.get('fo:font-style') == 'italic':
                    result.append(before)
                    result.append('*')
                    result.append(text)
                    result.append('*')
                    result.append(after)
                    continue
                # Unknown style, ...
                result.append(before)
                result.append(text)
                result.append(after)
            # Footnote or endnote
            elif tag == 'text:note':
                note_class = obj.get_class()
                container = {'footnote': context['footnotes'],
                             'endnote': context['endnotes']}[note_class]
                citation = obj.get_citation()
                if not citation:
                    # Would only happen with hand-made documents
                    citation = len(container)
                body = obj.get_body()
                container.append((citation, body))
                if rst_mode:
                    marker = {'footnote': u" [#]_ ",
                              'endnote': u" [*]_ "}[note_class]
                else:
                    marker = {'footnote': u"[{citation}]",
                              'endnote': u"({citation})"}[note_class]
                result.append(marker.format(citation=citation))
            # Annotations
            elif tag == 'office:annotation':
                context['annotations'].append(obj.get_body())
                if rst_mode:
                    result.append(' [#]_ ')
                else:
                    result.append('[*]')
            # Tabulation
            elif tag == 'text:tab':
                result.append(u'\t')
            # Line break
            elif tag == 'text:line-break':
                if rst_mode:
                    result.append(u"\n|")
                else:
                    result.append(u"\n")
            else:
                result.append(obj.get_formatted_text(context))
    return u''.join(result)



def odf_create_spaces(number=1):
    """This element shall be used to represent the second and all following “ “
    (U+0020, SPACE) characters in a sequence of “ “ (U+0020, SPACE) characters.
    Note: It is not an error if the character preceding the element is not a
    white space character, but it is good practice to use this element only for
    the second and all following SPACE characters in a sequence.

    Arguments:

        number -- int

    Return odf_element
    """
    element = odf_create_element('text:s')
    element.set_attribute('text:c', str(number))
    return element



def odf_create_tabulation(position=None):
    """This element represents the [UNICODE] tab character (HORIZONTAL
    TABULATION, U+0009).

    The position attribute contains the number of the tab-stop to which
    a tab character refers. The position 0 marks the start margin of a
    paragraph. Note: The position attribute is only a hint to help non-layout
    oriented consumers to determine the tab/tab-stop association. Layout
    oriented consumers should determine the tab positions based on the style
    information

    Arguments:

        number -- int

    Return odf_element
    """
    element = odf_create_element('text:tab')
    if position is not None:
        if position >= 0:
            element.set_attribute('text:tab-ref', str(position))
    return element



def odf_create_line_break():
    """This element represents a line break.

    Return odf_element
    """
    return odf_create_element('text:line-break')



class paragraph_base(odf_element):
    """Base class for paragraph like classes.
    """
    def get_style(self):
        return self.get_attribute('text:style-name')


    def set_style(self, name):
        return self.set_style_attribute('text:style-name', name)


    def get_text_style(self):
        return self.get_attribute('text:style-name')


    def set_text_style(self, name):
        return self.set_style_attribute('text:style-name', name)


    def get_formatted_text(self, context=None, simple=False):
        if not context:
            context = { 'document': None,
                        'footnotes': [],
                        'endnotes': [],
                        'annotations': [],
                        'rst_mode': False,
                        'img_counter': 0,
                        'images': [],
                        'no_img_level': 0}
        content = _get_formatted_text(self, context, with_text=True)
        if simple:
            return content
        else:
            return content + '\n\n'


    def append_plain_text(self, text=u'', encoding=None):
        """Append unicode plain text to the paragraph, replacing <CR>, <TAB>
           and multiple spaces by ODF corresponding tags.
        """
        if not isinstance(text, unicode):
            if encoding:
                text = text.decode(encoding)
            else:
                text = _guess_decode(text)
        blocs = _rsplitter.split(text)
        for b in blocs:
            if not b:
                continue
            if b == u'\n':
                self.append(odf_create_line_break())
                continue
            if b == u'\t':
                self.append(odf_create_tabulation())
                continue
            if _rspace.match(b):
                # follow ODF standard : n spaces => one space + spacer(n-1)
                self.append(u' ')
                self.append(odf_create_spaces(len(b) - 1))
                continue
            # standard piece of text:
            self.append(b)
