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

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
LOCALES_DIR = os.path.join(os.path.dirname(__file__), 'locales')
SOURCE_DIR = os.path.join(os.path.dirname(__file__), 'source')
ISO_639_DIR = os.path.join(SOURCE_DIR, 'iso-639')
ISO_639_XML = os.path.join(ISO_639_DIR, 'iso_639.xml')
ISO_639_ALPHA_2_CSV = os.path.join(DATA_DIR, 'iso-639-alpha-2.csv')


class Language(object):

    alpha2 = None

    def __init__(self, element, **kw):
        self._element = element
        for key, value in kw.items():
            setattr(self, key, value)


class Languages(object):

    field_map = dict(iso_639_2B_code='bibliographic',
                     iso_639_2T_code='terminology',
                     iso_639_1_code='alpha2',
                     name='name')
    xml_tag = 'iso_639_entry'

    def __init__(self, filename):
        self.objects = []
        self.indices = {}

        f = open(filename, 'rb')
        etree = lxml.etree.parse(f)

        for entry in etree.xpath('//%s' % self.xml_tag):
            mapped_data = {}
            for key in entry.keys():
                mapped_data[self.field_map[key]] = entry.get(key)
            entry_obj = Language(entry, **mapped_data)
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
                    print ('Language %r already taken in index %r and will be '
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
            if domain_file == 'iso639.po':
                poPath = os.path.join(lc_messages_path, 'iso639.po')
                moPath = os.path.join(lc_messages_path, 'iso639.mo')
                print 'Compile language "%s"' % language
                os.system('msgfmt -o %s %s' %(moPath, poPath))


def extractVocabularyData():
    # generate alpha 2 country codes vocabulary
    print "Extract vocabulary data based on debian iso_639.xml source file"
    alpha2CSVFile = open(ISO_639_ALPHA_2_CSV, 'wb')
    languages = Languages(ISO_639_XML)
    for lang in languages:
        if lang.alpha2 is None:
            continue
        line = '"%s";"%s"\n' % (lang.alpha2.encode('UTF-8'),
            lang.name.encode('UTF-8'))
        alpha2CSVFile.write(line)

    # copy locales
    print "Extract locales based on debian iso-639 source files"
    for po in os.listdir(ISO_639_DIR):
        if po.endswith('.po'):
            lang = po[:-3]
            msgDir = os.path.join(LOCALES_DIR, lang, 'LC_MESSAGES')
            poPath = os.path.join(msgDir, 'iso639.po')
            if not os.path.exists(poPath):
                os.makedirs(msgDir)
                source = os.path.join(ISO_639_DIR, po)
                shutil.copy(source, poPath)
    print "Compile *.po to *.mo files"
    msgfmt(LOCALES_DIR)
    print "Sucessfully generated vocabulary and locales data"


def main():
    extractVocabularyData()


