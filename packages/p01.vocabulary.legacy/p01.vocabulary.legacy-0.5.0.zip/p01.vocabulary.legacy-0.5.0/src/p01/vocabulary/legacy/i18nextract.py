##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: country.py 39 2007-01-28 07:08:55Z roger.ineichen $
"""

import os
from p01.vocabulary.legacy import vocabulary


# new style i18n vocabulary message extraction used with z3c.recipe.i18n
def vocabularyMessageExtractorWalker(arg, dirname, fnames):
    catalog, base_dir, exclude_dirs, messageFactory, vocabularyFactory = arg
    # Make sure we are not stepping into an excluded dir
    for exclude_dir in exclude_dirs:
        if dirname.startswith(exclude_dir):
            return
    # extract all strings from the csv files from the walking directory
    for filename in sorted(fnames):
        # .old is for legacyVocabulary items
        if filename.endswith('.csv') or filename.endswith('.old'):
            fullpath = os.path.join(dirname, filename)
            try:
                vocab = vocabularyFactory(fullpath, messageFactory=messageFactory)
            except ValueError, e:
                #something wrong in the data, or different format!
                print "WARNING: %s %s" % (fullpath, e)
                continue
            for index, term in enumerate(vocab):
                if term.title not in catalog:
                    catalog[term.title] = []
                reportpath = fullpath.replace(base_dir, '')
                catalog[term.title].append((reportpath, index+1))


def extractVocabularyMessages(path, base_dir, exclude_dirs,
    messageFactory, vocabularyFactory=vocabulary.CSVVocabulary):
    """Extract message strings from CSV data files located in dataDir."""
    if not path.startswith(base_dir):
        # do not collect if path is not a subfolder of base_dir
        return {}
    catalog = {}
    exclude_dirs = [os.path.join(path, dir) for dir in exclude_dirs]
    os.path.walk(path, vocabularyMessageExtractorWalker,
        (catalog, base_dir, exclude_dirs, messageFactory, vocabularyFactory))
    return catalog
