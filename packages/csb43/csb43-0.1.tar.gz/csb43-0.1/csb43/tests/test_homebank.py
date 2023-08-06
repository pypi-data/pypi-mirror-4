
import unittest

from csb43.homebank import transaction
from csb43.utils import utils
import datetime

class TestHomebankTransaction(unittest.TestCase):

	def setUp(self):
		self.tDate = datetime.date(2002,3,4)
		self.value = [self.tDate.strftime("%d-%m-%y"),'2','3','4','5','6.00']

	def test_init(self):
		try:
			transaction.Transaction()
		except utils.Csb43Exception:
			self.fail("exception not expected")

	def test_init_record(self):

		with self.assertRaises(utils.Csb43Exception):
			transaction.Transaction("1;2")

		with self.assertRaises(utils.Csb43Exception):
			transaction.Transaction(",".join(self.value))

		transaction.Transaction(";".join(self.value))

	def test_properties(self):
		t = transaction.Transaction(";".join(self.value))

		self.assertEqual(self.tDate.year, t.date.year)
		self.assertEqual(self.tDate.month, t.date.month)
		self.assertEqual(self.tDate.day, t.date.day)

		self.assertEqual(2, t.mode)
		self.assertEqual('3', t.info)
		self.assertEqual('4', t.payee)
		self.assertEqual('5', t.description)
		self.assertEqual(6, t.amount)
		self.assertIsNone(t.category)

		value = list(self.value)
		value.append('7')

		t = transaction.Transaction(";".join(value))

		self.assertEqual(self.tDate.year, t.date.year)
		self.assertEqual(self.tDate.month, t.date.month)
		self.assertEqual(self.tDate.day, t.date.day)

		self.assertEqual(2, t.mode)
		self.assertEqual('3', t.info)
		self.assertEqual('4', t.payee)
		self.assertEqual('5', t.description)
		self.assertEqual(6, t.amount)
		self.assertEqual('7', t.category)

		t.mode = '23'
		self.assertEqual(23, t.mode)
		t.mode = 23
		self.assertEqual(23, t.mode)

		t.info = '55'
		self.assertEqual('55', t.info)

		t.payee = 'payee'
		self.assertEqual('payee', t.payee)

		t.description = 'description'
		self.assertEqual('description', t.description)

		with self.assertRaises(ValueError):
			t.amount = 'amount'

		with self.assertRaises(utils.Csb43Exception):
			t.date = '43'

		try:
			t.date = self.tDate
		except:
			self.fail("exception not expected")

	def test_str(self):
		value = list(self.value)
		value.append('7')
		value = ";".join(value)

		t = transaction.Transaction(value)

		self.assertEqual(value, str(t))
