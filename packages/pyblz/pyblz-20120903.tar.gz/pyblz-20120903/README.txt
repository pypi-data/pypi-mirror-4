======================
The pyblz distribution
======================

Wrapper around the BLZ data from the Deutsche Bundesbank:
http://www.bundesbank.de/Redaktion/DE/Standardartikel/Kerngeschaeftsfelder/Unbarer_Zahlungsverkehr/bankleitzahlen_download.html

(The currently packaged file version is ``BLZ_20120903.txt``.)

This package provides a dict of the bank information, keyed by BLZ.

    >>> import pyblz
    >>> banks = pyblz.bank_data()
    >>> len(banks)
    4098
    >>> banks['64150020']
    {'bic': u'SOLADES1TUB',
     'blz': u'64150020',
     'change_type': u'U',
     'checksum_type': u'01',
     'city': u'T\xfcbingen',
     'delete_type': u'0',
     'name': u'Kreissparkasse T\xfcbingen',
     'next_blz': u'00000000',
     'pan': u'56008',
     'record_number': u'002683',
     'shortname': u'Kr Spk T\xfcbingen',
     'type': u'1',
     'zip': u'72008'}

In case this package is not kept up to date, you can parse a different file:

    >>> import pyblz.parse
    >>> banks = pyblz.parse.parse('another-file.txt')
