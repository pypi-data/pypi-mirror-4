
import unittest

from csb43.csb43 import Account, ClosingAccount, Exchange, Item, Transaction
from csb43.utils import utils
import pycountry
from datetime import datetime

class TestCsbAccount(unittest.TestCase):

    def setUp(self):
        self.t = Account()

    def test_init_bad_code(self):
        record = '12' + ('1'*78)

        self.assertEqual(80, len(record))

        with self.assertRaises(utils.Csb43Exception):
            Account(record)

    def test_init_bad_length(self):
        record = '1112380118008'

        with self.assertRaises(utils.Csb43Exception):
            Account(record)

    def test_init(self):
        record = '11' + ('1'*78)

        self.assertEqual(80, len(record))

        Account(record)

    def test_transactions(self):
        self.assertIsNotNone(self.t.transactions)
        self.assertIsInstance(self.t.transactions, list)
        self.assertEqual(len(self.t.transactions), 0)

    def test_initialDate(self):
        self.assertIsNone(self.t.initialDate)

        value = '230434'

        with self.assertRaises(utils.Csb43Exception):
            self.t.initialDate = value

        value = datetime(year=2004, month=3, day=1).date()

        self.t.initialDate = value

        self.assertEqual(2004, self.t.initialDate.year)
        self.assertEqual(3, self.t.initialDate.month)
        self.assertEqual(1, self.t.initialDate.day)

    def test_finalDate(self):
        self.assertIsNone(self.t.finalDate)

        value = '230434'

        with self.assertRaises(utils.Csb43Exception):
            self.t.finalDate = value

        value = datetime(year=2004, month=3, day=1).date()

        self.t.finalDate = value

        self.assertEqual(2004, self.t.finalDate.year)
        self.assertEqual(3, self.t.finalDate.month)
        self.assertEqual(1, self.t.finalDate.day)

    def test_initialBalance(self):
        self.assertIsNone(self.t.initialBalance)

        self.assertIsNone(self.t.initialBalance)

        value = '12345'*4

        with self.assertRaises(utils.Csb43Exception):
            self.t.initialBalance = value

        value = '12345'

        self.t.initialBalance = value
        self.assertEqual(12345, self.t.initialBalance)

        value = 123456

        self.t.initialBalance = value
        self.assertEqual(123456, self.t.initialBalance)

        value = 123456.876

        self.t.initialBalance = value
        self.assertEqual(123456.87, self.t.initialBalance)

        value = 'asdagsa'

        with self.assertRaises(ValueError):
            self.t.initialBalance = value

    def test_currency(self):
        self.assertIsNone(self.t.currency)

        with self.assertRaises(utils.Csb43Exception):
            self.t.currency = 3

        with self.assertRaises(utils.Csb43Exception):
            self.t.currency = 'asdfalsjk'

        self.t.currency = 978

        self.assertIsNotNone(self.t.currency)
        self.assertEqual('EUR', self.t.currency.letter)

        self.t.currency = 'usd'  # 840

        self.assertIsNotNone(self.t.currency)
        self.assertEqual('840', self.t.currency.numeric)

        self.t.currency = '978'

        self.assertIsNotNone(self.t.currency)
        self.assertEqual('EUR', self.t.currency.letter)

        self.t.currency = pycountry.currencies.get(numeric='840')

        self.assertIsNotNone(self.t.currency)
        self.assertEqual('USD', self.t.currency.letter)

    def test_shortName(self):
        self.assertIsNone(self.t.shortName)

        value = 'John Smith'

        self.t.shortName = value

        self.assertEqual(value, self.t.shortName)

        value = 'John Smith'*10

        with self.assertRaises(utils.Csb43Exception):
            self.t.shortName = value

    def test_accountNumber(self):
        self.assertIsNone(self.t.accountNumber)

        value = '0123456789'

        self.t.accountNumber = value
        self.assertEqual(value, self.t.accountNumber)

        value = 'a123456789'

        with self.assertRaises(utils.Csb43Exception):
            self.t.accountNumber = value

        value = '0123467'

        with self.assertRaises(utils.Csb43Exception):
            self.t.accountNumber = value

    def test_bankCode(self):
        self.assertIsNone(self.t.bankCode)

        value = '0123'

        self.t.bankCode = value
        self.assertEqual(value, self.t.bankCode)

        value = 'a123'

        with self.assertRaises(utils.Csb43Exception):
            self.t.bankCode = value

        value = '0123467'

        with self.assertRaises(utils.Csb43Exception):
            self.t.bankCode = value

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

    def test_abstract(self):
        self.assertIsNone(self.t.abstract)
        self.assertFalse(self.t.is_closed())
        # TODO

    def test_informationMode(self):
        self.assertIsNone(self.t.informationMode)

        value = '3'

        self.t.informationMode = value
        self.assertEqual(3, self.t.informationMode)

        value = 3

        self.t.informationMode = value
        self.assertEqual(3, self.t.informationMode)

        value = 'a'

        with self.assertRaises(utils.Csb43Exception):
            self.t.informationMode = value

        value = '12'

        with self.assertRaises(utils.Csb43Exception):
            self.t.informationMode = value

    def test_padding(self):
        self.assertIsNone(self.t.padding)

        value = 'sadl jasdf la'

        with self.assertRaises(utils.Csb43Exception):
            self.t.padding = value

        value = ' a '

        self.t.padding = value

        self.assertEqual(value, self.t.padding)

    def test_str(self):

        self.test_iter()

        s = str(self.t).split('\n')

        Account(s[0])
        Transaction(s[1])
        ClosingAccount(s[2])

    def test_iter(self):

        self.t.currency = 'EUR'
        self.t.bankCode = '0'*4
        self.t.branchCode = '0'*4
        self.t.accountNumber = '0'*10
        self.t.initialBalance = 0

        self.test_add_transaction1()

        l = [x for x in self.t]

        self.assertEqual(2, len(l))
        self.assertEqual('11', l[0][0:2])

        for x in l:
            self.assertEqual(80, len(x))

        Transaction(l[1])

        self.t.close_account()

        l = [x for x in self.t]

        self.assertEqual(3, len(l))
        self.assertEqual('11', l[0][0:2])

        for x in l:
            self.assertEqual(80, len(x))

        ClosingAccount(l[2])

    def test_add_item1(self):

        self.test_add_transaction1()

        i = Item()
        i.recordCode = 1
        i.item1 = 'a'
        i.item2 = 'b'

        self.t.add_item(str(i))

        self.assertEqual(str(i), str(self.t.get_last_transaction().optionalItems[-1]))

    def test_add_item2(self):

        self.test_add_transaction1()

        i = Item()
        i.recordCode = 1
        i.item1 = 'a'
        i.item2 = 'b'

        self.t.add_item(i)

        self.assertEqual(str(i), str(self.t.get_last_transaction().optionalItems[-1]))

    def test_add_exchange1(self):

        self.test_add_transaction1()

        e = Exchange()
        e.amount = 12345.5
        e.sourceCurrency = 'EUR'

        self.t.add_exchange(str(e))

        exchange = self.t.get_last_transaction().exchange

        self.assertIsInstance(exchange, Exchange)

        self.assertEqual(str(e), str(exchange))

    def test_add_exchange2(self):

        self.test_add_transaction2()

        e = Exchange()
        e.amount = 12345.5
        e.sourceCurrency = 'EUR'

        self.t.add_exchange(e)

        exchange = self.t.get_last_transaction().exchange

        self.assertIsInstance(exchange, Exchange)

        self.assertEqual(str(e), str(exchange))

    @staticmethod
    def _create_valid_transaction():
        t = Transaction()
        t.branchCode = '0'*4
        t.transactionDate = datetime.now()
        t.valueDate = datetime.now()
        t.commonItem = '00'
        t.ownItem = '000'
        t.amount = 123.00
        t.documentNumber = '0'

        return t

    def test_add_transaction1(self):
        t = self._create_valid_transaction()

        self.t.add_transaction(t)

        self.assertEqual(str(t), str(self.t.get_last_transaction()))

    def test_add_transaction2(self):
        t = self._create_valid_transaction()

        self.t.add_transaction(str(t))

        self.assertEqual(str(t), str(self.t.get_last_transaction()))


