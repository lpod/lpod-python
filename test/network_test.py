# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: Jerome Dumonteil <jerome.dumonteil@itaapy.com>
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
import os
from cStringIO import StringIO
from ftplib import FTP
from unittest import TestCase, main
from urllib import urlopen

# Import from lpod
from lpod.const import ODF_EXTENSIONS
from lpod.container import odf_get_container


# Tests requiring network moved from test_container and test_document
class NetworkTest(TestCase):

    def test_http_container(self):
        file = urlopen('http://ftp.lpod-project.org/example.odt')
        container = odf_get_container(file)
        mimetype = container.get_part('mimetype')
        self.assertEqual(mimetype, ODF_EXTENSIONS['odt'])


    def test_ftp_container(self):
        ftp = FTP('ftp.lpod-project.org')
        ftp.login()
        file = StringIO()
        ftp.retrbinary('RETR example.odt', file.write)
        ftp.quit()
        file.seek(0)
        container = odf_get_container(file)
        mimetype = container.get_part('mimetype')
        self.assertEqual(mimetype, ODF_EXTENSIONS['odt'])


    def test_http_document(self):
        file = urlopen('http://ftp.lpod-project.org/example.odt')
        document = odf_get_document(file)
        self.assertEqual(document.get_mimetype(), ODF_EXTENSIONS['odt'])


    def test_ftp_document(self):
        ftp = FTP('ftp.lpod-project.org')
        ftp.login()
        file = StringIO()
        ftp.retrbinary('RETR example.odt', file.write)
        ftp.quit()
        file.seek(0)
        document = odf_get_document(file)
        self.assertEqual(document.get_mimetype(), ODF_EXTENSIONS['odt'])




if __name__ == '__main__':
    main()
