# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Authors: David Versmisse <david.versmisse@itaapy.com>
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
from glob import glob

# Import from lpod
from lpod.document import odf_new_document_from_type
from lpod.table import import_from_csv

# Get elements
document = odf_new_document_from_type('spreadsheet')
body = document.get_body()

for id, filename in enumerate(glob('./files/*.csv')):
    table = import_from_csv(filename, u'Table %s' % (id + 1))
    # Table is represented as a matrix in memory,
    # so ask to reformat it to XML
    body.append_element(table.to_odf_element())

# Save
filename = 'spreadsheet.ods'
document.save(filename, pretty=True)
print 'Document "%s" generated.' % filename
