# -*- coding: utf-8 -*-
'''
.. note::

    license: GNU Lesser General Public License v3.0 (see LICENSE)
'''

from csb43.utils import DECIMAL, raiseCsb43Exception, check_strict, currencyISO, currencyISOByLetter, isCurrency
import csb43.utils.messages as msg
#from csb43.i18n import tr as _
from record import Record

import re


class Exchange(Record):
    '''
    Exchange record / (es) registro de cambio de divisa (24)
    '''

    CUR_NUM = re.compile(r'^\d{3}$')
    CUR_LET = re.compile(r'^[a-zA-Z]{3}$')

    def __init__(self, record=None, strict=True, decimal=DECIMAL):
        '''
        :param record: csb record
        :type record: :class:`basestring` or `None`

        :param strict: treat warnings as exceptions when `True`
        :type strict: :class:`bool`

        :param decimal: number of digits to be considered as the decimal part in money
        :type decimal: :class:`int`

        :raises: :class:`csb43.utils.Csb43Exception`


        Create an :class:`Exchange` object from a `CSB43` string record::

            >>> from csb43.csb43 import Exchange
            >>> record = '{: <80}'.format('240197800000000012345')
            >>> e = Exchange(record)
            >>> print e.amount
            123.45
            >>> print e.sourceCurrency.letter
            EUR
            >>> print e.sourceCurrency.numeric
            978


        From an empty object to a `CSB43` string record::

            >>> from csb43.csb43 import Exchange
            >>> e = Exchange()
            >>> e.amount = 123.45
            >>> e.sourceCurrency = 'EUR'
            >>> print e
            240197800000000012345


        '''
        super(Exchange, self).__init__(decimal=decimal)
        self.__strict = strict

        self.__originCurrency = None
        self.__amount = None
        self.__padding = None

        if record is not None:
            if not self.is_valid(record):
                raiseCsb43Exception(msg.BAD_RECORD(record), self.__strict)

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
            return currencyISO(self.__originCurrency)
        except KeyError:
            return None

    def _set_external_currency_code(self, value):
        try:
            if isCurrency(value):
                self._set_origin_currency_code(str(value.numeric))
            else:
                import numbers
                if isinstance(value, numbers.Number):
                    val = "%03d" % value
                else:
                    val = str(value)
                obj = None
                if self.CUR_NUM.match(val):
                    obj = currencyISO(val)
                elif self.CUR_LET.match(val):
                    obj = currencyISOByLetter(val.upper())
                else:
                    raiseCsb43Exception(msg.CURRENCY_EXPECTED(val), strict=True)
                if obj:
                    self._set_origin_currency_code(str(obj.numeric))
        except KeyError:
            raiseCsb43Exception(msg.CURRENCY_EXPECTED(value), strict=True)

    def __str__(self):
        ':rtype: representation of this object as a `CSB43` record'
        return "2401{currency:0>3}{amount:0>14}{padding: <59}".format(
                currency = self.__originCurrency or '',
                amount = self.__amount or '',
                padding = self.__padding or ''
            )

    def __iter__(self):
        return iter([str(self)])

    def as_dict(self):
        '''
        :rtype: a representation of this object as a :class:`dict`. The keys will be localised

            >>> e.as_dict()
            {u'divisa_original': 'EUR', u'cantidad': 1.23}

        '''
        return {
            msg.T_ORIGINAL_CURRENCY: str(self.sourceCurrency.letter) if self.sourceCurrency else None,
            msg.T_AMOUNT: self.amount
        }

    sourceCurrency = property(_get_external_currency_code,
                            _set_external_currency_code, None,
                            """original currency / (es) divisa original

`ISO 4217` codes can be assigned::

    >>> e.sourceCurrency = 'USD'
    >>> e.sourceCurrency.letter
    u'USD'
    >>> e.sourceCurrency.numeric
    u'840'
    >>> e.sourceCurrency = '978'
    >>> e.sourceCurrency.letter
    u'EUR'


As well as a :class:`pycountry.db.Currency` object::

    >>> import pycountry
    >>> e.sourceCurrency = pycountry.currencies.get(letter='EUR')
    >>> e.sourceCurrency = pycountry.currencies.get(letter='USD')
    >>> e.sourceCurrency.letter
    u'USD'
    >>> type(e.sourceCurrency)
    <class 'pycountry.db.Currency'>

""")
    amount = property(_get_external_amount, _set_external_amount, None,
                    """amount in the original currency / (es) cantidad en la divisa original

Quantities can be assigned as numbers or strings, and they will be truncated to adjust the
decimal format set for the object::

    >>> e.amount = 123
    >>> e.amount
    123.0
    >>> e.amount = 123.45
    >>> e.amount
    123.45
    >>> e.amount = '1234.56'
    >>> e.amount
    1234.56
    >>> e.amount = 1.2345
    >>> e.amount
    1.23

""")
    padding = property(_get_padding, _set_padding, None, "padding")
