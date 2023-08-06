# -*- coding: utf8 -*-
'''
@license: GNU Lesser General Public License v3.0 (see LICENSE)
'''

from csb43.utils import check_strict, raiseCsb43Exception, DECIMAL
from transaction import Transaction
from record import Record
import pycountry


class Account(Record):
    '''
    A Csb43 account
    
    (es) Cuenta
    '''

    def __init__(self, record=None, strict=True, decimal=DECIMAL,
                 yearFirst=True):
        '''
        Args:
            record (str)     -- csb record (defalt=None)
            strict (bool)    -- treat warning as exceptions when *True*
            decimal (int)    -- decimal positions to consider
            yearFirst (bool) -- switch between YYMMD [*True*] and DDMMYY
                                [*False*] date formats

        Raise:
            Csb43Exception   when the record does not match the specs
        '''
        super(Account, self).__init__(decimal=decimal, yearFirst=yearFirst)
        self.__transactions = []
        self.__strict = strict
        self.__closing = None

        if record is not None:
            if not Account.is_valid(record):
                raiseCsb43Exception('bad code of record', self.__strict)

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

    @check_strict(r'[ \d]{10}')
    def _set_account_number(self, value, strict=True):
        self.__accountNumber = value

    # bank code
    ##################
    def _get_bank_code(self):
        return self.__bankCode

    @check_strict(r'\d{4}')
    def _set_bank_code(self, value, strict=True):
        self.__bankCode = value

    # office code
    ##################
    def _get_office_code(self):
        return self.__officeCode

    @check_strict(r'[ \d]{4}')
    def _set_office_code(self, value, strict=True):
        self.__officeCode = value

    # currency code
    ######################
    def _get_currency_code(self):
        return self.__currencyCode

    def _get_external_currency_code(self):
        return pycountry.currencies.get(numeric=self.__currencyCode)

    @check_strict(r'[ \d]{3}')
    def _set_currency_code(self, value, strict=True):
        self.__currencyCode = value

    def _set_external_currency_code(self, value):
        self._set_currency_code(str(value.numeric))

    # information mode
    #######################
    def _get_information_mode(self):
        return self.__informationMode

    @check_strict(r'[ \d]')
    def _set_information_mode(self, value, strict=True):
        self.__informationMode = value

    # short name
    ####################
    def _get_short_name(self):
        return self.__shortName

    @check_strict(r'[\w ]{26}')
    def _set_short_name(self, value, strict=True):
        self.__shortName = value.rstrip(' ')

    # padding
    #############
    def _get_padding(self):
        return self.__padding

    @check_strict(r'.{3}')
    def _set_padding(self, value, strict=True):
        self.__padding = value

    # initial balance
    #####################
    def _get_initial_balance(self):
        return self.__initialBalance

    def _get_external_initial_balance(self):
        return self._format_currency(self.__initialBalance,
                                     self.__debitOrCredit)

    @check_strict(r'\d{14}')
    def _set_initial_balance(self, value, strict=True):
        self.__initialBalance = value

    def _set_external_initial_balance(self, value):
        c = self._unformat_currency(value)
        self._set_initial_balance(c[0])
        self._set_expense_or_income(c[1])

    # debit or credit
    #####################
    def _get_expense_or_income(self):
        return self.__debitOrCredit

    @check_strict(r'[12]')
    def _set_expense_or_income(self, value, strict=True):
        self.__debitOrCredit = value

    # initial date
    ################
    def _get_initial_date(self):
        return self.__initialDate

    def _get_external_initial_date(self):
        return self._format_date(self.__initialDate)

    @check_strict(r'\d{6}')
    def _set_initial_date(self, value, strict=True):
        self.__initialDate = value

    def _set_external_initial_date(self, value):
        self.__initialDate = self._unformat_date(value)

    # final date
    ###############
    def _get_final_date(self):
        return self.__finalDate

    def _get_external_final_date(self):
        return self._format_date(self.__finalDate)

    @check_strict(r'\d{6}')
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
        Return:
            (Transaction) the last added transaction
        '''
        return self.__transactions[-1]

    def add_transaction(self, record):
        '''
        Add a new transaction to the account

        Args:
            record (str) -- csb record

        Raise:
            Csb43Exception  if :record: is not valid
        '''
        self.__transactions.append(Transaction(record, self.__strict,
                                               decimal=self._decimal,
                                               yearFirst=self._yearFirst))

    def add_item(self, record):
        '''
        Add a new additional item record to the transaction

        Args:
            record (str) -- csb record

        Raise:
            Csb43Exception  if :record: is not valid
        '''
        self.get_last_transaction().add_item(record)

    def get_account_key(self):
        '''
        Return:
            (int) two-digits checksum for the bank account
        '''
        # digitos de control

        fixDigit = lambda x: 1 if x == 10 else x

        sumprod = lambda l1, l2: sum([int(x) * y for x, y in zip(l1, l2)])

        c1 = [7, 3, 6, 1]
        c2 = [2, 4, 8, 5]
        c3 = [10, 9, 7, 3, 6, 1, 2, 4, 8, 5]

        dig1 = fixDigit((sumprod(self.bankCode, c1) +
                         sumprod(self.branchCode, c2)) % 11)

        dig2 = fixDigit(sumprod(self.accountNumber, c3) % 11)

        return dig1 * 10 + dig2

    def close_account(self, record):
        '''
        Close the current account

        Args:
            record (str) -- csb record

        Raise:
            Csb43Exception  if :record: is not valid
        '''

        if self.__closing is not None:
            raiseCsb43Exception("trying to close a closed account",
                                self.__strict)

        def equal_f(a, bal):
            return abs(a - bal) < 10 ** (-self._decimal)

        balance = self.initialBalance
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

        closing = ClosingAccount(record, self.__strict, decimal=self._decimal,
                                 yearFirst=self._yearFirst)
        rBalance = closing.balance
        rPBalance = closing.income
        rNBalance = -closing.expense
        rPositive = closing.incomeEntries
        rNegative = closing.expenseEntries

        if not equal_f(balance, rBalance):
            raiseCsb43Exception("""balance (%1.2f) mismatch in closing account
                                record (%1.2f)""" %
                                (balance, rBalance), self.__strict)
        if not equal_f(pBalance, rPBalance):
            raiseCsb43Exception("""income amount (%1.2f) mismatch in closing
                                account record (%1.2f)""" %
                                (pBalance, rPBalance), self.__strict)
        if not equal_f(nBalance, rNBalance):
            raiseCsb43Exception("""expense amount (%1.2f) mismatch in closing
                                account record (%1.2f)""" %
                                (nBalance, rNBalance), self.__strict)
        if posRecords != rPositive:
            raiseCsb43Exception("""income entries (%d) mismatch in closing
                                account record (%d)""" %
                                (posRecords, rPositive), self.__strict)
        if negRecords != rNegative:
            raiseCsb43Exception("""expense entries (%d) mismatch in closing
                                account record (%d)""" %
                                (negRecords, rNegative), self.__strict)

        self.__closing = closing

    def is_closed(self):
        '''
        Return:
            *True* if this Account has been properly closed
        '''
        return self.__closing is not None

    def _get_closing(self):
        return self.__closing

    def add_exchange(self, record):
        '''
        Add a new additional exchange record to the last added transaction

        Args:
            record (str) -- csb record

        Raise:
            Csb43Exception  if :record: is not valid
        '''
        self.get_last_transaction().add_exchange(record)

    # **** Properties ****
    transactions = property(_get_transactions, None, None,
                            "list of transactions")
    initialDate = property(_get_external_initial_date,
                           _set_external_initial_date, None,
                           """Start date of the period to which the information
                           corresponds
                           (es) fecha de comienzo del periodo al que
                           corresponde la información""")
    finalDate = property(_get_external_final_date, _set_external_final_date,
                         None,
                         """End date of the period to which the information
                           corresponds
                           (es) fecha de fin del periodo al que
                           corresponde la información""")
    initialBalance = property(_get_external_initial_balance,
                              _set_external_initial_balance, None,
                              """initial balance amount
                              (es) montante del balance inicial""")
    currency = property(_get_external_currency_code,
                        _set_external_currency_code, None,
                        """currency object (pycountry.Currency)
                        (es) objecto de divisa (pycountry.Currency)""")
    shortName = property(_get_short_name, _set_short_name, None,
                         """abbreviated name of the client
                         (es) nombre abreviado del cliente""")
    padding = property(_get_padding, _set_padding, None,
                       "padding")
    accountNumber = property(_get_account_number, _set_account_number, None,
                             """account number
                             (es) número de cuenta""")
    bankCode = property(_get_bank_code, _set_bank_code, None,
                        """bank code
                        (es) código de banco""")
    branchCode = property(_get_office_code, _set_office_code, None,
                          """branch code
                          (es) código de sucursal u oficina""")
    abstract = property(_get_closing, None, None,
                        "account abstract")


class ClosingAccount(Record):
    '''
    An Account abstact, given by a termination record
    '''

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
        super(ClosingAccount, self).__init__(decimal=decimal,
                                             yearFirst=yearFirst)
        self.__strict = strict

        if record is not None:
            if not ClosingAccount.is_valid(record):
                raiseCsb43Exception('bad code of record', self.__strict)

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
        return long(self.__debitEntries)

    def _set_external_expense_entries(self, value):
        self.__debitEntries = '%05d' % value

    def _get_expense_amount(self):
        return self.__debitAmount

    def _get_external_expense_amount(self):
        return self._format_currency(self.__debitAmount)

    def _get_income_entries(self):
        return self.__creditEntries

    def _get_external_income_entries(self):
        return long(self.__creditEntries)

    def _set_external_income_entries(self, value):
        self.__creditEntries = '%05d' % value

    def _get_income_amount(self):
        return self.__creditAmount

    def _get_external_income_amount(self):
        return self._format_currency(self.__creditAmount)

    def _get_total_balance(self):
        return self.__totalAmount

    def _get_external_total_balance(self):
        return self._format_currency(self.__totalAmount,
                                     self.__totalAmountCode)

    def _get_total_balance_code(self):
        return self.__totalAmountCode

    def _get_currency_code(self):
        return self.__currencyCode

    def _get_external_currency_code(self):
        return pycountry.currencies.get(numeric=self.__currencyCode)

    def _get_padding(self):
        return self.__padding

    @check_strict(r'\d{5}')
    def _set_expense_entries(self, value, strict=True):
        self.__debitEntries = value

    @check_strict(r'\d{10}')
    def _set_expense_amount(self, value, strict=True):
        self.__debitAmount = value

    def _set_external_expense_amount(self, value):
        c = self._unformat_currency(value)
        self._set_expense_amount(c[0])

    @check_strict(r'\d{5}')
    def _set_income_entries(self, value, strict=True):
        self.__creditEntries = value

    @check_strict(r'\d{10}')
    def _set_income_amount(self, value, strict=True):
        self.__creditAmount = value

    def _set_external_income_amount(self, value):
        c = self._unformat_currency(value)
        self._set_income_amount(c[0])

    @check_strict(r'\d{14}')
    def _set_total_balance(self, value, strict=True):
        self.__totalAmount = value

    def _set_external_total_balance(self, value):
        c = self._unformat_currency(value)
        self._set_total_balance(c[0])
        self._set_total_balance_code(c[1])

    @check_strict(r'[12]')
    def _set_total_balance_code(self, value, strict=True):
        self.__totalAmountCode = value

    @check_strict(r'\d{3}')
    def _set_currency_code(self, value, strict=True):
        self.__currencyCode = value

    def _set_external_currency_code(self, value):
        self._set_currency_code(str(value.numeric))

    @check_strict(r'.{3}')
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

    @check_strict(r'\d{10}')
    def _set_account_number(self, value, strict=True):
        self.__accountNumber = value

    # bank code
    ##################
    def _get_bank_code(self):
        return self.__bankCode

    @check_strict(r'\d{4}')
    def _set_bank_code(self, value, strict=True):
        self.__bankCode = value

    # office code
    ##################
    def _get_office_code(self):
        return self.__officeCode

    @check_strict(r'\d{4}')
    def _set_office_code(self, value, strict=True):
        self.__officeCode = value

    # **** Properties ****
    accountNumber = property(_get_account_number, _set_account_number, None,
                             """account number
                             (es) número de cuenta""")
    bankCode = property(_get_bank_code, _set_bank_code, None,
                        """bank code
                        (es) código de banco""")
    branchCode = property(_get_office_code, _set_office_code, None,
                          """branch code
                          (es) código de sucursal u oficina""")
    expenseEntries = property(_get_external_expense_entries,
                              _set_external_expense_entries, None,
                              """number of debit entries
                              (es) número de entradas en el debe""")
    expense = property(_get_external_expense_amount,
                       _set_external_expense_amount, None,
                       """total debit amounts
                       (es) montante total en el debe""")
    incomeEntries = property(_get_external_income_entries,
                             _set_external_income_entries, None,
                             """number of credit entries
                              (es) número de entradas en el haber""")
    income = property(_get_external_income_amount,
                      _set_external_income_amount, None,
                      """total credit amounts
                       (es) montante total en el haber""")
    balance = property(_get_external_total_balance,
                       _set_external_total_balance, None,
                       """final balance
                       (es) balance final""")
    currency = property(_get_external_currency_code,
                        _set_external_currency_code, None,
                        """currency object (pycountry.Currency)
                        (es) objecto de divisa (pycountry.Currency)""")
    padding = property(_get_padding, _set_padding, None, "padding")
