# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestLoader, TestSuite, TextTestRunner

# Import tests
import test_utils
import test_container
import test_xmlpart
import test_document
import test_styles


test_modules = [test_utils, test_container, test_xmlpart, test_document,
                test_styles]


loader = TestLoader()

if __name__ == '__main__':
    suite = TestSuite()
    for module in test_modules:
        suite.addTest(loader.loadTestsFromModule(module))

    TextTestRunner(verbosity=1).run(suite)
