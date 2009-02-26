# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
import unittest
from unittest import TestCase

# Import from itools
from itools.xml import XML_DECL, START_ELEMENT

# Import from lpod
from lpod.container import new_odf_container, get_odf_container
from lpod.container import ODF_EXTENSIONS


class CreateElementTestCase(TestCase):

    def test_simple(self):
        element = create_element('<office:document></office:document>')



class ElementTestCase(TestCase):

    def test_get_element_list(self):
        raise NotImplementedError


    def test_get_attribute(self):
        raise NotImplementedError


    def test_set_attribute(self):
        raise NotImplementedError


    def test_get_text(self):
        raise NotImplementedError


    def test_set_text(self):
        raise NotImplementedError


    def test_insert_element(self):
        raise NotImplementedError


    def test_copy(self):
        raise NotImplementedError


    def test_delete(self):
        raise NotImplementedError



class ContextTestCase(TestCase):

    def test_get_element_list(self):
        raise NotImplementedError


    def serialize(self):
        raise NotImplementedError
