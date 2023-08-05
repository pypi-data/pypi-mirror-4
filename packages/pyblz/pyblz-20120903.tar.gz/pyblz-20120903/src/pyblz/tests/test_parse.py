# coding: utf-8
# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import pyblz
import unittest


class Parse(unittest.TestCase):

    maxDiff = None

    def test_allocates_field_widths_correctly(self):
        self.assertEqual(dict(
            blz=u'64150020',
            type=u'1',
            name=u'Kreissparkasse Tübingen',
            zip=u'72008',
            city=u'Tübingen',
            shortname=u'Kr Spk Tübingen',
            pan=u'56008',
            bic=u'SOLADES1TUB',
            checksum_type=u'01',
            record_number=u'002683',
            change_type=u'U',
            delete_type=u'0',
            next_blz=u'00000000'
        ), pyblz.bank_data()['64150020'])
