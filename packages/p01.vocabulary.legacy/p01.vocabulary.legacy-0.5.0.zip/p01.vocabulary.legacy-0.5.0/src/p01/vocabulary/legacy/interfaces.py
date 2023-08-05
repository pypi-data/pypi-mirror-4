##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: country.py 39 2007-01-28 07:08:55Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.schema.interfaces


class II18nVocabularyTokenized(zope.schema.interfaces.IVocabularyTokenized):
    """Marker interface for I18nAware widgets.
    
    Such widget can sort the vocabulary by the given language.
    """


class ILegacyVocabulary(zope.schema.interfaces.IVocabularyTokenized):
    """Legacy vocabulary providing a fallback vocabulary."""


class II18nLegacyVocabulary(II18nVocabularyTokenized):
    """Legacy vocabulary providing a fallback vocabulary."""


class IFallBackVocabulary(zope.schema.interfaces.IVocabularyTokenized):
    """Fallback vocabulary used for vocabularies."""


class IGroupVocabulary(zope.schema.interfaces.IVocabularyTokenized):
    """Group vocabulary providing a option groups"""


class IGroupTerm():
    """Group term providing weight order criteria, first and last marker"""
