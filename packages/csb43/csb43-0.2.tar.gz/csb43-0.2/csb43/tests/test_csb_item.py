
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

        with self.assertRaises(utils.Csb43Exception):
            self.item.recordCode = 23

        with self.assertRaises(utils.Csb43Exception):
            self.item.recordCode = '23'

        #with self.assertRaises(TypeError):
        self.item.recordCode = 5

        self.assertEqual(5, self.item.recordCode)

        self.item.recordCode = '05'

        self.assertEqual(5, self.item.recordCode)

    def test_item1(self):

        self.assertIsNone(self.item.item1)

        #with self.assertRaises(utils.Csb43Exception):
        value = '1235677744'
        self.item.item1 = value

        self.assertEqual(value.rstrip(' '), self.item.item1)

        value = '0123456789ABCDEF G '*2
        self.item.item1 = value

        self.assertEqual(value.rstrip(' '), self.item.item1)

    def test_item2(self):

        self.assertIsNone(self.item.item2)

        #with self.assertRaises(utils.Csb43Exception):
        value = '1235677744'
        self.item.item2 = value

        self.assertEqual(value.rstrip(' '), self.item.item2)

        value = '0123456789ABCDEF G '*2
        self.item.item2 = value

        self.assertEqual(value.rstrip(' '), self.item.item2)

    def test_str1(self):

        s = str(self.item)

        self.assertEqual(80, len(s))

        self.assertEqual('23', s[0:2])

    def test_str2(self):

        self.item.item1 = 'algo uno dos 1'
        self.item.item2 = 'dos 1 uno algo'
        self.item.recordCode = '05'

        s = str(self.item)

        e = item.Item(s, strict=True)

        self.assertEqual(self.item.item1, e.item1)
        self.assertEqual(self.item.item2, e.item2)
        self.assertEqual(self.item.recordCode, e.recordCode)

        self.assertEqual(str(e), s)

    def test_iter(self):

        self.test_str2()

        r = [x for x in self.item]

        self.assertEqual(1, len(r))

        self.assertEqual(str(self.item), r[0])