class TestCsbClosingAccount(unittest.TestCase):
    '''ClosingAccount'''

    def setUp(self):
        self.t = ClosingAccount()

    def test_init_bad_length(self):
        record = '33012380118008'

        with self.assertRaises(utils.Csb43Exception):
            ClosingAccount(record)

    def test_init_bad_code(self):
        record = '34' + ('1'*55)
        record += '0'*23

        self.assertEqual(80, len(record))

        with self.assertRaises(utils.Csb43Exception):
            ClosingAccount(record)

    def test_init(self):
        record = '33' + ('1'*78)

        ClosingAccount(record)

    def test_balance(self):

        self.assertIsNone(self.t.balance)

        self.assertIsNone(self.t.balance)

        value = '12345'*4

        with self.assertRaises(utils.Csb43Exception):
            self.t.balance = value

        value = '12345'

        self.t.balance = value
        self.assertEqual(12345, self.t.balance)

        value = 123456

        self.t.balance = value
        self.assertEqual(123456, self.t.balance)

        value = 123456.876

        self.t.balance = value
        self.assertEqual(123456.87, self.t.balance)

        value = 'asdagsa'

        with self.assertRaises(ValueError):
            self.t.balance = value

    def test_accountNumber(self):
        self.assertIsNone(self.t.accountNumber)

        value = '0123456789'

        self.t.accountNumber = value
        self.assertEqual(value, self.t.accountNumber)

        value = 'a123456789'

        with self.assertRaises(utils.Csb43Exception):
            self.t.accountNumber = value

        value = '0123467'

        with self.assertRaises(utils.Csb43Exception):
            self.t.accountNumber = value

    def test_bankCode(self):
        self.assertIsNone(self.t.bankCode)

        value = '0123'

        self.t.bankCode = value
        self.assertEqual(value, self.t.bankCode)

        value = 'a123'

        with self.assertRaises(utils.Csb43Exception):
            self.t.bankCode = value

        value = '0123467'

        with self.assertRaises(utils.Csb43Exception):
            self.t.bankCode = value

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

    def test_expenseEntries(self):

        self.assertIsNone(self.t.expenseEntries)

        self.assertIsNone(self.t.expenseEntries)

        value = '12345'*4

        with self.assertRaises(utils.Csb43Exception):
            self.t.expenseEntries = value

        value = '12345'

        self.t.expenseEntries = value
        self.assertEqual(12345, self.t.expenseEntries)

        value = 1234

        self.t.expenseEntries = value
        self.assertEqual(1234, self.t.expenseEntries)

        value = 123456.876

        with self.assertRaises(utils.Csb43Exception):
            self.t.expenseEntries = value

        value = 'asdagsa'

        with self.assertRaises(ValueError):
            self.t.expenseEntries = value

    def test_expense(self):
        self.assertIsNone(self.t.expense)

        value = '12345'*4

        with self.assertRaises(utils.Csb43Exception):
            self.t.expense = value

        value = '12345'

        self.t.expense = value
        self.assertEqual(12345, self.t.expense)

        value = 123456

        self.t.expense = value
        self.assertEqual(123456, self.t.expense)

        value = 123456.876

        self.t.expense = value
        self.assertEqual(123456.87, self.t.expense)

        value = 'asdagsa'

        with self.assertRaises(ValueError):
            self.t.expense = value

    def test_incomeEntries(self):

        self.assertIsNone(self.t.incomeEntries)

        self.assertIsNone(self.t.incomeEntries)

        value = '12345'*4

        with self.assertRaises(utils.Csb43Exception):
            self.t.incomeEntries = value

        value = '12345'

        self.t.incomeEntries = value
        self.assertEqual(12345, self.t.incomeEntries)

        value = 1234

        self.t.incomeEntries = value
        self.assertEqual(1234, self.t.incomeEntries)

        value = 123456.876

        with self.assertRaises(utils.Csb43Exception):
            self.t.incomeEntries = value

        value = 'asdagsa'

        with self.assertRaises(ValueError):
            self.t.incomeEntries = value

    def test_income(self):
        self.assertIsNone(self.t.income)

        value = '12345'*4

        with self.assertRaises(utils.Csb43Exception):
            self.t.income = value

        value = '12345'

        self.t.income = value
        self.assertEqual(12345, self.t.income)

        value = 123456

        self.t.income = value
        self.assertEqual(123456, self.t.income)

        value = 123456.876

        self.t.income = value
        self.assertEqual(123456.87, self.t.income)

        value = 'asdagsa'

        with self.assertRaises(ValueError):
            self.t.income = value

    def test_currency(self):

        self.assertIsNone(self.t.currency)

        with self.assertRaises(utils.Csb43Exception):
            self.t.currency = 3

        with self.assertRaises(utils.Csb43Exception):
            self.t.currency = 'asdfalsjk'

        self.t.currency = 978

        self.assertIsNotNone(self.t.currency)
        self.assertEqual('EUR', self.t.currency.letter)

        self.t.currency = 'usd'  # 840

        self.assertIsNotNone(self.t.currency)
        self.assertEqual('840', self.t.currency.numeric)

        self.t.currency = '978'

        self.assertIsNotNone(self.t.currency)
        self.assertEqual('EUR', self.t.currency.letter)

        self.t.currency = pycountry.currencies.get(numeric='840')

        self.assertIsNotNone(self.t.currency)
        self.assertEqual('USD', self.t.currency.letter)

    def test_padding(self):

        self.assertIsNone(self.t.padding)

        value = "asdga shfadsas"

        with self.assertRaises(utils.Csb43Exception):
            self.t.padding = value

        value = " a c"

        self.t.padding = value

        self.assertEqual(value, self.t.padding)

    def test_str(self):

        s = str(self.t)

        self.assertIsInstance(s, basestring)
        self.assertEqual(len(s), 80)

        self.assertEqual('33', s[0:2])

