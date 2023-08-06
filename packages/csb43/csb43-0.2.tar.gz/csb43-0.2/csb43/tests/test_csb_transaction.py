
import unittest
import datetime

from csb43.csb43 import Transaction, Item, Exchange
from csb43.utils import utils

class TestCsbTransaction(unittest.TestCase):

    def setUp(self):
        self.t = Transaction()

    def test_init_bad_length(self):
        record = '22011023402150'

        with self.assertRaises(utils.Csb43Exception):
            Transaction(record)

    def test_init_bad_code(self):
        record = '25' + ('1'*78)

        with self.assertRaises(utils.Csb43Exception):
            Transaction(record)

    def test_init(self):
        record = '22' + ('0'*25)
        record += '1'
        record += ('0'*52)

        Transaction(record)

    def test_amount(self):

        self.assertIsNone(self.t.amount)

        self.assertIsNone(self.t.amount)

        value = '12345'*4

        with self.assertRaises(utils.Csb43Exception):
            self.t.amount = value

        value = '12345'

        self.t.amount = value
        self.assertEqual(12345, self.t.amount)

        value = 123456

        self.t.amount = value
        self.assertEqual(123456, self.t.amount)

        value = 123456.876

        self.t.amount = value
        self.assertEqual(123456.87, self.t.amount)

        value = 'asdagsa'

        with self.assertRaises(ValueError):
            self.t.amount = value

    def test_branchCode(self):
        self.assertIsNone(self.t.branchCode)

        value = '1234'

        self.t.branchCode = value
        self.assertEqual(value, self.t.branchCode)

        value = '123b'

        with self.assertRaises(utils.Csb43Exception):
            self.t.branchCode = value

        value = 1234

        with self.assertRaises(TypeError):
            self.t.branchCode = value

        value = '123'

        with self.assertRaises(utils.Csb43Exception):
            self.t.branchCode = value

    def test_documentNumber(self):
        self.assertIsNone(self.t.documentNumber)

        value = '0123456789'

        self.t.documentNumber = value
        self.assertEqual(int(value), self.t.documentNumber)

        value = 'a123456789'

        with self.assertRaises(utils.Csb43Exception):
            self.t.documentNumber = value

        value = '0123467'

        #with self.assertRaises(utils.Csb43Exception):
        self.t.documentNumber = value
        self.assertEqual(int(value), self.t.documentNumber)

    def test_exchange(self):
        self.assertIsNone(self.t.exchange)

        value = '2401978' + '0'*(14+59)
        self.t.add_exchange(value)

        self.assertIsInstance(self.t.exchange, Exchange)
        self.assertEqual('EUR', self.t.exchange.sourceCurrency.letter)

    def test_optionalItems(self):
        #self.assertIsInstance(self.t.optionalItems, list)
        self.assertListEqual([], self.t.optionalItems)

        value = Item()
        self.t.add_item(value)

        self.assertListEqual([value], self.t.optionalItems)

        value = '2305' + '0'*76
        self.t.add_item(value)

        self.assertEqual(2, len(self.t.optionalItems))

        for n in xrange(3):
            self.t.add_item(Item())

        self.assertEqual(5, len(self.t.optionalItems))

        with self.assertRaises(utils.Csb43Exception):
            self.t.add_item(Item())

    def test_ownItem(self):

        self.assertIsNone(self.t.ownItem)


        self.assertIsNone(self.t.sharedItem)

        value = 'asd'

        with self.assertRaises(utils.Csb43Exception):
            self.t.sharedItem = value

        value = 123

        self.t.ownItem = value

        self.assertEqual('123', self.t.ownItem)

        value = '025'

        self.t.ownItem = value

        self.assertEqual('025', self.t.ownItem)

        value = 3

        self.t.ownItem = value

        self.assertEqual('003', self.t.ownItem)

        value = 1234

        with self.assertRaises(utils.Csb43Exception):
            self.t.ownItem = value

        value = '1256'

        with self.assertRaises(utils.Csb43Exception):
            self.t.ownItem = value

    def test_reference1(self):

        self.assertIsNone(self.t.reference1)

        value = '0123456789ab'

        with self.assertRaises(utils.Csb43Exception):
            self.t.reference1 = value

        value = ' 1234       '

        with self.assertRaises(utils.Csb43Exception):
            self.t.reference1 = value

        value = '0123456789abc'

        with self.assertRaises(utils.Csb43Exception):
            self.t.reference1 = value

        value = '012345678900'
        self.t.reference1 = value

        self.assertEqual(value, self.t.reference1)

    def test_reference2(self):

        self.assertIsNone(self.t.reference2)

        value = '0123456789ab0123'
        self.t.reference2 = value

        self.assertEqual(value, self.t.reference2)

        value = ' 12341234       '
        self.t.reference2 = value

        self.assertEqual(' 12341234', self.t.reference2)

        value = '0123456789abc'

        with self.assertRaises(utils.Csb43Exception):
            self.t.reference2 = value

    def test_sharedItem(self):

        self.assertIsNone(self.t.sharedItem)

        value = 'asd'

        with self.assertRaises(utils.Csb43Exception):
            self.t.sharedItem = value

        value = 23

        self.t.sharedItem = value

        self.assertEqual('23', self.t.sharedItem)

        value = '25'

        self.t.sharedItem = value

        self.assertEqual('25', self.t.sharedItem)

        value = 3

        self.t.sharedItem = value

        self.assertEqual('03', self.t.sharedItem)

        value = 123

        with self.assertRaises(utils.Csb43Exception):
            self.t.sharedItem = value

        value = '125'

        with self.assertRaises(utils.Csb43Exception):
            self.t.sharedItem = value

    def test_transactionDate(self):

        self.assertIsNone(self.t.transactionDate)

        d = datetime.date(2002, 3, 4)

        self.t.transactionDate = d

        self.assertEqual(2002, self.t.transactionDate.year)
        self.assertEqual(3, self.t.transactionDate.month)
        self.assertEqual(4, self.t.transactionDate.day)

    def test_valueDate(self):

        self.assertIsNone(self.t.valueDate)

        d = datetime.date(2002, 3, 4)

        self.t.valueDate = d

        self.assertEqual(2002, self.t.valueDate.year)
        self.assertEqual(3, self.t.valueDate.month)
        self.assertEqual(4, self.t.valueDate.day)

    def test_add_exchange1(self):

        e = Exchange()
        e.amount = 12345.5
        e.sourceCurrency = 'EUR'

        self.t.add_exchange(str(e))

        self.assertIsInstance(self.t.exchange, Exchange)

        self.assertEqual(e.amount, self.t.exchange.amount)
        self.assertEqual(e.sourceCurrency.letter, self.t.exchange.sourceCurrency.letter)

    def test_add_exchange2(self):

        e = Exchange()
        e.amount = 12345.5
        e.sourceCurrency = 'EUR'

        self.t.add_exchange(e)

        self.assertIsInstance(self.t.exchange, Exchange)

        self.assertEqual(e.amount, self.t.exchange.amount)
        self.assertEqual(e.sourceCurrency.letter, self.t.exchange.sourceCurrency.letter)

    def test_iter(self):

        l = [x for x in self.t]

        self.assertEqual(1, len(l))
        self.assertEqual('22', l[0][0:2])
        for x in l:
            self.assertEqual(80, len(x))

        self.test_add_exchange2()

        l = [x for x in self.t]
        self.assertEqual(2, len(l))
        self.assertEqual('22', l[0][0:2])
        for x in l:
            self.assertEqual(80, len(x))

        self.assertEqual(l[1], str(self.t.exchange))

    def test_str(self):

        self.test_iter()

        l = str(self.t).split('\n')

        li = [x for x in self.t]

        self.assertEqual(l[0], li[0])
        self.assertEqual(l[1], li[1])
