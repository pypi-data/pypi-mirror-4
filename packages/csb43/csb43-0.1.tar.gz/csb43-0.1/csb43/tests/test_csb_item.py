
import unittest

from csb43.csb43 import item
from csb43.utils import utils


class TestCsbItem(unittest.TestCase):

	def setUp(self):
		self.item = item.Item()

	def test_init(self):

		item.Item()

	def test_init_bad_length(self):

		record = '230001230405'

		with self.assertRaises(utils.Csb43Exception):
			item.Item(record)

	def test_init_bad_code(self):

		record = '22' + '0'*78

		with self.assertRaises(utils.Csb43Exception):
			item.Item(record)

	def test_init_bad_record_code(self):

		record = '2306' + '0'*76

		with self.assertRaises(utils.Csb43Exception):
			item.Item(record)

		record = '2315' + '0'*76

		with self.assertRaises(utils.Csb43Exception):
			item.Item(record)

		record = '2305' + '0'*76

		item.Item(record)

	def test_record_code(self):

		self.assertIsNone(self.item.recordCode)

		with self.assertRaises(TypeError):
			self.item.recordCode = 23

		with self.assertRaises(utils.Csb43Exception):
			self.item.recordCode = '23'

		with self.assertRaises(TypeError):
			self.item.recordCode = 5

		self.item.recordCode = '05'

		self.assertEqual('05', self.item.recordCode)

	def test_item1(self):

		self.assertIsNone(self.item.item1)

		with self.assertRaises(utils.Csb43Exception):
			self.item.item1 = '1235677744'

		value = '0123456789ABCDEF G '*2
		self.item.item1 = value

		self.assertEqual(value.rstrip(' '), self.item.item1)

	def test_item2(self):

		self.assertIsNone(self.item.item2)

		with self.assertRaises(utils.Csb43Exception):
			self.item.item2 = '1235677744'

		value = '0123456789ABCDEF G '*2
		self.item.item2 = value

		self.assertEqual(value.rstrip(' '), self.item.item2)
