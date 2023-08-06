# -*- coding: utf-8 -*-
'''
.. note::

    license: GNU Lesser General Public License v3.0 (see LICENSE)
'''

from csb43.utils import check_strict, raiseCsb43Exception, DECIMAL, currencyISO, currencyISOByLetter, isCurrency
import csb43.utils.messages as msg
from csb43.i18n import tr as _
from transaction import Transaction
from record import Record

import re

_CUR_NUM = re.compile(r'^\d{3}$')
_CUR_LET = re.compile(r'^[a-zA-Z]{3}$')

class Account(Record):
    '''
    A Csb43 account / (es) Cuenta

    - Create an :class:`Account` object from a `CSB43` string record::

        >>> from csb43.csb43 import Account
        >>> a = Account(record)

    - From an empty object to a `CSB43` string record::

        >>> a = Account()
        >>> str(a)
        '11                  000000000000000000000000000000                              '
    '''

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
        super(Account, self).__init__(decimal=decimal, yearFirst=yearFirst)
        self.__transactions = []
        self.__strict = strict
        self.__closing = None

        self.__bankCode = None
        self.__officeCode = None
        self.__accountNumber = None
        self.__initialBalance = None
        self.__debitOrCredit = None
        self.__initialDate = None
        self.__finalDate = None
        self.__shortName = None
        self.__currencyCode = None
        self.__padding = None
        self.__informationMode = None

        if record is not None:
            if not Account.is_valid(record):
                raiseCsb43Exception(msg.BAD_RECORD(record), self.__strict)

            # base 1
            # clave de banco: 3-6, N
            self._set_bank_code(record[2:6], self.__strict)
            # clave de oficina: 7-10 N
            self._set_office_code(record[6:10], self.__strict)
            # num. de cuenta: 11-20
            self._set_account_number(record[10:20], self.__strict)
            # fecha inicial: 21-26
            self._set_initial_date(record[20:26], self.__strict)
            # fecha final: 27-32
            self._set_final_date(record[26:32], self.__strict)
            # debe o haber: 33-33
            self._set_expense_or_income(record[32:33], self.__strict)
            # saldo inicial: 34-47
            self._set_initial_balance(record[33:47], self.__strict)
            # clave divisa: 48-50
            self._set_currency_code(record[47:50], self.__strict)
            # modalidad de informacion: 51-51
            self._set_information_mode(record[50:51], self.__strict)
            # nombre abreviado
            self._set_short_name(record[51:77], self.__strict)
            # padding
            self._set_padding(record[77:80], self.__strict)

    @staticmethod
    def is_valid(record):
        return isinstance(record, basestring)\
            and (77 <= len(record) <= 80) and (record[0:2] == '11')

    # account number
    ##################
    def _get_account_number(self):
        return self.__accountNumber

    @check_strict(r'^[ \d]{10}$')
    def _set_account_number(self, value, strict=True):
        self.__accountNumber = value

    # bank code
    ##################
    def _get_bank_code(self):
        return self.__bankCode

    @check_strict(r'^\d{4}$')
    def _set_bank_code(self, value, strict=True):
        self.__bankCode = value

    # office code
    ##################
    def _get_office_code(self):
        return self.__officeCode

    @check_strict(r'^[ \d]{4}$')
    def _set_office_code(self, value, strict=True):
        self.__officeCode = value

    # currency code
    ######################
    def _get_currency_code(self):
        return self.__currencyCode

    def _get_external_currency_code(self):
        if self.__currencyCode is None:
            return None
        return currencyISO(self.__currencyCode)

    @check_strict(r'^[ \d]{3}$')
    def _set_currency_code(self, value, strict=True):
        self.__currencyCode = value

    def _set_external_currency_code(self, value):
        try:
            if isCurrency(value):
                self._set_currency_code(str(value.numeric))
            else:
                import numbers
                if isinstance(value, numbers.Number):
                    val = "%03d" % value
                else:
                    val = str(value)
                obj = None
                if _CUR_NUM.match(val):
                    obj = currencyISO(val)
                elif _CUR_LET.match(val):
                    obj = currencyISOByLetter(val.upper())
                else:
                    raiseCsb43Exception(msg.CURRENCY_EXPECTED(val), strict=True)
                if obj:
                    self._set_currency_code(str(obj.numeric))
        except KeyError:
            raiseCsb43Exception(msg.CURRENCY_EXPECTED(value), strict=True)

    # information mode
    #######################
    def _get_information_mode(self):
        return self.__informationMode

    @check_strict(r'^[ \d]$')
    def _set_information_mode(self, value, strict=True):
        self.__informationMode = value

    def _set_external_information_mode(self, value):
        self._set_information_mode(str(value))

    def _get_external_information_mode(self):
        if self.__informationMode is None:
            return None
        elif self.__informationMode == ' ':
            return None
        return int(self.__informationMode)

    # short name
    ####################
    def _get_short_name(self):
        return self.__shortName

    @check_strict(r'^[\w ]{26}$')
    def _set_short_name(self, value, strict=True):
        self.__shortName = value.rstrip(' ')

    def _set_external_short_name(self, value):
        self._set_short_name(str(value).ljust(26))

    # padding
    #############
    def _get_padding(self):
        return self.__padding

    @check_strict(r'^.{3}$')
    def _set_padding(self, value, strict=True):
        self.__padding = value

    # initial balance
    #####################
    def _get_initial_balance(self):
        return self.__initialBalance

    def _get_external_initial_balance(self):
        if self.__initialBalance is None:
            return None
        return self._format_currency(self.__initialBalance,
                                     self.__debitOrCredit)

    @check_strict(r'^\d{14}$')
    def _set_initial_balance(self, value, strict=True):
        self.__initialBalance = value

    def _set_external_initial_balance(self, value):
        c = self._unformat_currency(float(value))
        self._set_initial_balance('%014d' % c[0])
        self._set_expense_or_income(c[1])

    # debit or credit
    #####################
    def _get_expense_or_income(self):
        return self.__debitOrCredit

    @check_strict(r'^[12]$')
    def _set_expense_or_income(self, value, strict=True):
        self.__debitOrCredit = value

    # initial date
    ################
    def _get_initial_date(self):
        return self.__initialDate

    def _get_external_initial_date(self):
        if self.__initialDate is None:
            return None
        return self._format_date(self.__initialDate)

    @check_strict(r'^\d{6}$')
    def _set_initial_date(self, value, strict=True):
        self.__initialDate = value

    def _set_external_initial_date(self, value):
        self.__initialDate = self._unformat_date(value)

    # final date
    ###############
    def _get_final_date(self):
        return self.__finalDate

    def _get_external_final_date(self):
        if self.__finalDate is None:
            return None
        return self._format_date(self.__finalDate)

    @check_strict(r'^\d{6}$')
    def _set_final_date(self, value, strict=True):
        self.__finalDate = value

    def _set_external_final_date(self, value):
        self.__finalDate = self._unformat_date(value)

    # transactions
    ################
    def _get_transactions(self):
        return self.__transactions

    def get_last_transaction(self):
        '''
        :rtype: the last added :class:`Transaction`
        '''
        return self.__transactions[-1]

    def add_transaction(self, record):
        '''
        Add a new transaction to the account

        :param record: transaction record
        :type record: :class:`Transaction` or :class:`basestring`

        :raises: :class:`csb43.utils.Csb43Exception`
        '''

        if isinstance(record, Transaction):
            self.__transactions.append(record)
        else:
            self.__transactions.append(Transaction(record, self.__strict,
                                               decimal=self._decimal,
                                               yearFirst=self._yearFirst))

    def add_item(self, record):
        '''
        Add a new additional item record to the transaction

        :param record: item record
        :type record: :class:`Item` or :class:`basestring`

        :raises: :class:`csb43.utils.Csb43Exception` when the record is impossible to parse, or if the         maximum number of complementary items has been reached

        .. seealso::

            :func:`Transaction.add_item`
        '''
        self.get_last_transaction().add_item(record)

    def get_account_key(self):
        '''
        :rtype: :class:`int` two-digits checksum for the bank account / (es) digitos de control
        '''

        fixDigit = lambda x: 1 if x == 10 else x

        sumprod = lambda l1, l2: sum([int(x) * y for x, y in zip(l1, l2)])

        c1 = [7, 3, 6, 1]
        c2 = [2, 4, 8, 5]
        c3 = [10, 9, 7, 3, 6, 1, 2, 4, 8, 5]

        dig1 = fixDigit((sumprod(self.bankCode, c1) +
                         sumprod(self.branchCode, c2)) % 11)

        dig2 = fixDigit(sumprod(self.accountNumber, c3) % 11)

        return dig1 * 10 + dig2

    def close_account(self, record = None, update = False):
        '''
        Close the current account and generate an abstract object

        :param record: csb record
        :type record: :class:`ClosingAccount`, :class:`basestring` or `None`

        :param update: update the abstract if already present
        :type record: :class:`bool`

        :raises: :class:`csb43.utils.Csb43Exception` if invalid record of incongruent abstract
        '''

        if (self.__closing is not None) and not update:
            raiseCsb43Exception(_("trying to close an already closed account"),
                                self.__strict)

        def equal_f(a, bal):
            return abs(a - bal) < 10 ** (-self._decimal)

        balance = self.initialBalance or 0
        pBalance = 0
        nBalance = 0
        negRecords = 0
        posRecords = 0
        for t in self.__transactions:
            tAmount = t.amount
            balance += tAmount
            if tAmount >= 0:
                posRecords += 1
                pBalance += tAmount
            else:
                negRecords += 1
                nBalance += tAmount

        closing = None

        if isinstance(record, basestring):
            closing = ClosingAccount(record, self.__strict, decimal=self._decimal,
                                    yearFirst=self._yearFirst)
        elif isinstance(record, ClosingAccount):
            closing = record
        elif record is not None:
            raiseCsb43Exception(msg.INCOMPATIBLE_OBJECT(record, "ClosingAccount", "basestring"), True)

        if closing:
            rBalance = closing.balance
            rPBalance = closing.income
            rNBalance = -closing.expense
            rPositive = closing.incomeEntries
            rNegative = closing.expenseEntries

            if not equal_f(balance, rBalance):
                raiseCsb43Exception(_("balance (%1.2f) mismatch in closing account "
                                    "record (%1.2f)") %
                                    (balance, rBalance), self.__strict)
            if not equal_f(pBalance, rPBalance):
                raiseCsb43Exception(_("income amount (%1.2f) mismatch in closing "
                                    "account record (%1.2f)") %
                                    (pBalance, rPBalance), self.__strict)
            if not equal_f(nBalance, rNBalance):
                raiseCsb43Exception(_("expense amount (%1.2f) mismatch in closing "
                                    "account record (%1.2f)") %
                                    (nBalance, rNBalance), self.__strict)
            if posRecords != rPositive:
                raiseCsb43Exception(_("income entries (%d) mismatch in closing "
                                    "account record (%d)") %
                                    (posRecords, rPositive), self.__strict)
            if negRecords != rNegative:
                raiseCsb43Exception(_("expense entries (%d) mismatch in closing "
                                    "account record (%d)") %
                                    (negRecords, rNegative), self.__strict)
        else:
            closing = ClosingAccount(strict=self.__strict, decimal=self._decimal,
                                    yearFirst=self._yearFirst)
            closing.balance = balance
            closing.income = pBalance
            closing.expense = -nBalance
            closing.incomeEntries = posRecords
            closing.expenseEntries = negRecords
            if self.currency:
                closing.currency = self.currency
            if self.accountNumber:
                closing.accountNumber = self.accountNumber
            if self.bankCode:
                closing.bankCode = self.bankCode
            if self.branchCode:
                closing.branchCode = self.branchCode

        self.__closing = closing

    def is_closed(self):
        '''
        :rtype: :class:`bool` `True`  if this :class:`Account` has been properly closed
        '''
        return self.__closing is not None

    def _get_closing(self):
        return self.__closing

    def add_exchange(self, record, update=False):
        '''
        Add a new additional exchange record to the last added transaction

        :param record: csb exchange record or object
        :type record: :class:`Exchange` or :class:`basestring`

        :param update: update the current exchange object if it exists
        :type update: :class:`bool`

        :raises: :class:`csb43.utils.Csb43Exception`

        .. seealso::

            :func:`Transaction.add_exchange`

        '''
        self.get_last_transaction().add_exchange(record, update)

    # **** Properties ****
    transactions = property(_get_transactions, None, None,
                            ":class:`list` of transactions / (es) lista de movimientos")
    initialDate = property(_get_external_initial_date,
                           _set_external_initial_date, None,
                           "Start date of the period to which the information "
                           "corresponds / (es) fecha de comienzo del periodo al que "
                           "corresponde la informacion"
                           """

:rtype: :class:`datetime.datetime`

Setting a date::

    >>> a.initialDate = datetime.datetime(year=2012,month=2,day=13).date()
    >>> a.initialDate
    datetime.datetime(2012, 2, 13, 0, 0)

                         """)
    finalDate = property(_get_external_final_date, _set_external_final_date,
                         None,
                         "End date of the period to which the information "
                         "corresponds / (es) fecha de fin del periodo al que "
                         "corresponde la informacion"
                         """

:rtype: :class:`datetime.datetime`

Setting a date::

    >>> a.finalDate = datetime.datetime(year=2012,month=2,day=13).date()
    >>> a.finalDate
    datetime.datetime(2012, 2, 13, 0, 0)

                         """)
    initialBalance = property(_get_external_initial_balance,
                              _set_external_initial_balance, None,
                              "initial balance amount / "
                              "(es) montante del balance inicial"
                              """

Quantities can be assigned as numbers or strings, and they will be truncated to adjust the
decimal format set for the object::

    >>> a.initialBalance = 123
    >>> a.initialBalance
    123.0
    >>> a.initialBalance = 123.45
    >>> a.initialBalance
    123.45
    >>> a.initialBalance = '1234.56'
    >>> a.initialBalance
    1234.56
    >>> a.initialBalance = 1.2345
    >>> a.initialBalance
    1.23
                              """)
    currency = property(_get_external_currency_code,
                        _set_external_currency_code, None,
                        "currency object / "
                        "(es) objecto de divisa"
                        """

:rtype: :class:`pycountry.db.Currency`

`ISO 4217` codes can be assigned::

    >>> a.currency = 'USD'
    >>> a.currency.letter
    u'USD'
    >>> a.currency.numeric
    u'840'
    >>> a.currency = '978'
    >>> a.currency.letter
    u'EUR'
                        """)
    shortName = property(_get_short_name, _set_external_short_name, None,
                         "abbreviated name of the client / "
                         "(es) nombre abreviado del cliente"
                         """

:rtype: :class:`str`
                         """)
    padding = property(_get_padding, _set_padding, None,
                       "padding")
    accountNumber = property(_get_account_number, _set_account_number, None,
                             "account number / "
                             "(es) numero de cuenta"
                             """

:rtype: :class:`str`

>>> a.accountNumber = '0000000000'
>>> a.accountNumber
'0000000000'
                             """)
    bankCode = property(_get_bank_code, _set_bank_code, None,
                        "bank code / "
                        "(es) codigo de banco"
                        """

:rtype: :class:`str`

>>> a.bankCode = '0000'
>>> a.bankCode
'0000'
                        """)
    branchCode = property(_get_office_code, _set_office_code, None,
                          "branch code / "
                          "(es) codigo de sucursal u oficina"
                          """

:rtype: :class:`str`

>>> a.branchCode = '0000'
>>> a.branchCode
'0000'

                          """)
    abstract = property(_get_closing, None, None,
                        ":rtype: :class:`ClosingAccount` account abstract")

    informationMode = property(_get_external_information_mode, _set_external_information_mode, None,
                        "information mode / "
                        "(es) modalidad de informacion"
                        """

>>> a.informationMode = 1
>>> a.informationMode
1
>>> a.informationMode = '2'
>>> a.informationMode
2
                        """)

    def as_dict(self):
        '''
        :rtype: a representation of this object as a :class:`dict`. The keys will be localised
        '''

        d = {
            msg.T_INITIAL_DATE: str(self.initialDate.date()) if self.initialDate else None,
            msg.T_FINAL_DATE: str(self.finalDate.date()) if self.finalDate else None,
            msg.T_INITIAL_BALANCE: self.initialBalance,
            msg.T_CURRENCY: str(self.currency.letter) if self.currency else None,
            msg.T_SHORT_NAME: self.shortName,
            msg.T_ACCOUNT_NUMBER: self.accountNumber,
            msg.T_BANK_CODE: self.bankCode,
            msg.T_BRANCH_CODE: self.branchCode,
            msg.T_INFORMATION_MODE: self.informationMode,
        }

        if self.accountNumber:
            d[msg.T_ACCOUNT_KEY] = self.get_account_key()

        if len(self.transactions) > 0:
            d[_("transactions")] = [x.as_dict() for x in self.transactions]

        if self.abstract:
            d.update(self.abstract.as_dict())

        return d

    def __main_str(self):
        return "11{b_code: >4}{of_code: >4}{ac_num: >10}{in_date:0>6}{fin_date:0>6}{e_i:0>1}{bal:0>14}{cur:0>3}{info: >1}{nom: <26}{padding: <3}".format(
                b_code = self._get_bank_code() or '',
                of_code = self._get_office_code() or '',
                ac_num = self._get_account_number() or '',
                in_date = self._get_initial_date() or '',
                fin_date = self._get_final_date() or '',
                e_i = self._get_expense_or_income() or '',
                bal = self._get_initial_balance() or '',
                cur = self._get_currency_code() or '',
                info = self._get_information_mode() or '',
                nom = self._get_short_name() or '',
                padding = self._get_padding() or ''
            )

    def __iter__(self):
        ''':rtype: iterator of all the `CSB43` records that this object represents'''
        return _AccountIter(self, self.__main_str())

    def __str__(self):
        r''':rtype: representation of this object as `CSB43` records (using `\\n` as separator)'''
        return '\n'.join([x for x in self])


