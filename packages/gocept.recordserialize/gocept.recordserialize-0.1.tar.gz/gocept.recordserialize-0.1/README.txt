=======================================
The gocept.recordserialize distribution
=======================================

File writer/parser for fixed-width and character-separated files.

This package is compatible with Python version 2.7.


Fixed-width format
==================

Define the format by listing all fields, in order. Each field has the following
settings:

:name: Name of the field (required)
:width: Width of the field in characters (required)
:fill character: default: Space
:alignment: default: align LEFT (that is, pad on the right side)

For example::

   >>> from gocept.recordserialize import FixedWidthRecord
   >>> class FixedExample(FixedWidthRecord):
   ...
   ...    encoding = 'utf-8'
   ...    lineterminator = '\r\n'
   ...
   ...    fields = [
   ...        ('one', 3, ' ', FixedWidthRecord.LEFT),
   ...        ('two', 7, '0', FixedWidthRecord.RIGHT),
   ...    ]


Writing
-------

   >>> r = FixedExample()
   >>> r['one'] = 'foo'
   >>> r['two'] = '12'
   >>> str(r)
   'foo0000012\r\n'

Reading
-------

    >>> r = FixedExample.parse('bar0000034\r\n')
    >>> r['one']
    u'bar'
    >>> r['two']
    u'34'

Also available: ``parse_file`` which takes a file-like object.


Character-separated format
==========================

Define the format by declaring attributes on the class. Each field has the
following settings:

:position: position of the field
:default: default value to write if none is given
:maximum length: truncate field to this length

Note that you do not have to declare all fields, any positions not declared are
filled with empty columns. For this reason, you always have to give the total
number of fields in the ``fields`` attribute::

    >>> from gocept.recordserialize import SeparatedRecord
    >>> class PipeExample(SeparatedRecord):
    ...
    ...    fields = 5
    ...    encoding = 'utf-8'
    ...    separator = '|'
    ...    lineterminator = '\r\n'
    ...
    ...    first = 1
    ...    default = 2, 'qux'
    ...    maxlen = 3, 3
    ...    maxlen_default = 4, 5, 'asdfg'


Writing
-------

    >>> r = PipeExample()
    >>> r['first'] = 'some text'
    >>> r['maxlen'] = '12345'
    >>> str(r)
    'some text|qux|123|asdfg|\r\n'

Reading
-------

    >>> r = PipeExample.parse('some text|qux|123|asdfg|\r\n')
    >>> r['first']
    u'some text'
    >>> r['default']
    u'qux'
    >>> r['maxlen']
    u'123'
    >>> r['maxlen_default']
    u'asdfg'

Also available: ``parse_file`` which takes a file-like object.

Escaping
--------

For subclassing, SeparatedRecord provides classmethods ``escape`` and
``unescape`` that each value is passed through on write/read. An example that
makes use of this is ``gocept.recordserialize.CSVRecord`` which escapes quotes::

  >>> from gocept.recordserialize import CSVRecord
  >>> class CSVExample(CSVRecord):
  ...
  ...     fields = 1
  ...     one = 1

  >>> r = CSVExample()
  >>> r['one'] = 'my "quoted" string'
  >>> str(r)
  '"my \'quoted\' string"\r\n'

