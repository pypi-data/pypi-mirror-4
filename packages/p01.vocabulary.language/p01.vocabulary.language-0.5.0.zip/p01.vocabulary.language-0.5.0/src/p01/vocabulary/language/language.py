##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: country.py 39 2007-01-28 07:08:55Z roger.ineichen $
"""

import csv
import os
import os.path

import zope.interface
from zope.schema import vocabulary
from zope.schema.interfaces import IVocabularyFactory

import p01.util.ucsv
from p01.vocabulary.language.i18n import MessageFactory as _


def csvVocabulary(fName):
    filename = os.path.join(os.path.dirname(__file__), 'data', fName)
    # Open a file and read the data
    f = file(filename)
    reader = p01.util.ucsv.UnicodeReader(f, delimiter=";")
    # Create the terms and the vocabulary
    terms = []
    for id, title in reader:
        msg = _(title, default=title)
        term = vocabulary.SimpleTerm(id, title=msg)
        terms.append(term)
    return vocabulary.SimpleVocabulary(terms)


try:
    iso639Alpha2LanguageVocabularyData =  csvVocabulary(
        'iso-639-alpha-2.csv')

    @zope.interface.implementer(IVocabularyFactory)
    def ISO639Alpha2LanguageVocabulary(context):
        return iso639Alpha2LanguageVocabularyData
except IOError:
    # data not generated
    iso639Alpha2LanguageVocabularyData = None
    ISO639Alpha2LanguageVocabulary = None
