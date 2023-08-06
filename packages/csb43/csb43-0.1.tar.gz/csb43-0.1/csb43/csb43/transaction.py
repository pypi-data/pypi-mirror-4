# -*- coding: utf8 -*-
'''
@license: GNU Lesser General Public License v3.0 (see LICENSE)
'''

from csb43.utils import DECIMAL, raiseCsb43Exception, check_strict
from item import Item
from record import Record
from exchange import Exchange


class Transaction(Record):
    '''
    A Csb43 transaction

    (es) Movimiento
    '''

    MAX_ITEMS = 5

    def __init__(self, record=None, strict=True, decimal=DECIMAL,
                 yearFirst=True):
        '''
        Args:
            record (str)     -- csb record (defalt=None)
            strict (bool)    -- treat warning as exceptions when *True*
            decimal (int)    -- decimal positions to consider
            yearFirst (bool) -- switch between YYMMD [True] and DDMMYY
                                [False] date formats

        Raise:
            Csb43Exception
        '''
        super(Transaction, self).__init__(decimal=decimal, yearFirst=yearFirst)
        self.__items = []
        self.__exchange = None
        self.__strict = strict

        if record is not None:
            if not Transaction.is_valid(record):
                raiseCsb43Exception('bad code of record', self.__strict)

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

    def add_exchange(self, record):
        '''
        Add a new additional exchange record to the transaction

        Args:
            record (str) -- csb record

        Raise:
            Csb43Exception  if :record: is not valid
        '''
        exchange = Exchange(record, decimal=self._decimal,
                            strict=self.__strict)
        if self.__exchange is not None:
            raiseCsb43Exception("""maximum number of exchange record
                                reached (1)""", self.__strict)
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
        return self.__documentNumber

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

    @staticmethod
    def _validate_reference(value, strict):
        n = value.strip(' ')
        try:
            long(n)
            control = int(n[-1])
            res = (sum([int(x) * ((i % 8) + 2) for (i, x)
                        in enumerate(reversed(n[:-1]))]) % 11) % 10

            if res != control:
                raiseCsb43Exception("Validation failed for reference '%s'"
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
        if len(self.__items) == Transaction.MAX_ITEMS:
            raiseCsb43Exception("""the maximum number of complementary items
                                for transaction has been reached: %d""" %
                                Transaction.MAX_ITEMS, self.__strict)
        if isinstance(record, basestring):
            self.__items.append(Item(record, self.__strict))
        elif isinstance(record, Item):
            self.__items.append(record)
        else:
            raiseCsb43Exception("Incompatible object", True)

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

    # **** Properties ****
    optionalItems = property(_get_items, None, None,
                             """list of optional items
                             (es) lista de conceptos adicionales""")
    padding = property(_get_padding, _set_padding, None, "padding")
    branchCode = property(_get_office_code, _set_office_code, None,
                          """branch code
                          (es) código de sucursal u oficina""")
    transactionDate = property(_get_external_operation_date,
                               _set_external_operation_date, None,
                               """transaction date
                               (es) fecha de la operación""")
    valueDate = property(_get_external_effective_date,
                         _set_external_effective_date, None,
                         """value date
                         (es) fecha valor""")
    sharedItem = property(_get_common_item, _set_external_common_item, None,
                          """inter-bank shared item
                          (es) concepto común""")
    ownItem = property(_get_own_item, _set_external_own_item, None,
                       """own item (given by each bank to its transactions)
                       (es) concepto propio del banco""")
    amount = property(_get_external_amount, _set_external_amount, None,
                      """amount of the transaction
                      (es) cantidad implicada en el movimiento""")
    documentNumber = property(_get_document_number, _set_document_number, None,
                              """document number
                              (es) número del documento""")
    reference1 = property(_get_reference_1, _set_reference_1, None,
                          """first reference (checksummed)
                          (es) primera referencia (verificada)""")
    reference2 = property(_get_reference_2, _set_reference_2, None,
                          """second reference (not checksummed)
                          (es) segunda referencia (no verificada)""")
    exchange = property(_get_exchange, _set_exchange, None,
                        """(Exchange) exchange object, or None
                        (es) objecto de cambio de divisa (Exchange)""")
