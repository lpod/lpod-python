# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from xmlpart import register_element_class, odf_element


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



register_element_class('text:table-of-content', odf_toc)
