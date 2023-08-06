==============
CSV Vocabulary
==============

This package provides a very simple vocabulary implementation using CSV
files. The advantage of CSV files is that they provide an external point to
specify data, which allows a non-developer to adjust the data themselves.

  >>> import z3c.csvvocabulary

  >>> import os.path
  >>> path = os.path.dirname(z3c.csvvocabulary.__file__)

CSV Vocabulary
--------------

The CSV Vocabulary implementation is really just a function that creates a
simple vocabulary with titled terms. There is a ``sample.csv`` file in the
``data`` directory of the ``testing`` sub-package, so let's create a
vocabulary from that:

  >>> csvfile = os.path.join(path, 'testing', 'data', 'sample.csv')

  >>> samples = z3c.csvvocabulary.CSVVocabulary(csvfile)
  >>> samples
  <zope.schema.vocabulary.SimpleVocabulary object at ...>

  >>> sorted([term.value for term in samples])
  ['value1', 'value2', 'value3', 'value4', 'value5']

Let's now look at a term:

  >>> term1 = samples.getTerm('value1')
  >>> term1
  <zope.schema.vocabulary.SimpleTerm object at ...>

As you can see, the vocabulary automatically prefixes the value:

  >>> term1.value
  'value1'

  >>> term1.token
  'value1'

  >>> term1.title
  u'sample-value1'

While it looks like the title is the wrong unicode string, it is really an
I18n message:

  >>> type(term1.title)
  <type 'zope.i18nmessageid.message.Message'>

  >>> term1.title.default
  u'Title 1'

  >>> term1.title.domain
  'zope'

Of course, it is not always acceptable to make 'zope' the domain of the
message. You can specify the message factory when initializing the vocabulary:

  >>> from zope.i18nmessageid import MessageFactory
  >>> exampleDomain = MessageFactory(u'example')

  >>> samples = z3c.csvvocabulary.CSVVocabulary(csvfile, exampleDomain)
  >>> term1 = samples.getTerm(u'value1')
  >>> term1.title.domain
  'example'

The vocabulary is designed to work with small data sets, typically choices in
user interfaces. All terms are created upon initialization, so the vocabulary
does not detect updates in the csv file or loads the data when needed. But as
I said, this is totally okay.


Encoding
````````

By default the vocabulary expects the csv file to be latin1 encoded.

  >>> csvfile = os.path.join(path, 'testing', 'data', 'utf-8.csv')
  >>> wrongEncoding = z3c.csvvocabulary.CSVVocabulary(csvfile)
  >>> wrongEncoding.getTerm('ae').title.default
  u'\xc3\xa4'

If you csv file has a different encoding you can specify it explicitly:

  >>> utf8Encoded = z3c.csvvocabulary.CSVVocabulary(csvfile, encoding='utf-8')
  >>> term = utf8Encoded.getTerm('ae')
  >>> term.title.default
  u'\xe4'


CSV Message String Extraction
-----------------------------

There is a simple function in ``i18nextract.py`` that extracts all message
strings from the CSV files in a particular sub-tree. Here we just want to make
sure that the function completes and some dummy data from the testing package
will be used:

  >>> basedir = os.path.dirname(z3c.__file__)

  >>> catalog = z3c.csvvocabulary.csvStrings(path, basedir)
  >>> pprint(catalog)
  {u'sample-value1': [('...sample.csv', 1)],
   u'sample-value2': [('...sample.csv', 2)],
   u'sample-value3': [('...sample.csv', 3)],
   u'sample-value4': [('...sample.csv', 4)],
   u'sample-value5': [('...sample.csv', 5)],
   u'utf-8-ae': [('...utf-8.csv', 1)],
   u'utf-8-oe': [('...utf-8.csv', 2)]}
