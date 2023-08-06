##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""I18n Extraction Tool for CSV Files

Important: The functionality provided in this package must be manually
integrated into your string extraction script/tool.
"""
import os

from z3c.csvvocabulary import vocabulary

def _extractCsvStrings(dirname, fnames, catalog, basepath, exclude_dirs):
    # Make sure we have a data directory
    if os.path.split(dirname)[-1] != 'data':
        return
    # Make sure we are not stepping into an excluded dir
    for exclude_dir in exclude_dirs:
        if dirname.startswith(exclude_dir):
            return
    # Now we extract all strings from the csv files
    for filename in fnames:
        if filename.endswith('.csv'):
            fullpath = os.path.join(dirname, filename)
            vocab = vocabulary.CSVVocabulary(fullpath)
            for index, term in enumerate(vocab):
                if term.title not in catalog:
                    catalog[term.title] = []
                reportpath = fullpath.replace(basepath, '')
                catalog[term.title].append((reportpath, index+1))


def csvStrings(path, base_dir, exclude_dirs=()):
    """Extract message strings from CSV data files

    This function allows the standard i18n extraction tool arguments for
    simple integration.
    """
    catalog = {}
    exclude_dirs = [os.path.join(path, dir) for dir in exclude_dirs]
    for dirname, subnames, fnames in os.walk(path):
        _extractCsvStrings(dirname, fnames, catalog, base_dir, exclude_dirs)
    return catalog
