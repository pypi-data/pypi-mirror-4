
import unittest
import pycountry

from csb43.csb43 import Exchange
from csb43.utils import utils

class TestCsbExchange(unittest.TestCase):

    def setUp(self):
        self.exch = Exchange()

    def test_init(self):

        Exchange()

    def test_init_bad_length(self):
        record = '24011023402150'

        with self.assertRaises(utils.Csb43Exception):
            Exchange(record)

    def test_init_bad_code(self):
        record = '2501' + ('1'*76)

        with self.assertRaises(utils.Csb43Exception):
            Exchange(record)

    def test_init_record(self):
        record = '2401'
        record += '840' # currency code
        record += '14'*7 # amount
        record += '1' * 59

        try:
            e = Exchange(record)

            self.assertEqual('USD', e.sourceCurrency.letter)
            self.assertEqual(141414141414.14, e.amount)

        except utils.Csb43Exception:
            self.fail("exception not expected")

    def test_sourceCurrency(self):

        self.assertIsNone(self.exch.sourceCurrency)

        with self.assertRaises(utils.Csb43Exception):
            self.exch.sourceCurrency = 3

        with self.assertRaises(utils.Csb43Exception):
            self.exch.sourceCurrency = 'asdfalsjk'

        self.exch.sourceCurrency = 978

        self.assertIsNotNone(self.exch.sourceCurrency)
        self.assertEqual('EUR', self.exch.sourceCurrency.letter)

        self.exch.sourceCurrency = 'usd' # 840

        self.assertIsNotNone(self.exch.sourceCurrency)
        self.assertEqual('840', self.exch.sourceCurrency.numeric)

        self.exch.sourceCurrency = '978'

        self.assertIsNotNone(self.exch.sourceCurrency)
        self.assertEqual('EUR', self.exch.sourceCurrency.letter)

        self.exch.sourceCurrency = pycountry.currencies.get(numeric='840')

        self.assertIsNotNone(self.exch.sourceCurrency)
        self.assertEqual('USD', self.exch.sourceCurrency.letter)

    def test_amount(self):

        self.assertIsNone(self.exch.amount)

        value = '12345'*4

        with self.assertRaises(utils.Csb43Exception):
            self.exch.amount = value

        value = '12345'

        self.exch.amount = value
        self.assertEqual(12345, self.exch.amount)

        value = 123456

        self.exch.amount = value
        self.assertEqual(123456, self.exch.amount)

        value = 123456.876

        self.exch.amount = value
        self.assertEqual(123456.87, self.exch.amount)

        value = 'asdagsa'

        with self.assertRaises(ValueError):
            self.exch.amount = value


    def test_padding(self):

        self.assertIsNone(self.exch.padding)

        value = "asdga shfadsas"

        with self.assertRaises(utils.Csb43Exception):
            self.exch.padding = value

        value = "0"*9 + (" a c " * 10)

        self.exch.padding = value

        self.assertEqual(value, self.exch.padding)

    def test_str1(self):

        s = str(self.exch)

        self.assertEqual(80, len(s))

        self.assertEqual('2401', s[0:4])

    def test_str2(self, exch = None):

        exch = exch or self.exch

        exch.amount = 12345.678

        exch.sourceCurrency = 'EUR'

        s = str(exch)

        e = Exchange(str(exch), strict=True, decimal=2)

        self.assertEqual(u'EUR', e.sourceCurrency.letter)
        self.assertEqual(12345.67, e.amount)

        self.assertEqual(str(e), s)

    def test_iter(self):

        self.test_str2()

        r = [x for x in self.exch]

        self.assertEqual(1, len(r))

        self.assertEqual(str(self.exch), r[0])


