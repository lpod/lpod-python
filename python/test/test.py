# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestLoader, TestSuite, TextTestRunner

# Import tests
import test_bookmark
import test_container
import test_content
import test_datatype
import test_document
import test_draw_page
import test_element
import test_frame
import test_heading
import test_image
import test_link
import test_list
import test_meta
import test_note
import test_paragraph
import test_reference
import test_section
import test_shapes
import test_span
import test_style
import test_styles
import test_table
import test_tracked_changes
import test_utils
import test_variable
import test_xmlpart


test_modules = [test_bookmark,
                test_container,
                test_content,
                test_datatype,
                test_document,
                test_draw_page,
                test_element,
                test_frame,
                test_heading,
                test_image,
                test_link,
                test_list,
                test_meta,
                test_note,
                test_paragraph,
                test_reference,
                test_section,
                test_shapes,
                test_span,
                test_style,
                test_styles,
                test_table,
                test_tracked_changes,
                test_utils,
                test_variable,
                test_xmlpart]


loader = TestLoader()

if __name__ == '__main__':
    suite = TestSuite()
    for module in test_modules:
        suite.addTest(loader.loadTestsFromModule(module))

    TextTestRunner(verbosity=1).run(suite)
