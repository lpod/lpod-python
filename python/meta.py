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
from datetime import timedelta, date, datetime
from decimal import Decimal
from datatype import DateTime, Duration, Boolean, Date

# Import from lpod
from element import LAST_CHILD, odf_create_element
from xmlpart import odf_xmlpart


class odf_meta(odf_xmlpart):

    def get_meta_body(self):
        return self.get_element('//office:meta')


    def get_title(self):
        """Get the title of the document.

        This is not the first heading but the title metadata.

        Return: unicode (or None if inexistant)
        """
        element = self.get_element('//dc:title')
        if element is None:
            return None
        return element.get_text()


    def set_title(self, title):
        """Set the title of the document.

        This is not the first heading but the title metadata.

        Arguments:

            title -- unicode
        """
        element = self.get_element('//dc:title')
        if element is None:
            element = odf_create_element('<dc:title/>')
            self.get_meta_body().insert_element(element, LAST_CHILD)
        element.set_text(title)


    def get_description(self):
        """Get the description of the document.

        Return: unicode (or None if inexistant)
        """
        element = self.get_element('//dc:description')
        if element is None:
            return None
        return element.get_text()


    def set_description(self, description):
        """Set the title of the document.

        Arguments:

            description -- unicode
        """
        element = self.get_element('//dc:description')
        if element is None:
            element = odf_create_element('<dc:description/>')
            self.get_meta_body().insert_element(element, LAST_CHILD)
        element.set_text(description)


    def get_subject(self):
        """Get the subject of the document.

        Return: unicode (or None if inexistant)
        """
        element = self.get_element('//dc:subject')
        if element is None:
            return None
        return element.get_text()


    def set_subject(self, subject):
        """Set the subject of the document.

        Arguments:

            subject -- unicode
        """
        element = self.get_element('//dc:subject')
        if element is None:
            element = odf_create_element('<dc:subject/>')
            self.get_meta_body().insert_element(element, LAST_CHILD)
        element.set_text(subject)


    def get_language(self):
        """Get the language code of the document.

        Return: str (or None if inexistant)

        Example::

            >>> document.get_language()
            fr-FR
        """
        element = self.get_element('//dc:language')
        if element is None:
            return None
        return str(element.get_text())


    def set_language(self, language):
        """Set the language code of the document.

        Arguments:

            language -- str

        Example::

            >>> document.set_language('fr-FR')
        """
        if type(language) is not str:
            raise TypeError, ('language must be "xx-YY" lang-COUNTRY code '
                              '(RFC3066)')
        # FIXME test validity?
        element = self.get_element('//dc:language')
        if element is None:
            element = odf_create_element('<dc:language/>')
            self.get_meta_body().insert_element(element, LAST_CHILD)
        element.set_text(unicode(language))


    def get_modification_date(self):
        """Get the last modified date of the document.

        Return: datetime (or None if inexistant)
        """
        element = self.get_element('//dc:date')
        if element is None:
            return None
        modification_date = element.get_text()
        return DateTime.decode(modification_date)


    def set_modification_date(self, date):
        """Set the last modified date of the document.

        Arguments:

            date -- datetime
        """
        element = self.get_element('//dc:date')
        if element is None:
            element = odf_create_element('<dc:date/>')
            self.get_meta_body().insert_element(element, LAST_CHILD)
        modification_date = DateTime.encode(date)
        element.set_text(modification_date)


    def get_creation_date(self):
        """Get the creation date of the document.

        Return: datetime (or None if inexistant)
        """
        element = self.get_element('//meta:creation-date')
        if element is None:
            return None
        creation_date = element.get_text()
        return DateTime.decode(creation_date)


    def set_creation_date(self, date):
        """Set the creation date of the document.

        Arguments:

            date -- datetime
        """
        element = self.get_element('//meta:creation-date')
        if element is None:
            element = odf_create_element('<meta:creation-date/>')
            self.get_meta_body().insert_element(element, LAST_CHILD)
        creation_date = DateTime.encode(date)
        element.set_text(creation_date)


    def get_initial_creator(self):
        """Get the first creator of the document.

        Return: unicode (or None if inexistant)

        Example::

            >>> document.get_initial_creator()
            Unknown
        """
        element = self.get_element('//meta:initial-creator')
        if element is None:
            return None
        return element.get_text()


    def set_initial_creator(self, creator):
        """Set the first creator of the document.

        Arguments:

            creator -- unicode

        Example::

            >>> document.set_initial_creator(u"Plato")
        """
        element = self.get_element('//meta:initial-creator')
        if element is None:
            element = odf_create_element('<meta:initial-creator/>')
            self.get_meta_body().insert_element(element, LAST_CHILD)
        element.set_text(creator)


    def get_keyword(self):
        """Get the keyword(s) of the document.

        Return: unicode (or None if inexistant)
        """
        element = self.get_element('//meta:keyword')
        if element is None:
            return None
        return element.get_text()


    def set_keyword(self, keyword):
        """Set the keyword(s) of the document.

        Arguments:

            keyword -- unicode
        """
        element = self.get_element('//meta:keyword')
        if element is None:
            element = odf_create_element('<meta:keyword/>')
            self.get_meta_body().insert_element(element, LAST_CHILD)
        element.set_text(keyword)


    def get_editing_duration(self):
        """Get the time the document was edited, as reported by the
        generator.

        Return: timedelta (or None if inexistant)
        """
        element = self.get_element('//meta:editing-duration')
        if element is None:
            return None
        duration = element.get_text()
        return Duration.decode(duration)


    def set_editing_duration(self, duration):
        """Set the time the document was edited.

        Arguments:

            duration -- timedelta
        """
        if type(duration) is not timedelta:
            raise TypeError, u"duration must be a timedelta"
        element = self.get_element('//meta:editing-duration')
        if element is None:
            element = odf_create_element('<meta:editing-duration/>')
            self.get_meta_body().insert_element(element, LAST_CHILD)
        duration = Duration.encode(duration)
        element.set_text(duration)


    def get_editing_cycles(self):
        """Get the number of times the document was edited, as reported by
        the generator.

        Return: int (or None if inexistant)
        """
        element = self.get_element('//meta:editing-cycles')
        if element is None:
            return None
        cycles = element.get_text()
        return int(cycles)


    def set_editing_cycles(self, cycles):
        """Set the number of times the document was edited.

        Arguments:

            cycles -- int
        """
        if type(cycles) is not int:
            raise TypeError, u"cycles must be an int"
        if cycles < 1:
            raise ValueError, "cycles must be a positive int"
        element = self.get_element('//meta:editing-cycles')
        if element is None:
            element = odf_create_element('<meta:editing-cycles/>')
            self.get_meta_body().insert_element(element, LAST_CHILD)
        cycles = str(cycles)
        element.set_text(cycles)


    def get_generator(self):
        """Get the signature of the software that generated this document.

        Return: unicode (or None if inexistant)

        Example::

            >>> document.get_generator()
            KOffice/2.0.0
        """
        element = self.get_element('//meta:generator')
        if element is None:
            return None
        return element.get_text()


    def set_generator(self, generator):
        """Set the signature of the software that generated this document.

        Arguments:

            generator -- unicode

        Example::

            >>> document.set_generator(u"lpOD Project")
        """
        element = self.get_element('//meta:generator')
        if element is None:
            element = odf_create_element('<meta:generator/>')
            self.get_meta_body().insert_element(element, LAST_CHILD)
        element.set_text(generator)


    def get_statistic(self):
        """Get the statistic from the software that generated this document.

        Return: dict (or None if inexistant)

        Example::

            >>> document.get_statistic():
            {'meta:table-count': 1,
             'meta:image-count': 2,
             'meta:object-count': 3,
             'meta:page-count': 4,
             'meta:paragraph-count': 5,
             'meta:word-count': 6,
             'meta:character-count': 7}
        """
        element = self.get_element('//meta:document-statistic')
        if element is None:
            return None
        statistic = {}
        for key, value in element.get_attributes().iteritems():
            statistic[key] = int(value)
        return statistic


    def set_statistic(self, statistic):
        """Set the statistic for the documents: number of words, paragraphs,
        etc.

        Arguments:

            statistic -- dict

        Example::

            >>> statistic = {'meta:table-count': 1,
                             'meta:image-count': 2,
                             'meta:object-count': 3,
                             'meta:page-count': 4,
                             'meta:paragraph-count': 5,
                             'meta:word-count': 6,
                             'meta:character-count': 7}
            >>> document.set_statistic(statistic)
        """
        if type(statistic) is not dict:
            raise TypeError, "statistic must be a dict"
        element = self.get_element('//meta:document-statistic')
        for key, value in statistic.iteritems():
            if type(key) is not str:
                raise TypeError, "statistic key must be a str"
            if type(value) is not int:
                raise TypeError, "statistic value must be a int"
            element.set_attribute(key, str(value))


    def get_user_defined_metadata(self):
        """Return a dict of unicode/value mapping.

        Value types can be: Decimal, date, time, boolean or unicode.
        """

        result = {}
        for meta in self.get_element_list('//meta:user-defined'):
            # Read the values
            name = meta.get_attribute('meta:name')
            value_type = meta.get_attribute('meta:value-type')
            if value_type is None:
                value_type = 'string'
            value = meta.get_text()
            # Interpretation
            if value_type == 'boolean':
                result[name] = Boolean.decode(value)
            elif value_type in  ('float', 'percentage', 'currency'):
                result[name] = Decimal(value)
            elif value_type == 'date':
                if 'T' in value:
                    result[name] = DateTime.decode(value)
                else:
                    result[name] = Date.decode(value)
            elif value_type == 'string':
                result[name] = value
            elif value_type == 'time':
                result[name] = Duration.decode(value)
        return result


    def set_user_defined_metadata(self, name, value):
        if type(value) is bool:
            value_type = 'boolean'
            value = u'true' if value else u'false'
        elif isinstance(value, (int, float, Decimal)):
            value_type = 'float'
            value = unicode(value)
        elif type(value) is date:
            value_type = 'date'
            value = unicode(Date.encode(value))
        elif type(value) is datetime:
            value_type = 'date'
            value = unicode(DateTime.encode(value))
        elif type(value) is str:
            value_type = 'string'
            value = unicode(value)
        elif type(value) is unicode:
            value_type = 'string'
        elif type(value) is timedelta:
            value_type = 'time'
            value = unicode(Duration.encode(value))
        else:
            raise TypeError, 'unexpected type "%s" for value' % type(value)
        # Already the same element ?
        for metadata in self.get_element_list('//meta:user-defined'):
            if metadata.get_attribute('meta:name') == name:
                break
        else:
            data = '<meta:user-defined meta:name="%s"/>'
            metadata = odf_create_element(data % name.encode('utf_8'))
            self.get_meta_body().insert_element(metadata, LAST_CHILD)
        metadata.set_attribute('meta:value-type', value_type)
        metadata.set_text(value)
