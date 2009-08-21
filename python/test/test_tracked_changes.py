# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from unittest import TestCase, main

# Import from lpod
from lpod.document import odf_get_document


class TestTrackedChanges(TestCase):

    def setUp(self):
        file = 'samples/tracked_changes.odt'
        self.document = document = odf_get_document(file)
        self.content = document.get_xmlpart('content')


    def tearDown(self):
        del self.content
        del self.document


    def test_get_tracked_changes(self):
        content = self.content
        tracked_changes = content.get_tracked_changes()
        expected = ('<text:tracked-changes>\n'
                    '    <text:changed-region text:id="ct-1371898904">\n'
                    '     <text:deletion>\n'
                    '      <office:change-info>\n'
                    '       <dc:creator>Romain Gauthier</dc:creator>\n'
                    '       <dc:date>2009-08-21T18:27:00</dc:date>\n'
                    '      </office:change-info>\n'
                    '      <text:p text:style-name="Standard">les</text:p>\n'
                    '     </text:deletion>\n'
                    '    </text:changed-region>\n'
                    '    <text:changed-region text:id="ct-1371898680">\n'
                    '     <text:insertion>\n'
                    '      <office:change-info>\n'
                    '       <dc:creator>Romain Gauthier</dc:creator>\n'
                    '       <dc:date>2009-08-21T18:27:00</dc:date>\n'
                    '      </office:change-info>\n'
                    '     </text:insertion>\n'
                    '    </text:changed-region>\n'
                    '    <text:changed-region text:id="ct-1371898456">\n'
                    '     <text:deletion>\n'
                    '      <office:change-info>\n'
                    '       <dc:creator>Romain Gauthier</dc:creator>\n'
                    '       <dc:date>2009-08-21T18:27:00</dc:date>\n'
                    '      </office:change-info>\n'
                    '      <text:p text:style-name="Standard">amis,</text:p>\n'
                    '     </text:deletion>\n'
                    '    </text:changed-region>\n'
                    '   </text:tracked-changes>\n')
        self.assertEqual(tracked_changes.serialize(pretty=True), expected)


    def test_get_changes_ids(self):
        content = self.content
        body = content.get_body()
        paragraph = body.get_paragraph_by_content(ur'Bonjour')
        changes_ids = paragraph.get_changes_ids()
        expected = ['ct-1371898904', 'ct-1371898680', 'ct-1371898456']
        self.assertEqual(changes_ids, expected)



if __name__ == '__main__':
    main()
