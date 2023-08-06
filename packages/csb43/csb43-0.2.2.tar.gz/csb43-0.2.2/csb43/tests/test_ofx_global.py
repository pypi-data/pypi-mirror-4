
import unittest
import pycountry
import datetime

from csb43 import ofx

class TestOfxGlobal(unittest.TestCase):

    def test_getXMLTag(self):
        name = 'tag'
        content = '12345'

        self.assertEqual('<TAG>12345</TAG>', ofx.getXMLTag(name, content))

        content = None

        self.assertEqual('', ofx.getXMLTag(name, content))

        content = ''

        self.assertEqual('<TAG></TAG>', ofx.getXMLTag(name, content))

        with self.assertRaises(Exception):
            ofx.getXMLTag(None, content)

    def test_strDate(self):
        value = datetime.date(year=2004, month=3, day=1)

        self.assertEqual('20040301', ofx.strDate(value))

        value = None

        self.assertIsNone(ofx.strDate(value))

        value = 5

        with self.assertRaises(Exception):
            ofx.strDate(value)

    def test_strBool(self):
        value = True

        self.assertEqual('Y', ofx.strBool(value))

        value = False

        self.assertEqual('N', ofx.strBool(value))

        value = None

        self.assertIsNone(ofx.strBool(value))

        value = 5

        self.assertEqual('Y', ofx.strBool(value))

        value = ''

        self.assertEqual('N', ofx.strBool(value))

    def test_strCurrency(self):
        value = pycountry.currencies.get(letter='EUR')

        self.assertEqual('EUR', ofx.strCurrency(value))

        value = None

        self.assertIsNone(ofx.strCurrency(value))

        value = 5

        with self.assertRaises(Exception):
            ofx.strCurrency(value)

class TestOfxObject(unittest.TestCase):

    def test_init(self):

        with self.assertRaises(Exception):
            ofx.OfxObject()

        ofx.OfxObject(None)

        ofx.OfxObject('1234')

        ofx.OfxObject(5)

    def test_tag_name(self):
        value = 'tag1'

        o = ofx.OfxObject(value)

        self.assertEqual(value, o.get_tag_name())

        value = 'tag2'
        o.set_tag_name(value)

        self.assertEqual(value, o.get_tag_name())

    def test_str(self):

        o = ofx.OfxObject('tag')

        self.assertEqual('', str(o))
