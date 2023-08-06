
import unittest

from csb43.csb43 import ClosingFile, File, Account, Transaction, Item, Exchange
import csb43.utils as utils

class TestFile(unittest.TestCase):

    def setUp(self):
        self.t = File()

    def test_init(self):
        self.assertEqual([], self.t.accounts)

    def test_get_last_account(self):

        with self.assertRaises(IndexError):
            self.t.get_last_account()

        self.test_add_account1()

        self.assertIsInstance(self.t.get_last_account(), Account)

    def test_add_account1(self):

        a = Account()
        a.bankCode = '0'*4
        a.branchCode = '0'*4
        a.accountNumber = '0'*10
        a.initialBalance = 0

        self.t.add_account(str(a))

        self.assertEqual(str(a), str(self.t.get_last_account()))

    def test_add_account2(self):

        a = Account()
        a.bankCode = '0'*4
        a.branchCode = '0'*4
        a.accountNumber = '0'*10
        a.initialBalance = 0

        self.t.add_account(a)

        self.assertEqual(str(a), str(self.t.get_last_account()))

    def test_add_transaction(self):

        t = Transaction()
        t.amount = 3

        with self.assertRaises(IndexError):
            self.t.add_transaction(t)

        self.test_add_account1()

        self.t.add_transaction(t)

        self.assertIsInstance(self.t.get_last_account().get_last_transaction(), Transaction)

        self.t.add_transaction(str(t))

        self.assertIsInstance(self.t.get_last_account().get_last_transaction(), Transaction)

    def test_add_item(self):

        i = Item()
        i.recordCode = 1

        with self.assertRaises(IndexError):
            self.t.add_item(i)

        self.test_add_transaction()

        self.t.add_item(i)

        t = self.t.get_last_account().get_last_transaction()

        self.assertIsInstance(t.optionalItems[-1], Item)

        self.t.add_item(str(i))

        self.assertIsInstance(t.optionalItems[-1], Item)

    def test_add_exchange1(self):

        e = Exchange()

        with self.assertRaises(IndexError):
            self.t.add_exchange(e)

        self.test_add_transaction()

        self.t.add_exchange(e)

        t = self.t.get_last_account().get_last_transaction()

        self.assertIsInstance(t.exchange, Exchange)

        with self.assertRaises(utils.Csb43Exception):
            self.t.add_exchange(e)

    def test_add_exchange2(self):

        e = Exchange()

        with self.assertRaises(IndexError):
            self.t.add_exchange(str(e))

        self.test_add_transaction()

        self.t.add_exchange(str(e))

        t = self.t.get_last_account().get_last_transaction()

        self.assertIsInstance(t.exchange, Exchange)

        with self.assertRaises(utils.Csb43Exception):
            self.t.add_exchange(e)

    def test_close_file0(self):

        self.t.close_file()

    def test_close_file1(self):

        c = ClosingFile()
        c.totalRecords = 0

        self.t.close_file(str(c))

        self.assertEqual(0, self.t.abstract.totalRecords)

        self.t.close_file(c)

        self.assertEqual(0, self.t.abstract.totalRecords)

        self.t.close_file()

        self.assertEqual(0, self.t.abstract.totalRecords)

    def test_close_file2(self):

        c = ClosingFile()
        c.totalRecords = 3 # 1ac + 2 trans

        self.test_add_transaction()

        self.t.close_file(str(c))

        self.assertEqual(3, self.t.abstract.totalRecords)

    def test_close_file3(self):

        self.t.close_file()
        self.assertEqual(0, self.t.abstract.totalRecords)

        # +1 acc, +2 trans
        self.test_add_transaction()

        self.t.close_file()

        self.assertEqual(3, self.t.abstract.totalRecords)

    def test_close_file4(self):

        c = ClosingFile()
        c.totalRecords = 3

        self.test_add_transaction()

        self.t.close_file(str(c))

    def test_iter(self):

        l = [x for x in self.t]

        self.assertEqual(1, len(l))

        ClosingFile(str(l[0]))

        self.test_add_transaction()

        l = [x for x in self.t]

        self.assertEqual(4, len(l))

        Account(str(l[0]))

        Transaction(str(l[1]))

        Transaction(str(l[2]))

        ClosingFile(str(l[3]))

    def test_str(self):

        s = str(self.t).split('\n')

        ClosingFile(s[0])

        self.test_add_transaction()

        s = str(self.t).split('\n')

        for r in s:
            self.assertEqual(80, len(r))

        Account(s[0])

        Transaction(s[1])

        Transaction(s[2])

        ClosingFile(s[3])


class TestClosingFile(unittest.TestCase):

    def setUp(self):
        self.t = ClosingFile()

    def test_init(self):
        record = '88' + '9'*18 + '1'*60

        ClosingFile(record)

    def test_init_bad_length(self):
        record = '88' + '9'*18 + '1'*4

        with self.assertRaises(utils.Csb43Exception):
            ClosingFile(record)

    def test_init_bad_code(self):
        record = '89' + '9'*18 + '1'*60

        with self.assertRaises(utils.Csb43Exception):
            ClosingFile(record)

    def test_totalRecords(self):
        self.assertIsNone(self.t.totalRecords)

        value = 1234

        self.t.totalRecords = value
        self.assertEqual(1234, self.t.totalRecords)

        value = '1234'

        self.t.totalRecords = value
        self.assertEqual(1234, self.t.totalRecords)

        value = 'a123'

        with self.assertRaises(utils.Csb43Exception):
            self.t.totalRecords = value

        value = '12345678'

        with self.assertRaises(utils.Csb43Exception):
            self.t.totalRecords = value

    def test_padding(self):
        self.assertIsNone(self.t.padding)

        value = ' b '

        self.t.padding = value

        self.assertEqual(value, self.t.padding)

        value = ' b '*18

        self.t.padding = value

        self.assertEqual(value, self.t.padding)

        value = ' b '*18 + 'c'

        with self.assertRaises(utils.Csb43Exception):
            self.t.padding = value

    def test_str(self):
        res = str(self.t)

        self.assertIsInstance(res, basestring)

        self.assertEqual(80, len(res))
        self.assertEqual('88', res[0:2])

