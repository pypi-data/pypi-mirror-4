import unittest

from csb43.utils import utils

class TestUtils(unittest.TestCase):

	def test_currency2raw(self):
		value = -123.456

		self.assertEqual(2, utils.DECIMAL)

		gotten = utils.currency2raw(value)

		self.assertIsNotNone(gotten)
		self.assertIsInstance(gotten, tuple, "returned value is tuple")
		self.assertEqual(2, len(gotten))

		self.assertEqual(12345, gotten[0], "third decimal is truncated")
		self.assertEqual('1', gotten[1], "marked as debit")

		value = 1234.56

		gotten = utils.currency2raw(value)

		self.assertEqual(123456, gotten[0], "no decimal is truncated")
		self.assertEqual('2', gotten[1], "marked as credit")

	def test_raw2currency(self):
		value = "123456"
		tag = "1"

		gotten = utils.raw2currency(value, debit=tag)

		self.assertEqual(-1234.56, gotten)

		tag = "2"

		gotten = utils.raw2currency(value, debit=tag)

		self.assertEqual(1234.56, gotten)

		value = 123456

		self.assertEqual(1234.56, gotten)

	def test_check_string(self):

		strict = False

		pattern = r"^[12]$"

		field = "13"

		try:
			utils.check_string(pattern, field, strict)
		except utils.Csb43Exception:
			self.fail("exception has been raised")

		strict = True

		with self.assertRaises(utils.Csb43Exception):
			utils.check_string(pattern, field, strict)

		field = "1"
		try:
			utils.check_string(pattern, field, strict)
		except utils.Csb43Exception:
			self.fail("exception has been raised")

	def test_currencyISO(self):

		numeric = '978'
		self.assertEqual('EUR', utils.currencyISO(numeric).letter)

	def test_raw2date(self):
		value = "020304"

		gotten = utils.raw2date(value)

		self.assertEqual(2002, gotten.year)
		self.assertEqual(3, gotten.month)
		self.assertEqual(4, gotten.day)

		gotten = utils.raw2date(value, yearFirst=False)

		self.assertEqual(2004, gotten.year)
		self.assertEqual(3, gotten.month)
		self.assertEqual(2, gotten.day)

	def test_date2raw(self):

		import datetime
		value = datetime.date(2002, 3, 4)

		gotten = utils.date2raw(value)

		self.assertEqual("020304", gotten)

		gotten = utils.date2raw(value, yearFirst = False)

		self.assertEqual("040302", gotten)




