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
from p01.vocabulary.country.i18n import MessageFactory as _


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
    iso3166Alpha2CountryVocabularyData = csvVocabulary('iso-3166-alpha-2.csv')

    @zope.interface.implementer(IVocabularyFactory)
    def ISO3166Alpha2CountryVocabulary(context):
        return iso3166Alpha2CountryVocabularyData
except IOError:
    # data not generated
    iso3166Alpha2CountryVocabularyData = None
    ISO3166Alpha2CountryVocabulary = None


try:
    iso3166Alpha3CountryVocabularyData = csvVocabulary('iso-3166-alpha-3.csv')
    
    @zope.interface.implementer(IVocabularyFactory)
    def ISO3166Alpha3CountryVocabulary(context):
        return iso3166Alpha3CountryVocabularyData
except IOError:
    # data not generated
    iso3166Alpha3CountryVocabularyData = None
    ISO3166Alpha3CountryVocabulary = None


try:
    from p01.vocabulary.country.mapping import alpha2to3
    from p01.vocabulary.country.mapping import alpha3to2
except ImportError:
    # data not generated
    alpha2to3 = None
    alpha3to2 = None
