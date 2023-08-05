# coding: utf-8
# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.recordserialize
import unittest


class BasicRecordTest(unittest.TestCase):

    def setUp(self):
        class MyRecord(gocept.recordserialize.SeparatedRecord):
            fields = 3

        self.record = MyRecord()

    def test_no_values_should_yield_empty_fields(self):
        self.assertEqual(';;\r\n', str(self.record))

    def test_records_should_be_one_based(self):
        self.assertRaises(KeyError, self.record.__getitem__, 0)

    def test_unassigned_fields_should_show_up_empty(self):
        self.record[1] = u'föö'
        self.record[3] = 'bar'
        self.assertEqual(u'föö;;bar\r\n', str(self.record).decode('utf-8'))

    def test_customize_properties(self):
        self.record.separator = '|'
        self.record.lineterminator = '#'
        self.record.encoding = 'cp1252'

        self.record[1] = u'föö'
        self.record[3] = 'bar'
        self.assertEqual(u'föö||bar#', str(self.record).decode('cp1252'))


class DeclarationTest(unittest.TestCase):

    def setUp(self):
        class MyRecord(gocept.recordserialize.SeparatedRecord):
            fields = 4
            lineterminator = ''

            first = 1
            default = 2, 'qux'
            maxlen = 3, 5
            maxlen_default = 4, 5, 'asdfg'

        self.record = MyRecord()

    def test_accessing_fields_by_name(self):
        self.record['first'] = 'foo'
        self.assertEqual('foo', self.record['first'])
        self.assertEqual('foo', self.record[1])

    def test_unassigned_fields_with_default_values(self):
        self.assertEqual(';qux;;asdfg', str(self.record))

    def test_values_should_be_truncated_to_maximum_length(self):
        self.record['maxlen'] = '1234567890'
        self.assertEqual(';qux;12345;asdfg', str(self.record))

    def test_key_names(self):
        self.assertEqual(['first', 'default', 'maxlen', 'maxlen_default'],
                         self.record.key_names)

    def test__str_key_names(self):
        self.assertEqual('first;default;maxlen;maxlen_default',
                         self.record._str_key_names())

    def test_method_on_record_class_does_not_break_init(self):
        # A method defined on the record class does not break the
        # instantiation.
        class MyRecordWithMethod(self.record.__class__):
            def hash(self):
                pass
        self.failUnless(MyRecordWithMethod())
