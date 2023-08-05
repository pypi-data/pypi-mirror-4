# coding: utf-8
# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from gocept.recordserialize import FixedWidthRecord
import unittest


class SimpleRecord(FixedWidthRecord):

    lineterminator = 'X'

    fields = [
        ('one', 5),
        ('two', 5),
        ('three', 5),
    ]


class FixedWidthRecordTest(unittest.TestCase):

    def test_assign_values_via_setitem_and_join_them_in_str(self):
        r = SimpleRecord()
        r['three'] = 3
        r['one'] = 1
        r['two'] = 2
        self.assertEqual('    1    2    3X', str(r))

    def test_values_shorter_than_length_are_padded(self):
        r = SimpleRecord()
        r['one'] = '1234'
        self.assertEqual(' 1234          X', str(r))

    def test_values_longer_than_length_are_truncated(self):
        r = SimpleRecord()
        r['one'] = '1234567890'
        self.assertEqual('12345          X', str(r))

    def test_fields_can_have_different_lengths(self):
        class Record(FixedWidthRecord):

            fields = [
                ('one', 1),
                ('two', 2),
                ('three', 3),
            ]
        r = Record()
        r['one'] = '1'
        r['two'] = '1'
        r['three'] = '1'
        self.assertEqual('1 1  1\r\n', str(r))

    def test_fields_can_have_different_fill_characters(self):
        class Record(FixedWidthRecord):

            fields = [
                ('one', 3, ' '),
                ('two', 3, '0'),
            ]
        r = Record()
        r['one'] = '1'
        r['two'] = '1'
        self.assertEqual('  1001\r\n', str(r))

    def test_fields_can_specify_fill_direction(self):
        from gocept.recordserialize.fixed import FixedWidthRecord

        class Record(FixedWidthRecord):

            fields = [
                ('one', 3, ' ', FixedWidthRecord.LEFT),
                ('two', 3, ' ', FixedWidthRecord.RIGHT),
            ]
        r = Record()
        r['one'] = '1'
        r['two'] = '1'
        self.assertEqual('1    1\r\n', str(r))

    def test_writes_with_specified_encoding(self):
        class Record(FixedWidthRecord):

            encoding = 'utf-8'

            fields = [
                ('one', 3, ' '),
            ]
        r = Record()
        r['one'] = u'föö'
        self.assertEqual('f\xc3\xb6\xc3\xb6\r\n', str(r))

    def test_reads_with_specified_encoding(self):
        class Record(FixedWidthRecord):

            encoding = 'utf-8'

            fields = [
                ('one', 3, ' '),
            ]
        r = Record.parse('f\xc3\xb6\xc3\xb6\r\n')
        self.assertEqual(u'föö', r['one'])

    def test_parse_reads_string_and_creates_records(self):
        from gocept.recordserialize.fixed import FixedWidthRecord

        class Record(FixedWidthRecord):

            fields = [
                ('one', 3, ' '),
                ('two', 5, '0', FixedWidthRecord.LEFT),
            ]

        r = Record.parse('  120000\r\n')
        self.assertEqual('1', r['one'])
        self.assertEqual('2', r['two'])
        r = Record.parse('  340000\r\n')
        self.assertEqual('3', r['one'])
        self.assertEqual('4', r['two'])
