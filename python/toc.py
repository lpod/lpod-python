# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from element import register_element_class, odf_create_element, odf_element
from element import FIRST_CHILD
from utils import Boolean


def odf_create_toc(name=u"Table of content", protected=True, style=None,
                   outline_level=10):
    data = '<text:table-of-content/>'
    element = odf_create_element(data)
    if name:
        element.set_attribute('text:name', name)
    element.set_attribute('text:protected', Boolean.encode(protected))
    if style:
        element.set_attribute('text:style-name', style)
    # A TOC is quite a complex hierarchy
    element.set_toc_outline_level(outline_level)
    return element



class odf_toc(odf_element):

    def get_formated_text(self, context):
        index_body = self.get_element('text:index-body')

        if index_body is None:
            return u''

        result = []
        for element in index_body.get_children():
            if element.get_name() == 'text:index-title':
                for element in element.get_children():
                    result.append(element.get_formated_text(context))
                result.append(u'\n')
            else:
                result.append(element.get_formated_text(context))
        result.append('\n')
        return u''.join(result)


    def get_toc_outline_level(self):
        source = self.get_element('text:table-of-content-source')
        if source is None:
            return None
        return source.get_attribute('text:outline-level')


    def set_toc_outline_level(self, level):
        source = self.get_element('text:table-of-content-source')
        if source is None:
            source = odf_create_element('<text:table-of-content-source/>')
            self.insert_element(source, FIRST_CHILD)
        source.set_attribute('text:outline-level', str(int(level)))



register_element_class('text:table-of-content', odf_toc)
