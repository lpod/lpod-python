# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Romain Gauthier <romain@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#
# This file is part of Lpod (see: http://lpod-project.org).
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
import test_text
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
                test_text,
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
