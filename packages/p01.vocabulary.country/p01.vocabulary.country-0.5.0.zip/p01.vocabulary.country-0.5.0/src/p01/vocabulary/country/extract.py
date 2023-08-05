##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Extract country vocabulary data based on debian isofiles

$Id:$
"""
__docformat__ = "reStructuredText"

import os
import os.path
import shutil

import lxml.etree

MAPPING_HEADER = '''##############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH.
# All Rights Reserved.
# 
# AUTO GENERATED FILE
# see: p01/vocaulary/country/extract.py for more information 
#
##############################################################################
"""Alpha 2-3 and 3-2 mapping data
$Id:$
"""

'''

HERE = os.path.dirname(__file__)
DATA_DIR = os.path.join(HERE, 'data')
LOCALES_DIR = os.path.join(HERE, 'locales')
SOURCE_DIR = os.path.join(HERE, 'source')
ISO_3166_DIR = os.path.join(SOURCE_DIR, 'iso-3166')
ISO_3166_XML = os.path.join(ISO_3166_DIR, 'iso_3166.xml')
ISO_3166_ALPHA_2_CSV = os.path.join(DATA_DIR, 'iso-3166-alpha-2.csv')
ISO_3166_ALPHA_3_CSV = os.path.join(DATA_DIR, 'iso-3166-alpha-3.csv')
MAPPING_FILE = os.path.join(HERE, 'mapping.py')


class Country(object):

    def __init__(self, element, **kw):
        self._element = element
        for key, value in kw.items():
            setattr(self, key, value)


class Countries(object):

    # Override those names in sub-classes for specific ISO database.

    field_map = dict(alpha_2_code='alpha2',
                     alpha_3_code='alpha3',
                     numeric_code='numeric',
                     name='name',
                     official_name='official_name',
                     common_name='common_name')
    xml_tag = 'iso_3166_entry'

    def __init__(self, filename):
        self.objects = []
        self.indices = {}

        f = open(filename, 'rb')
        etree = lxml.etree.parse(f)

        for entry in etree.xpath('//%s' % self.xml_tag):
            mapped_data = {}
            for key in entry.keys():
                mapped_data[self.field_map[key]] = entry.get(key)
            entry_obj = Country(entry, **mapped_data)
            self.objects.append(entry_obj)

        # Create indices
        for key in self.field_map.values():
            self.indices[key] = {}

        # Update indices
        for obj in self.objects:
            for key in self.field_map.values():
                value = getattr(obj, key, None)
                if value is None:
                    continue
                if value in self.indices[key]:
                    print ('Country %r already taken in index %r and will be '
                          'ignored. This is an error in the XML databases.' %
                          (value, key))
                self.indices[key][value] = obj

    def __iter__(self):
        return iter(self.objects)

    def __len__(self):
        return len(self.objects)

    def get(self, **kw):
        assert len(kw) == 1, 'Only one criteria may be given.'
        field, value = kw.items()[0]
        return self.indices[field][value]


def msgfmt(path):
    for language in os.listdir(path):
        lc_messages_path = os.path.join(path, language, 'LC_MESSAGES')

        # Make sure we got a language directory
        if not os.path.isdir(lc_messages_path):
            continue

        for domain_file in os.listdir(lc_messages_path):
            if domain_file == 'iso3166.po':
                poPath = os.path.join(lc_messages_path, 'iso3166.po')
                moPath = os.path.join(lc_messages_path, 'iso3166.mo')
                print 'Compile language "%s"' % language
                os.system('msgfmt -o %s %s' %(moPath, poPath))


def extractVocabularyData():
    # generate alpha 2 country codes vocabulary
    print "Extract vocabulary data based on debian iso_3166.xml source file"
    alpha2CSVFile = open(ISO_3166_ALPHA_2_CSV, 'wb')
    countries = Countries(ISO_3166_XML)
    for country in countries:
        name = getattr(country, 'common_name', country.name)
        line = '"%s";"%s"\n' % (country.alpha2.encode('UTF-8'),
            name.encode('UTF-8'))
        alpha2CSVFile.write(line)

    # generate alpha 3 country codes vocabulary
    alpha3CSVFile = open(ISO_3166_ALPHA_3_CSV, 'wb')
    for country in countries:
        name = getattr(country, 'common_name', country.name)
        line = '"%s";"%s"\n' % (country.alpha3.encode('UTF-8'),
            name.encode('UTF-8'))
        alpha3CSVFile.write(line)

    # copy locales used by alpha 2 and alpha 3
    print "Extract locales based on debian iso-3166 source files"
    for po in os.listdir(ISO_3166_DIR):
        if po.endswith('.po'):
            lang = po[:-3]
            msgDir = os.path.join(LOCALES_DIR, lang, 'LC_MESSAGES')
            poPath = os.path.join(msgDir, 'iso3166.po')
            if not os.path.exists(poPath):
                os.makedirs(msgDir)
                source = os.path.join(ISO_3166_DIR, po)
                shutil.copy(source, poPath)
    print "Compile *.po to *.mo files"
    msgfmt(LOCALES_DIR)
    print "Sucessfully generated vocabulary and locales data"


def extractMappingModule():
    """Generate mapping module"""
    print "Generate Alpha 2 - 3 mapping data based on iso_3166.xml source file"
    # generate alpha 2 -> 3 mapping
    print "create file %s" % MAPPING_FILE
    countries = Countries(ISO_3166_XML)
    pyFile = open(MAPPING_FILE, 'wb')
    pyFile.write(MAPPING_HEADER)
    pyFile.write('alpha2to3 = {\n')
    for country in countries:
        name = getattr(country, 'common_name', country.name)
        line = "    u'%s': u'%s',\n" % (country.alpha2, country.alpha3)
        pyFile.write(line)
    pyFile.write('}')
    pyFile.write('\n')
    pyFile.write('\n')

    print "Generate Alpha 3 - 2 mapping data based on iso_3166.xml source file"
    # generate alpha 3 -> 2 mapping
    pyFile.write('alpha3to2 = {\n')
    for country in countries:
        name = getattr(country, 'common_name', country.name)
        line = "    u'%s': u'%s',\n" % (country.alpha3, country.alpha2)
        pyFile.write(line)
    pyFile.write('}')
    pyFile.write('\n')
    print "Sucessfully generated mapping module"
