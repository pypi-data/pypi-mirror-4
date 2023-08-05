# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from gocept.recordserialize import FixedWidthRecord


class BLZRecord(FixedWidthRecord):

    fields = [
        ('blz', 8, ' ', FixedWidthRecord.LEFT),
        ('type', 1, ' ', FixedWidthRecord.LEFT),
        ('name', 58, ' ', FixedWidthRecord.LEFT),
        ('zip', 5, ' ', FixedWidthRecord.LEFT),
        ('city', 35, ' ', FixedWidthRecord.LEFT),
        ('shortname', 27, ' ', FixedWidthRecord.LEFT),
        ('pan', 5, ' ', FixedWidthRecord.LEFT),
        ('bic', 11, ' ', FixedWidthRecord.LEFT),
        ('checksum_type', 2, ' ', FixedWidthRecord.LEFT),
        ('record_number', 6, ' ', FixedWidthRecord.LEFT),
        ('change_type', 1, ' ', FixedWidthRecord.LEFT),
        ('delete_type', 1, ' ', FixedWidthRecord.LEFT),
        ('next_blz', 8, ' ', FixedWidthRecord.LEFT),
    ]
    encoding = 'iso-8859-1'


def parse(filename):
    result = {}
    for record in BLZRecord.parse_file(open(filename, 'r')):
        if record['type'] == '1':
            result[record['blz']] = record.data
    return result
