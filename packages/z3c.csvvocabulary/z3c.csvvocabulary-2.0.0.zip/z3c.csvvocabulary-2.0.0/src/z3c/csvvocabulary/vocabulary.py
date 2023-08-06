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
"""CSV Vocabulary Implementation

$Id: vocabulary.py 129508 2013-02-20 03:40:24Z srichter $
"""
__docformat__ = "reStructuredText"
import csv
import os.path
import sys

from zope.schema import vocabulary
from zope.i18nmessageid import MessageFactory

PY3 = sys.version_info[0] == 3

_ = MessageFactory('zope')


def CSVVocabulary(filename, messageFactory=_, encoding='latin1'):
    # Create a prefix
    prefix = os.path.split(filename)[-1][:-4]
    # Open a file and read the data
    if PY3:
        f = open(filename, 'r', encoding=encoding)
    else:
        f = open(filename, 'r')
    # Py3: The big problem here is that the Py2 CSV Reader is not unicode
    # aware, so we must handle everything in bytes, but in Py3 it is exactely
    # the opposite and we are forced decode to unicode early.
    reader = csv.reader(f, delimiter=";")
    # Create the terms and the vocabulary
    terms = []
    for id, title in reader:
        if not PY3:
            title = title.decode(encoding)
        term = vocabulary.SimpleTerm(
            id, title=messageFactory(prefix+'-'+id, default=title))
        terms.append(term)
    f.close()
    return vocabulary.SimpleVocabulary(terms)
