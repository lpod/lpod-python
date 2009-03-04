# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestLoader, TestSuite, TextTestRunner

# Import tests
import test_container
import test_xmlpart


test_modules = [test_container, test_xmlpart]


loader = TestLoader()

if __name__ == '__main__':
    suite = TestSuite()
    for module in test_modules:
        suite.addTest(loader.loadTestsFromModule(module))

    TextTestRunner(verbosity=1).run(suite)
