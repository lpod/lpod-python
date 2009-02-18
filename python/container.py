# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library

# Import from itools
from itools.core import get_abspath


ODF_CLASSES = {
        'text': {'document': 'odt',
                 'template': 'ott'},
        'spreadsheet': {'document': 'ods',
                        'template': 'ots'},
        'presentation': {'document': 'odp',
                         'template': 'otp'},
        'drawing': {'document': 'odg',
                    'template': 'otg'},
        # TODO
}


class odf_container(object):

    def __init__(self, uri):
        # TODO use vfs/gio
        open(uri)

        self.uri = uri


    def _clone(self):
        clone = object.__new__(self.__class__)
        for name in self.__dict__:
            if name == 'uri':
                setattr(clone, 'uri', None)
            else:
                value = getattr(self, name)
                value = deepcopy(value)
                setattr(clone, name, value)

        return clone



def new_odf_container(odf_class=None, template_uri=None):
    if ((odf_class is None and template_uri is None)
         or (odf_class is not None and template_uri is not None)):
        raise ValueError, "either 'odf_class' or 'template_uri' is mandatory"
    if odf_class not in ODF_CLASSES:
        raise ValueError, "unknown ODF class '%s'" % odf_class

    if odf_class is not None:
        extension = ODF_CLASSES[odf_class]['template']
        path = 'templates/%s.%s' % (odf_class, extension)
        template_uri = get_abspath(path)

    template = get_odf_container(template_uri)

    # Return a copy of the template
    return template._clone()



def get_odf_container(uri):
    return odf_container(uri)