class _AccountIter(object):

    def __init__(self, ac, main_str):
        self.__output = [main_str]
        self.__output.extend(ac.transactions)
        if ac.abstract:
            self.__output.append(ac.abstract)

        self.__iter = iter(self.__output)
        self.__tran = None

    def next(self):
        if self.__tran:
            try:
                return self.__tran.next()
            except StopIteration:
                self.__tran = None
        now = self.__iter.next()

        if isinstance(now, Transaction):
            self.__tran = iter(now)
            return self.next()
        else:
            return str(now)


class ClosingAccount(Record):
    '''
    An Account abstact, given by a termination record
    '''

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
        super(ClosingAccount, self).__init__(decimal=decimal,
                                             yearFirst=yearFirst)
        self.__strict = strict

        self.__bankCode = None
        self.__officeCode = None
        self.__accountNumber = None
        self.__debitEntries = None
        self.__creditEntries = None
        self.__debitAmount = None
        self.__creditAmount = None
        self.__totalAmountCode = None
        self.__totalAmount = None
        self.__currencyCode = None
        self.__padding = None

        if record is not None:
            if not ClosingAccount.is_valid(record):
                raiseCsb43Exception(msg.BAD_RECORD(record), self.__strict)

            # base 1
            # clave de banco: 3-6, N
            self._set_bank_code(record[2:6], self.__strict)
            # clave de oficina: 7-10 N
            self._set_office_code(record[6:10], self.__strict)
            # num. de cuenta: 11-20
            self._set_account_number(record[10:20], self.__strict)
            # apuntes debe: 21-25, N
            self._set_expense_entries(record[20:25], self.__strict)
            # importes debe: 26-39, N
            self._set_expense_amount(record[25:39], self.__strict)
            # apuntes haber: 40-44 N
            self._set_income_entries(record[39:44], self.__strict)
            # importes haber: 45-58 N
            self._set_income_amount(record[44:58], self.__strict)
            # codigo saldo final 59-59 N
            self._set_total_balance_code(record[58:59], self.__strict)
            # saldo finak
            self._set_total_balance(record[59:73], self.__strict)
            # clave divisa
            self._set_currency_code(record[73:76], self.__strict)
            # libre
            self._set_padding(record[76:80], self.__strict)

    def _get_expense_entries(self):
        return self.__debitEntries

    def _get_external_expense_entries(self):
        if self.__debitEntries is None:
            return None
        return int(self.__debitEntries)

    def _set_external_expense_entries(self, value):
        self._set_expense_entries('%05d' % int(value))

    def _get_expense_amount(self):
        return self.__debitAmount

    def _get_external_expense_amount(self):
        if self.__debitAmount is None:
            return None
        return self._format_currency(self.__debitAmount)

    def _get_income_entries(self):
        return self.__creditEntries

    def _get_external_income_entries(self):
        if self.__creditEntries is None:
            return None
        return int(self.__creditEntries)

    def _set_external_income_entries(self, value):
        self._set_income_entries('%05d' % int(value))

    def _get_income_amount(self):
        return self.__creditAmount

    def _get_external_income_amount(self):
        if self.__creditAmount is None:
            return None
        return self._format_currency(self.__creditAmount)

    def _get_total_balance(self):
        return self.__totalAmount

    def _get_external_total_balance(self):
        if self.__totalAmount is None:
            return None
        return self._format_currency(self.__totalAmount,
                                     self.__totalAmountCode)

    def _get_total_balance_code(self):
        return self.__totalAmountCode

    def _get_currency_code(self):
        return self.__currencyCode

    def _get_external_currency_code(self):
        if self.__currencyCode is None:
            return None
        return currencyISO(self.__currencyCode)

    def _get_padding(self):
        return self.__padding

    @check_strict(r'^\d{5}$')
    def _set_expense_entries(self, value, strict=True):
        self.__debitEntries = value

    @check_strict(r'^\d{14}$')
    def _set_expense_amount(self, value, strict=True):
        self.__debitAmount = value

    def _set_external_expense_amount(self, value):
        c = self._unformat_currency(float(value))
        self._set_expense_amount("%014d" % c[0])

    @check_strict(r'^\d{5}$')
    def _set_income_entries(self, value, strict=True):
        self.__creditEntries = value

    @check_strict(r'^\d{14}$')
    def _set_income_amount(self, value, strict=True):
        self.__creditAmount = value

    def _set_external_income_amount(self, value):
        c = self._unformat_currency(float(value))
        self._set_income_amount("%014d" % c[0])

    @check_strict(r'^\d{14}$')
    def _set_total_balance(self, value, strict=True):
        self.__totalAmount = value

    def _set_external_total_balance(self, value):
        c = self._unformat_currency(float(value))
        self._set_total_balance("%014d" % c[0])
        self._set_total_balance_code(c[1])

    @check_strict(r'^[12]$')
    def _set_total_balance_code(self, value, strict=True):
        self.__totalAmountCode = value

    @check_strict(r'^\d{3}$')
    def _set_currency_code(self, value, strict=True):
        self.__currencyCode = value

    def _set_external_currency_code(self, value):
        try:
            if isCurrency(value):
                self._set_currency_code(str(value.numeric))
            else:
                import numbers
                if isinstance(value, numbers.Number):
                    val = "%03d" % value
                else:
                    val = str(value)
                obj = None
                if _CUR_NUM.match(val):
                    obj = currencyISO(val)
                elif _CUR_LET.match(val):
                    obj = currencyISOByLetter(val.upper())
                else:
                    raiseCsb43Exception(msg.CURRENCY_EXPECTED(val), strict=True)
                if obj:
                    self._set_currency_code(str(obj.numeric))
        except KeyError:
            raiseCsb43Exception(msg.CURRENCY_EXPECTED(value), strict=True)

    @check_strict(r'^.{4}$')
    def _set_padding(self, value, strict=True):
        self.__padding = value

    @staticmethod
    def is_valid(record):
        return isinstance(record, basestring) and\
            (76 <= len(record) <= 80) and (record[0:2] == '33')

    # account number
    ##################
    def _get_account_number(self):
        return self.__accountNumber

    @check_strict(r'^\d{10}$')
    def _set_account_number(self, value, strict=True):
        self.__accountNumber = value

    # bank code
    ##################
    def _get_bank_code(self):
        return self.__bankCode

    @check_strict(r'^\d{4}$')
    def _set_bank_code(self, value, strict=True):
        self.__bankCode = value

    # office code
    ##################
    def _get_office_code(self):
        return self.__officeCode

    @check_strict(r'^\d{4}$')
    def _set_office_code(self, value, strict=True):
        self.__officeCode = value


    def __str__(self):
        return "33{bank_code: >4}{of_code: >4}{ac_number: >10}{ex_num:0>5}{ex_am:0>14}{in_num:0>5}{in_am:0>14}{bal_code:0>1}{bal:0>14}{cur:0>3}{padding: >4}".format(
                bank_code = self._get_bank_code() or '',
                of_code = self._get_office_code() or '',
                ac_number = self._get_account_number() or '',
                ex_num = self._get_expense_entries() or '',
                ex_am = self._get_expense_amount() or '',
                in_num = self._get_income_entries() or '',
                in_am = self._get_income_amount() or '',
                bal_code = self._get_total_balance_code() or '',
                bal = self._get_total_balance() or '',
                cur = self._get_currency_code() or '',
                padding = self._get_padding() or ''
            )

    def as_dict(self):
        return {
            msg.T_EXPENSES_ENTRIES: self.expenseEntries,
            msg.T_INCOME_ENTRIES: self.incomeEntries,
            msg.T_EXPENSES: self.expense,
            msg.T_INCOME: self.income,
            msg.T_FINAL_BALANCE: self.balance
        }

    # **** Properties ****
    accountNumber = property(_get_account_number, _set_account_number, None,
                             """account number / (es) numero de cuenta""")
    bankCode = property(_get_bank_code, _set_bank_code, None,
                        """bank code / (es) codigo de banco""")
    branchCode = property(_get_office_code, _set_office_code, None,
                          """branch code / (es) codigo de sucursal u oficina""")
    expenseEntries = property(_get_external_expense_entries,
                              _set_external_expense_entries, None,
                              """number of debit entries / (es) numero de entradas en el debe""")
    expense = property(_get_external_expense_amount,
                       _set_external_expense_amount, None,
                       """total debit amounts / (es) montante total en el debe""")
    incomeEntries = property(_get_external_income_entries,
                             _set_external_income_entries, None,
                             """number of credit entries / (es) numero de entradas en el haber""")
    income = property(_get_external_income_amount,
                      _set_external_income_amount, None,
                      """total credit amounts / (es) montante total en el haber""")
    balance = property(_get_external_total_balance,
                       _set_external_total_balance, None,
                       """final balance / (es) balance final""")
    currency = property(_get_external_currency_code,
                        _set_external_currency_code, None,
                        """currency object (:class:`pycountry.db.Currency`) / (es) objecto de divisa""")
    padding = property(_get_padding, _set_padding, None, "padding")
