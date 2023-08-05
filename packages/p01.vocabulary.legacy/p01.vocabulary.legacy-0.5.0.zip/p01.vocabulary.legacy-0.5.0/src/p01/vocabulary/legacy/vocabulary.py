##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id:$
"""

import os
import csv
import zope.interface
import zope.component
import zope.i18nmessageid
from zope.schema.interfaces import ITitledTokenizedTerm
from zope.schema.interfaces import IVocabularyTokenized
from zope.schema.interfaces import IVocabularyFactory
from zope.schema import vocabulary

from p01.vocabulary.legacy import interfaces

_ = zope.i18nmessageid.MessageFactory('p01')

MISSING_DATA = _('missing')
MISSING_VALUE = 'missing'
MISSING_TERM = vocabulary.SimpleTerm(MISSING_VALUE, MISSING_VALUE, MISSING_DATA)


class I18nSimpleVocabulary(vocabulary.SimpleVocabulary):
    """Simple vocabulary with i18n widget marker."""

    zope.interface.implements(interfaces.II18nVocabularyTokenized)


class LegacyVocabulary(vocabulary.SimpleVocabulary):
    """Vocabulary with legacy data support."""

    zope.interface.implements(interfaces.ILegacyVocabulary)

    missingTerm = MISSING_TERM
    name = ''
    legacyVocabulary = None

    def getLegacyVocabulary(self):
        if isinstance(self.legacyVocabulary, basestring):
            vr = vocabulary.getVocabularyRegistry()
            return vr.get(None, self.legacyVocabulary)
        elif self.legacyVocabulary is not None:
            return self.legacyVocabulary
        else:
            return zope.component.queryAdapter(self,
                interfaces.IFallBackVocabulary, name=self.name)

    def _getLegacyTerm(self, value):
        vocab = self.getLegacyVocabulary()
        if vocab is None:
            return self.missingTerm
        try:
            return vocab.getTerm(value)
        except (KeyError, LookupError):
            return self.missingTerm

    def _getLegacyTermByToken(self, token):
        vocab = self.getLegacyVocabulary()
        if vocab is None:
            return self.missingTerm
        try:
            return vocab.getTermByToken(token)
        except (KeyError, LookupError):
            return self.missingTerm

    def __contains__(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        if value == MISSING_VALUE:
            return True
        try:
            #value in self.by_value
            # sometimes values are not hashable, let's try to get them and if
            # no KeyError raises return True
            ignore = self.by_value[value]
            return True
        except KeyError:
            return False

    def getTerm(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        try:
            return self.by_value[value]
        except KeyError:
            return self._getLegacyTerm(value)

    def getTermByToken(self, token):
        """See zope.schema.interfaces.IVocabularyTokenized"""
        try:
            return self.by_token[token]
        except KeyError:
            return self._getLegacyTermByToken(token)

    def queryTitle(self, value):
        """Returns the title for the given value"""
        try:
            return self.by_value[value].title
        except KeyError:
            return None


class I18nLegacyVocabulary(LegacyVocabulary):
    """Vocabulary with legacy data support."""

    zope.interface.implements(interfaces.II18nLegacyVocabulary)


class FallBackVocabulary(vocabulary.SimpleVocabulary):
    """Vocabulary with legacy data support."""

    zope.interface.implements(interfaces.IFallBackVocabulary)
    zope.component.adapts(interfaces.ILegacyVocabulary)


def CSVVocabulary(filename, messageFactory, 
    vocabularyFactory=I18nSimpleVocabulary):
    # Create a prefix
    prefix = os.path.split(filename)[-1]
    while os.path.splitext(prefix)[1]:
        prefix = os.path.splitext(prefix)[0]
    # Open a file and read the data
    f = file(filename)
    reader = csv.reader(f, delimiter=";")
    # Create the terms and the vocabulary
    terms = []
    for row in reader:
        if not len(row):
            # skip empty lines (non separator)
            continue
        if row[0].startswith('#'):
            # skip lines startwing with comments
            continue
        id, title = row[0], row[1]
        title = unicode(title, 'latin1')
        term = vocabulary.SimpleTerm(id,
            title=messageFactory(prefix+'-'+id, default=title))
        terms.append(term)

    return vocabularyFactory(terms)


def LegacyCSVVocabulary(filename, messageFactory,
    vocabularyFactory=LegacyVocabulary):
        return CSVVocabulary(filename, messageFactory, vocabularyFactory)


def I18nLegacyCSVVocabulary(filename, messageFactory, 
    vocabularyFactory=I18nLegacyVocabulary):
        return CSVVocabulary(filename, messageFactory, vocabularyFactory)


def getFallBackVocabulary(filename, messageFactory, 
    vocabularyFactory=FallBackVocabulary):
        return CSVVocabulary(filename, messageFactory, vocabularyFactory)
