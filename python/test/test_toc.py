# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document
from lpod.toc import odf_create_toc



class TOCTest(TestCase):

    def test_toc_autofill(self):
        document = odf_get_document("samples/toc.odt")

        toc = odf_create_toc(u"Table des matières")
        toc.auto_fill(document)
        toc_lines = [ paragraph.get_text()
                      for paragraph in toc.get_paragraph_list() ]

        expected = [u"Table des matières",
                    u"1. Level 1 title 1",
                    u"1.1. Level 2 title 1",
                    u"2. Level 1 title 2",
                    u"2.1.1. Level 3 title 1",
                    u"2.2. Level 2 title 2",
                    u"3. Level 1 title 3",
                    u"3.1. Level 2 title 1",
                    u"3.1.1. Level 3 title 1",
                    u"3.1.2. Level 3 title 2",
                    u"3.2. Level 2 title 2",
                    u"3.2.1. Level 3 title 1",
                    u"3.2.2. Level 3 title 2"]

        self.assertEqual(toc_lines, expected)



if __name__ == '__main__':
    main()

