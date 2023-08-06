# -*- coding: utf-8 -*-
'''
.. note::

    license: GNU Lesser General Public License v3.0 (see LICENSE)
'''

from csb43.utils import DECIMAL, raiseCsb43Exception, check_strict
import csb43.utils.messages as msg
from csb43.i18n import tr as _
from item import Item
from record import Record
from exchange import Exchange


class Transaction(Record):
    '''
    A Csb43 transaction / (es) Movimiento

    - Create a :class:`Transaction` object from a `CSB43` string record::

        >>> from csb43.csb43 import Transaction
        >>> t = Transaction(record)

    - From an empty object to a `CSB43` string record::

        >>> t = Transaction()
        >>> t.amount = 123.45
        >>> str(t)
        '22    0000000000000000000002000000000123450000000000000000000000                '
    '''

    MAX_ITEMS = 5

    def __init__(self, record=None, strict=True, decimal=DECIMAL,
                yearFirst=True):
        '''
        :param record: csb record
        :type record: :class:`basestring` or `None`

        :param strict: treat warnings as exceptions when `True`
        :type strict: :class:`bool`

        :param decimal: number of digits to be considered as the decimal part in money
        :type decimal: :class:`int`

        :param yearFirst: switch between YYMMD [`True`] and DDMMYY [`False`] date formats
        :type yearFirst: :class:`bool`

        :raises: :class:`csb43.utils.Csb43Exception`

        '''
        super(Transaction, self).__init__(decimal=decimal, yearFirst=yearFirst)
        self.__items = []
        self.__exchange = None
        self.__strict = strict

        if record is not None:
            if not Transaction.is_valid(record):
                raiseCsb43Exception(msg.BAD_RECORD(record), self.__strict)

            # base 1
            # libre 3-6 -
            self._set_padding(record[2:6], self.__strict)
            # clave oficina origen 7-10 N
            self._set_office_code(record[6:10], self.__strict)
            # operation date
            self._set_operation_date(record[10:16], self.__strict)
            # effective date
            self._set_effective_date(record[16:22], self.__strict)
            # concepto comun
            self._set_common_item(record[22:24], self.__strict)
            # concepto propio
            self._set_own_item(record[24:27], self.__strict)
            # debe o haber
            self._set_expense_or_income(record[27:28], self.__strict)
            # importe
            self._set_amount(record[28:42], self.__strict)
            # num. de documento
            self._set_document_number(record[42:52], self.__strict)
            # referencia 1
            self._set_reference_1(record[52:64], self.__strict)
            # referencia 2
            self._set_reference_2(record[64:80], self.__strict)

        else:
            self.__padding = None
            self.__officeCode = None
            self.__operation_date = None
            self.__effective_date = None
            self.__commonItem = None
            self.__ownItem = None
            self.__debitOrCredit = None
            self.__amount = None
            self.__documentNumber = None
            self.__reference1 = None
            self.__reference2 = None

    def _get_exchange(self):
        return self.__exchange

    def _set_exchange(self, value):
        self.__exchange = value

    def add_exchange(self, record, update = False):
        '''
        Add a new additional exchange record to the transaction

        :param record: csb exchange record or object
        :type record: :class:`Exchange` or :class:`basestring`

        :param update: update the current exchange object if it exists
        :type update: :class:`bool`

        :raises: :class:`csb43.utils.Csb43Exception`

        Add an exchange object from a `CSB43` string record::

            >>> from csb43.csb43 import Exchange
            >>> record = '{: <80}'.format('240197800000000012345')
            >>> t.add_exchange(record)
            >>> str(t.exchange)
            '240197800000000012345                                                           '

        Add an exchange object from a :class:`Exchange`::

            >>> from csb43.csb43 import Exchange
            >>> e = Exchange()
            >>> e.amount = 123.45
            >>> e.sourceCurrency = 'EUR'
            >>> t.add_exchange(e)
            >>> str(t.exchange)
            '240197800000000012345                                                           '

        '''
        if isinstance(record, basestring):
            exchange = Exchange(record, decimal=self._decimal,
                                strict=self.__strict)
        elif isinstance(record, Exchange):
            exchange = record
        else:
            raiseCsb43Exception(msg.INCOMPATIBLE_OBJECT(record, "Exchange", "basestring"), True)

        if (self.__exchange is not None) and not update:
            raiseCsb43Exception(_("maximum number of exchange record"
                                " reached (%s)") % 1, self.__strict)
        self.__exchange = exchange

    @staticmethod
    def is_valid(record):
        return isinstance(record, basestring) and\
            (len(record) == 80) and (record[0:2] == '22')

    def _get_expense_or_income(self):
        return self.__debitOrCredit

    def _get_amount(self):
        return self.__amount

    def _get_document_number(self):
        if self.__documentNumber is None:
            return None
        return int(self.__documentNumber)

    def _get_reference_1(self):
        return self.__reference1

    def _get_reference_2(self):
        return self.__reference2

    # debit or credit
    @check_strict(r'^[12]$')
    def _set_expense_or_income(self, value, strict=True):
        self.__debitOrCredit = value

    @check_strict(r'^\d{14}$')
    def _set_amount(self, value, strict=True):
        self.__amount = value

    @check_strict(r'^\d{10}$')
    def _set_document_number(self, value, strict=True):
        self.__documentNumber = value

    def _set_external_document_number(self, value):
        self._set_document_number('{:0>10}'.format(value))

    @staticmethod
    def _validate_reference(value, strict):
        n = value.strip(' ')
        try:
            long(n)
            control = int(n[-1])
            res = (sum([int(x) * ((i % 8) + 2) for (i, x)
                        in enumerate(reversed(n[:-1]))]) % 11) % 10

            if res != control:
                raiseCsb43Exception(_("Validation failed for reference '%s'")
                                    % value, strict)

            return n
        except ValueError:
            return n

    @check_strict(r'^\d{12}$')
    def _set_reference_1(self, value, strict=True):
        self.__reference1 = Transaction._validate_reference(value, strict)

    @check_strict(r'^[ \w]{16}$')
    def _set_reference_2(self, value, strict=True):
        self.__reference2 = value.rstrip(' ')

    # items
    ############
    def _get_items(self):
        return self.__items

    # padding
    ############
    def _get_padding(self):
        return self.__padding

    @check_strict(r'^.{4}$')
    def _set_padding(self, value, strict=True):
        self.__padding = value

    # office code
    ################
    def _get_office_code(self):
        return self.__officeCode

    @check_strict(r'^\d{4}$')
    def _set_office_code(self, value, strict=True):
        self.__officeCode = value

    # operation date
    ################
    def _get_operation_date(self):
        return self.__operation_date

    def _get_external_operation_date(self):
        if self.__operation_date is None:
            return None
        return self._format_date(self.__operation_date)

    @check_strict(r'^\d{6}$')
    def _set_operation_date(self, value, strict=True):
        self.__operation_date = value

    def _set_external_operation_date(self, value):
        self.__operation_date = self._unformat_date(value)

    # effective date
    ################
    def _get_effective_date(self):
        return self.__effective_date

    def _get_external_effective_date(self):
        if self.__effective_date is None:
            return None
        return self._format_date(self.__effective_date)

    @check_strict(r'^\d{6}$')
    def _set_effective_date(self, value, strict=True):
        self.__effective_date = value

    def _set_external_effective_date(self, value):
        self.__effective_date = self._unformat_date(value)

    # common item
    ################
    def _get_common_item(self):
        return self.__commonItem

    @check_strict(r'^\d{2}$')
    def _set_common_item(self, value, strict=True):
        self.__commonItem = value

    def _set_external_common_item(self, value):
        if isinstance(value, basestring):
            self._set_common_item(value)
        else:
            v = int(value)
            self._set_common_item('%02d' % v)

    # own item
    ################
    def _get_own_item(self):
        return self.__ownItem

    @check_strict(r'^\d{3}$')
    def _set_own_item(self, value, strict=True):
        self.__ownItem = value

    def _set_external_own_item(self, value):
        if isinstance(value, basestring):
            self._set_own_item(value)
        else:
            v = int(value)
            self._set_own_item('%03d' % v)

    def add_item(self, record):
        '''
        Add a new optional item to the transaction.

        :param record: item record
        :type record: :class:`Item` or :class:`basestring`

        :raises: :class:`csb43.utils.Csb43Exception` when the record is impossible to parse, or if the         maximum number of complementary items has been reached
        '''
        if len(self.__items) == Transaction.MAX_ITEMS:
            raiseCsb43Exception(_("the maximum number of complementary items"
                                " for transaction has been reached: %d") %
                                Transaction.MAX_ITEMS, self.__strict)
        if isinstance(record, basestring):
            self.__items.append(Item(record, self.__strict))
        elif isinstance(record, Item):
            self.__items.append(record)
        else:
            raiseCsb43Exception(msg.INCOMPATIBLE_OBJECT(record, "Item", "basestring"), True)

    def _set_external_amount(self, value):
        v = float(value)
        c = self._unformat_currency(v)
        self._set_amount("%014d" % c[0])
        self._set_expense_or_income(c[1])

    def _get_external_amount(self):
        if self.__amount is None:
            return None
        return self._format_currency(self.__amount,
                                    debit=self.__debitOrCredit)

    def __str_main_record(self):
        ':rtype: representation of this object as a `CSB43` record'
        return "22{padding: <4}{of_code:0>4}{op_date:0>6}{ef_date:0>6}{common_item:0>2}{own_item:0>3}{ex_in:1>1}{amount:0>14}{doc_number:0>10}{ref1:0>12}{ref2: <16}".format(
                padding = self.__padding or '',
                of_code = self.__officeCode or '',
                op_date = self.__operation_date or '',
                ef_date = self.__effective_date or '',
                common_item = self.__commonItem or '',
                own_item = self.__ownItem or '',
                ex_in = self.__debitOrCredit or '',
                amount = self.__amount or '',
                doc_number = self.__documentNumber or '',
                ref1 = self.__reference1 or '',
                ref2 = self.__reference2 or ''
            )

    def __iter__(self):
        ''':rtype: iterator of all the `CSB43` records that this object represents

>>> [x for x in t]
['22    0000000000120213000002000000001234560000000000012345678900       something', '2301first item record                                                           ', '2302second item record                                                          ', '240184000000000012300                                                           ']

        '''
        return _TransactionIter(self, self.__str_main_record())

    def __str__(self):
        r''':rtype: representation of this object as `CSB43` records (using `\\n` as separator)

>>> str(t)
'22    0000000000120213000002000000001234560000000000012345678900       something\n2301first item record                                                           \n2302second item record                                                          \n240184000000000012300                                                           '
        '''
        return '\n'.join([x for x in self])

    def as_dict(self):
        '''
        :rtype: a representation of this object as a :class:`dict`. The keys will be localised

            >>> t.as_dict()
            {u'cantidad': 123.45, u'primera_referencia': None, u'segunda_referencia': None, u'concepto_propio': None, u'fecha_de_operacion': None, u'numero_del_documento': None, u'codigo_de_sucursal': None, u'concepto_comun': None, u'fecha_valor': None}
        '''
        d = {
            msg.T_BRANCH_CODE: self.branchCode,
            msg.T_TRANSACTION_DATE: str(self.transactionDate.date()) if self.transactionDate else None,
            msg.T_VALUE_DATE: str(self.valueDate.date()) if self.valueDate else None,
            msg.T_SHARED_ITEM: self.sharedItem,
            msg.T_OWN_ITEM: self.ownItem,
            msg.T_AMOUNT: self.amount,
            msg.T_DOCUMENT_NUMBER: self.documentNumber,
            msg.T_REFERENCE_1: self.reference1,
            msg.T_REFERENCE_2: self.reference2,
        }

        if len(self.optionalItems):
            d[msg.T_OPTIONAL_ITEMS] = [x.as_dict() for x in self.optionalItems]

        if self.exchange:
            d[msg.T_EXCHANGE] = self.exchange.as_dict()

        return d

    # **** Properties ****
    optionalItems = property(_get_items, None, None,
                            """list of optional items / (es) lista de conceptos adicionales

:rtype: :class:`list` of :class:`Item` attached to this transaction
""")
    padding = property(_get_padding, _set_padding, None, "padding")
    branchCode = property(_get_office_code, _set_office_code, None,
                        """branch code / (es) código de sucursal u oficina

:rtype: :class:`str`

>>> t.branchCode = '0000'
>>> t.branchCode
'0000'

""")
    transactionDate = property(_get_external_operation_date,
                            _set_external_operation_date, None,
                            """transaction date / (es) fecha de la operación

:rtype: :class:`datetime.datetime`

Setting a date::

    >>> t.transactionDate = datetime.datetime(year=2012,month=2,day=13).date()
    >>> t.transactionDate
    datetime.datetime(2012, 2, 13, 0, 0)

""")
    valueDate = property(_get_external_effective_date,
                        _set_external_effective_date, None,
                        """value date / (es) fecha valor

:rtype: :class:`datetime.datetime`

Setting a date::

    >>> t.valueDate = datetime.datetime(year=2012,month=2,day=13).date()
    >>> t.valueDate
    datetime.datetime(2012, 2, 13, 0, 0)

""")
    sharedItem = property(_get_common_item, _set_external_common_item, None,
                        """inter-bank shared item / (es) concepto común

:rtype: :class:`str`

>>> t.sharedItem = 12
>>> t.sharedItem
'12'
>>> t.sharedItem = '04'
>>> t.sharedItem
'04'
>>> from csb43.csb43 import utils
>>> utils.CONCEPTOS[t.sharedItem]
'GIROS - TRANSFERENCIAS - TRASPASOS - CHEQUES'

""")
    ownItem = property(_get_own_item, _set_external_own_item, None,
                    """own item (given by each bank to its transactions) / (es) concepto propio del banco

:rtype: :class:`str`

>>> t.ownItem = 123
>>> t.ownItem
'123'
>>> t.ownItem = '125'
>>> t.ownItem
'125'

""")
    amount = property(_get_external_amount, _set_external_amount, None,
                    """amount of the transaction / (es) cantidad implicada en el movimiento

:rtype: :class:`float`

Quantities can be assigned as numbers or strings, and they will be truncated to adjust the
decimal format set for the object::

    >>> t.amount = 123
    >>> t.amount
    123.0
    >>> t.amount = 123.45
    >>> t.amount
    123.45
    >>> t.amount = '1234.56'
    >>> t.amount
    1234.56
    >>> t.amount = 1.2345
    >>> t.amount
    1.23

""")
    documentNumber = property(_get_document_number, _set_external_document_number, None,
                            """document number / (es) número del documento

:rtype: :class:`int`

>>> t.documentNumber = 1
>>> t.documentNumber
1

                            """)
    reference1 = property(_get_reference_1, _set_reference_1, None,
                        """first reference (checksummed) / (es) primera referencia (verificada)

:rtype: :class:`str`

>>> t.reference1 = '012345678900'
>>> t.reference1
'012345678900'
>>> try:
...     t.reference1 = '012345678901'
... except Exception, e:
...     print e
...
Validación fallida para el campo de referencia '012345678901'

                        """)
    reference2 = property(_get_reference_2, _set_reference_2, None,
                        """second reference (not checksummed) / (es) segunda referencia (no verificada)

:rtype: :class:`str`

>>> t.reference2 = '{: >16}'.format('something')
>>> t.reference2
'       something'

""")
    exchange = property(_get_exchange, _set_exchange, None,
                        """exchange object / (es) objecto de cambio de divisa

:rtype: :class:`Exchange`

""")


class _TransactionIter(object):

    def __init__(self, trans, mainRecord):
        self.__output = [mainRecord]
        self.__output.extend(trans.optionalItems)
        if trans.exchange:
            self.__output.append(trans.exchange)

        self.__iter = iter(self.__output)

    def next(self):
        return str(self.__iter.next())

