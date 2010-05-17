#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Import from the Standard Library
from datetime import date
from os import remove
from os.path import exists
from sys import argv, stderr, exit

# Import from lpod
from lpod.document import odf_new_document_from_template
from lpod.span import odf_create_span
from lpod.template import stl_odf


def get_namespace(homme=False):
    return {u"titre": u"Test de STL no 1",
            u"date": date.today().strftime(u"%d/%m/%Y"),
            u"homme": homme,
            u"genre": u"M." if homme else u"Mme",
            u"nom": u"Michu",
            u"enum1": {'label': u"Revenu", 'value': 1234.56},
            u"enum2": {'label': u"Âge", 'value': 65},
            u"couleur": u"rouge",
            u"gras": u"gras comme un moine",
            u"élément": odf_create_span(u"élément", style='T2')}


if __name__ == '__main__':
    try:
        output = argv[1]
    except IndexError:
        print >>stderr, "Usage: %s <output document>" % argv[0]
        exit(1)
    document = odf_new_document_from_template('test_template.ott')
    stl_odf(document, get_namespace())
    if exists(output):
        remove(output)
    document.save(output)
    print 'Document "%s" generated.' % output
