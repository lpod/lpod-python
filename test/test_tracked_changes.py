# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009 Ars Aperta, Itaapy, Pierlis, Talend.
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
from unittest import TestCase, main
from datetime import datetime

# Import from lpod
from lpod.document import odf_get_document
from lpod.tracked_changes import odf_tracked_changes


class TestTrackedChanges(TestCase):

    def setUp(self):
        uri = 'samples/tracked_changes.odt'
        self.document = document = odf_get_document(uri)
        self.body = document.get_body()


    def test_get_tracked_changes(self):
        tracked_changes = self.body.get_tracked_changes()
        self.assert_(isinstance(tracked_changes, odf_tracked_changes))



class TestChangedRegionTestCase(TestCase):

    def setUp(self):
        uri = 'samples/tracked_changes.odt'
        self.document = document = odf_get_document(uri)
        self.tracked_changes = document.get_body().get_tracked_changes()


    def test_get_changed_region_list(self):
        regions = self.tracked_changes.get_changed_region_list()
        self.assertEqual(len(regions), 3)


    def test_get_changed_region_list_creator(self):
        creator = u'Romain Gauthier'
        tracked_changes = self.tracked_changes
        regions = tracked_changes.get_changed_region_list(creator=creator)
        expected = ('<text:changed-region text:id="ct-1371898904">\n'
                    '     <text:deletion>\n'
                    '      <office:change-info>\n'
                    '       <dc:creator>Romain Gauthier</dc:creator>\n'
                    '       <dc:date>2009-08-21T19:27:00</dc:date>\n'
                    '      </office:change-info>\n'
                    '      <text:p text:style-name="Standard">les</text:p>\n'
                    '     </text:deletion>\n'
                    '    </text:changed-region>\n')
        self.assertEqual(regions[0].serialize(pretty=True), expected)


    def test_get_changed_region_list_date(self):
        date = datetime(2009, 8, 21, 17, 27, 00)
        tracked_changes = self.tracked_changes
        regions = tracked_changes.get_changed_region_list(date=date)
        expected = ('<text:changed-region text:id="ct-1371898456">\n'
                    '     <text:deletion>\n'
                    '      <office:change-info>\n'
                    '       <dc:creator>David Versmisse</dc:creator>\n'
                    '       <dc:date>2009-08-21T17:27:00</dc:date>\n'
                    '      </office:change-info>\n'
                    '      <text:p text:style-name="Standard">amis,</text:p>\n'
                    '     </text:deletion>\n'
                    '    </text:changed-region>\n')
        self.assertEqual(regions[0].serialize(pretty=True), expected)


    def test_get_changed_region_list_regex(self):
        tracked_changes = self.tracked_changes
        regions = tracked_changes.get_changed_region_list(content=ur'amis')
        expected = ('<text:changed-region text:id="ct-1371898456">\n'
                    '     <text:deletion>\n'
                    '      <office:change-info>\n'
                    '       <dc:creator>David Versmisse</dc:creator>\n'
                    '       <dc:date>2009-08-21T17:27:00</dc:date>\n'
                    '      </office:change-info>\n'
                    '      <text:p text:style-name="Standard">amis,</text:p>\n'
                    '     </text:deletion>\n'
                    '    </text:changed-region>\n')
        self.assertEqual(regions[0].serialize(pretty=True), expected)


    def test_get_changed_region_by_id(self):
        tracked_changes = self.tracked_changes
        region = tracked_changes.get_changed_region(text_id='ct-1371898680')
        expected = ('<text:changed-region text:id="ct-1371898680">\n'
                    '     <text:insertion>\n'
                    '      <office:change-info>\n'
                    '       <dc:creator>Herv&#233; Cauwelier</dc:creator>\n'
                    '       <dc:date>2009-08-21T18:27:00</dc:date>\n'
                    '      </office:change-info>\n'
                    '     </text:insertion>\n'
                    '    </text:changed-region>\n')
        self.assertEqual(region.serialize(pretty=True), expected)


    def test_get_changed_region_by_creator(self):
        creator = u'David Versmisse'
        tracked_changes = self.tracked_changes
        region = tracked_changes.get_changed_region(creator=creator)
        expected = ('<text:changed-region text:id="ct-1371898456">\n'
                    '     <text:deletion>\n'
                    '      <office:change-info>\n'
                    '       <dc:creator>David Versmisse</dc:creator>\n'
                    '       <dc:date>2009-08-21T17:27:00</dc:date>\n'
                    '      </office:change-info>\n'
                    '      <text:p text:style-name="Standard">amis,</text:p>\n'
                    '     </text:deletion>\n'
                    '    </text:changed-region>\n')
        self.assertEqual(region.serialize(pretty=True), expected)


    def test_get_changed_region_by_date(self):
        date = datetime(2009, 8, 21, 18, 27, 00)
        tracked_changes = self.tracked_changes
        region = tracked_changes.get_changed_region(date=date)
        expected = ('<text:changed-region text:id="ct-1371898680">\n'
                    '     <text:insertion>\n'
                    '      <office:change-info>\n'
                    '       <dc:creator>Herv&#233; Cauwelier</dc:creator>\n'
                    '       <dc:date>2009-08-21T18:27:00</dc:date>\n'
                    '      </office:change-info>\n'
                    '     </text:insertion>\n'
                    '    </text:changed-region>\n')
        self.assertEqual(region.serialize(pretty=True), expected)


    def test_get_changed_region_by_content(self):
        tracked_changes = self.tracked_changes
        region = tracked_changes.get_changed_region(content=ur'les')
        expected = ('<text:changed-region text:id="ct-1371898904">\n'
                    '     <text:deletion>\n'
                    '      <office:change-info>\n'
                    '       <dc:creator>Romain Gauthier</dc:creator>\n'
                    '       <dc:date>2009-08-21T19:27:00</dc:date>\n'
                    '      </office:change-info>\n'
                    '      <text:p text:style-name="Standard">les</text:p>\n'
                    '     </text:deletion>\n'
                    '    </text:changed-region>\n')
        self.assertEqual(region.serialize(pretty=True), expected)



class TestChangesIdsTestCase(TestCase):

    def setUp(self):
        uri = 'samples/tracked_changes.odt'
        self.document = document = odf_get_document(uri)
        self.body = document.get_body()


    def test_get_changes_ids(self):
        paragraph = self.body.get_paragraph(content=ur'Bonjour')
        changes_ids = paragraph.get_changes_ids()
        expected = ['ct-1371898904', 'ct-1371898680', 'ct-1371898456']
        self.assertEqual(changes_ids, expected)



if __name__ == '__main__':
    main()
