# -*- coding: utf8 -*-
'''
@license: GNU Lesser General Public License v3.0 (see LICENSE)
'''

from csb43.utils import DECIMAL, raiseCsb43Exception, check_strict
from record import Record
import pycountry

import re


class Exchange(Record):
    '''
    Exchange record
    (es) registro de cambio de divisa (24)
    '''

    CUR_NUM = re.compile(r'^\d{3}$')
    CUR_LET = re.compile(r'^[a-zA-Z]{3}$')

    def __init__(self, record=None, strict=True, decimal=DECIMAL):
        '''
        Args:
            record (str)  -- csb record (defalt=None)
            strict (bool) -- treat warning as exceptions when *True*

        Raise:
            Csb43Exception
        '''
        super(Exchange, self).__init__(decimal=decimal)
        self.__strict = strict

        self.__originCurrency = None
        self.__amount = None
        self.__padding = None

        if record is not None:
            if not self.is_valid(record):
                raiseCsb43Exception('bad code of record', self.__strict)

            self._set_origin_currency_code(record[4:7], strict)
            self._set_amount(record[7:21], strict)
            self._set_padding(record[21:80], strict)

    def _get_origin_currency_code(self):
        return self.__originCurrency

    def _get_amount(self):
        return self.__amount

    def _get_padding(self):
        return self.__padding

    @check_strict(r'^\d{3}$')
    def _set_origin_currency_code(self, value, strict=True):
		self.__originCurrency = value

    @check_strict(r'^\d{14}$')
    def _set_amount(self, value, strict=True):
        self.__amount = value

    @check_strict(r'^.{59}$')
    def _set_padding(self, value, strict=True):
        self.__padding = value

    def is_valid(self, record):
        return isinstance(record, basestring)\
            and (22 <= len(record) <= 80) and (record[0:4] == '2401')

    def _set_external_amount(self, value):
        v = float(value)
        c = self._unformat_currency(v)
        self._set_amount("%014d" % c[0])

    def _get_external_amount(self):
        a = self._get_amount()
        if a is not None:
            return self._format_currency(self._get_amount(), debit='2')
        else:
            return None

    def _get_external_currency_code(self):
        try:
            return pycountry.currencies.get(numeric=self.__originCurrency)
        except KeyError:
            return None

    def _set_external_currency_code(self, value):
        try:
            if isinstance(value, pycountry.db.Data):
                self._set_origin_currency_code(str(value.numeric))
            else:
                import numbers
                if isinstance(value, numbers.Number):
                    val = "%03d" % value
                else:
                    val = str(value)
                obj = None
                if self.CUR_NUM.match(val):
                    obj = pycountry.currencies.get(numeric=val)
                elif self.CUR_LET.match(val):
                    obj = pycountry.currencies.get(letter=val.upper())
                else:
                    raiseCsb43Exception("""pycountry.Currencies object or a valid
                                        ISO 4217 code expected,
                                        but %s found""" % val, strict=True)
                if obj:
                    self._set_origin_currency_code(str(obj.numeric))
        except KeyError:
            raiseCsb43Exception("""pycountry.Currencies object or  a valid
                                ISO 4217 code expected,
                                but %s found""" % value, strict=True)

    sourceCurrency = property(_get_external_currency_code,
                              _set_external_currency_code, None,
                              """original currency
                              (es) divisa original""")
    amount = property(_get_external_amount, _set_external_amount, None,
                      """amount in the original currency
                      (es) cantidad en la divisa original""")
    padding = property(_get_padding, _set_padding, None, "padding")
