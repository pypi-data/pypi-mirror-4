Vocabulary
----------

This vocabulary implementation supports legacy data for each vocabulary. Let's
setup a vocabulary with some sample data and support a legacy data vocabulary.

  >>> import zope.interface
  >>> import zope.component
  >>> from zope.schema.interfaces import IVocabularyTokenized
  >>> from p01.vocabulary.legacy import interfaces


CSVVocabulary
-------------

Let's first test our csv vocabulary:


  >>> import os
  >>> import zope.i18nmessageid
  >>> from p01.vocabulary.legacy import vocabulary
  >>> _messageFactory = zope.i18nmessageid.MessageFactory('p01')

  >>> def sampleVocabulary(context):
  ...     return vocabulary.CSVVocabulary(
  ...         os.path.join(os.path.dirname(__file__), 'sample.csv'),
  ...         messageFactory=_messageFactory)

Taht's all, let's call the vocabulary now:

  >>> vocab = sampleVocabulary(None)
  >>> len(vocab)
  6

  >>> for item in vocab:
  ...     print item.value, item.token, item.title
  tryoutApprenticeship tryoutApprenticeship sample-tryoutApprenticeship
  summerJob summerJob sample-summerJob
  internship internship sample-internship
  limitedJob limitedJob sample-limitedJob
  fulltimeJob fulltimeJob sample-fulltimeJob
  other other sample-other


LegacyVocabulary
----------------

First define our sample vocabulary:

  >>> from zope.schema.vocabulary import SimpleTerm
  >>> SampleLegacyVocabulary = vocabulary.LegacyVocabulary([
  ...     SimpleTerm('first', title='First Title'),
  ...     SimpleTerm('second', title='Second Title'),
  ...     ])

And we need to define a name:

  >>> SampleLegacyVocabulary.name = 'Sample Legacy Vocabulary'

Now we can define our legacy data vocabulary as adapter for our vocabulary:

  >>> SampleFallBackVocabulary = vocabulary.FallBackVocabulary([
  ...     SimpleTerm('missing', title='missing'),
  ...     ])

  >>> def getSampleFallBackVocabulary(context):
  ...     return SampleFallBackVocabulary

  >>> zope.component.provideAdapter(getSampleFallBackVocabulary,
  ...     (interfaces.ILegacyVocabulary,),
  ...     provides=interfaces.IFallBackVocabulary,
  ...     name='Sample Legacy Vocabulary')

Now we can use our sample vocabulary:
  
  >>> vocab = SampleLegacyVocabulary
  >>> len(vocab)
  2

  >>> for item in vocab:
  ...     print item.value, item.token
  first first
  second second

Now we can test the vocabulary API:

  >>> term = vocab.getTerm('second')
  >>> term.token
  'second'

  >>> term.value
  'second'

  >>> term.title
  'Second Title'

There is a fallback vocabulary which supports a token called ``missing``.
So let's try this in the defualt vocabulary none existent key:

  >>> term = vocab.getTerm('missing')
  >>> term.value
  'missing'

Now it comes to the interesting part. Let's call a value which doesn't exist.
We will get the default missing term defined in the vocabulary:

  >>> term = vocab.getTerm('nada')
  >>> term.value
  'missing'

We also can override the missing term:

  >>> from zope.schema.vocabulary import SimpleTerm
  >>> MISSING_TERM = SimpleTerm('foo', 'foo', 'Foo')
  >>> vocab.missingTerm = MISSING_TERM

  >>> term = vocab.getTerm('nada')
  >>> term.value
  'foo'
