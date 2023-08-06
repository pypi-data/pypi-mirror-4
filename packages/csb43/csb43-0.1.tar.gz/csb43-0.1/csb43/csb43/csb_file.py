# -*- coding: utf8 -*-
'''
@license: GNU Lesser General Public License v3.0 (see LICENSE)
'''

from account import Account
from csb43.utils import check_strict, raiseCsb43Exception, DECIMAL
import sys


def showInfo(csb, fd=sys.stderr):
    '''
    Dump abstract of the object *csb* to a given file descriptor *fd*

    Args:
        csb (csb43.File) -- File file object
        fd (file)        -- file descriptor (default=stderr)
    '''
    print >> fd, "*", len(csb.accounts), "account(s) read"
    print >> fd, "*", "File properly closed:", csb.is_closed()
    print >> fd, "*", csb.abstract.totalRecords, "record(s) read"
    for ac in csb.accounts:
        print >> fd, "*" * 60
        print >> fd, "* +", "Account:", ac.accountNumber, ac.shortName
        print >> fd, "*  ", " From:", ac.initialDate.strftime("%Y-%m-%d")
        print >> fd, "*  ", " To:  ", ac.finalDate.strftime("%Y-%m-%d")
        print >> fd, "*  "
        print >> fd, "*  ", len(ac.transactions), "transaction(s) read"
        print >> fd, "*  ", "Account properly closed:", ac.is_closed()
        print >> fd, "*  "
        print >> fd, "*  ", "Previous amount:", "%14.2f" % \
            ac.initialBalance, ac.currency.letter
        print >> fd, "*  ", " Income:        ", "%14.2f" % \
            ac.abstract.income, ac.abstract.currency.letter
        print >> fd, "*  ", " Expense:       ", "%14.2f" % \
            - ac.abstract.expense, ac.abstract.currency.letter
        print >> fd, "*  ", "Balance:        ", "%14.2f" % \
            ac.abstract.balance, ac.abstract.currency.letter
        print >> fd, "*" * 60


class File(object):
    '''
    A CSB43 file
    '''

    def __init__(self, fd, strict=True, decimal=DECIMAL, yearFirst=True):
        '''
        Args:
            fd (file)
            strict (bool)    -- treat warning as exceptions when *True*
            decimal (int)    -- decimal positions to consider
            yearFirst (bool) -- switch between YYMMD [True] and DDMMYY
                                [False] date formats

        Raise:
            Csb43Exception
        '''

        def skip():
            pass

        launcher = {'00': skip,
                    '11': self.add_account,
                    '22': self.add_transaction,
                    '23': self.add_item,
                    '24': self.add_exchange,
                    '33': self.close_account,
                    '88': self.close_file}
        self.__accounts = []
        self.__strict = strict
        self.__closing = None
        self.__decimal = decimal
        self.__yearFirst = yearFirst

        self.__numRecords = 0
        for line in fd:
            line = line.rstrip('\n\r')
            launcher.get(line[0:2], self.__unknownRecord)(line)
            self.__numRecords += 1

    def __unknownRecord(self, line=''):
        raiseCsb43Exception('bad code of record %s' % line[0:2], self.__strict)

    def _get_accounts(self):
        return self.__accounts

    def get_last_account(self):
        '''
        Return:
            (Account) the last added account
        '''
        return self.__accounts[-1]

    def add_account(self, record):
        '''
        Add a new account

        Args:
            record (str) -- csb record

        Raise:
            Csb43Exception  if :record: is not valid
        '''
        self.__accounts.append(Account(record, self.__strict,
                                       decimal=self.__decimal,
                                       yearFirst=self.__yearFirst))

    def add_transaction(self, record):
        '''
        Add a new transaction to the last added account

        Args:
            record (str) -- csb record

        Raise:
            Csb43Exception  if :record: is not valid
        '''
        self.get_last_account().add_transaction(record)

    def add_item(self, record):
        '''
        Add a new additional item record to the last added transaction

        Args:
            record (str) -- csb record

        Raise:
            Csb43Exception  if :record: is not valid
        '''
        self.get_last_account().add_item(record)

    def add_exchange(self, record):
        '''
        Add a new additional exchange record to the last added transaction

        Args:
            record (str) -- csb record

        Raise:
            Csb43Exception  if :record: is not valid
        '''
        self.get_last_account().add_exchange(record)

    def close_account(self, record):
        '''
        Close the current account

        Args:
            record (str) -- csb record

        Raise:
            Csb43Exception  if :record: is not valid
        '''
        self.get_last_account().close_account(record)

    def close_file(self, record):
        '''
        Close the file with a termination record

        Args:
            record (str) -- csb record

        Raise:
            Csb43Exception  if :record: is not valid
        '''
        if self.__closing is not None:
            raiseCsb43Exception("trying to close a closed file", self.__strict)

        self.__closing = ClosingFile(record, self.__strict)
        if int(self.__closing.totalRecords) != self.__numRecords:
            raiseCsb43Exception('incongruent closing record of file',
                                self.__strict)

    def is_closed(self):
        '''
        Return:
            *True* if this File has been properly closed
        '''
        return self.__closing is not None

    def _get_closing(self):
        return self.__closing

    #**** Properties ****

    accounts = property(_get_accounts, None, None, "list of accounts")
    abstract = property(_get_closing, None, None, "file abstract")


class ClosingFile(object):
    '''
    A File abstact, given by a termination record
    '''

    def __init__(self, record=None, strict=True):
        '''
        Args:
            record (str)  -- csb record
            strict (bool) -- treat warning as exceptions when *True*
        Raise:
            Csb43Exception   if :record: is not valid
        '''
        self.__strict = strict

        if record is not None:
            if not ClosingFile.is_valid(record):
                raiseCsb43Exception('bad code of record', self.__strict)

            self._check_nines(record[2:20], self.__strict)
            self._set_total_records(record[20:26], self.__strict)
            self._set_padding(record[26:80], self.__strict)

    def _get_total_records(self):
        return self.__totalRecords

    def _get_external_total_records(self):
        return long(self.__totalRecords)

    def _get_padding(self):
        return self.__padding

    @check_strict(r'\d{6}')
    def _set_total_records(self, value, strict=True):
        self.__totalRecords = value

    def _set_external_total_records(self, value):
        self.__totalRecords = "%06d" % value

    @check_strict(r'.{54}')
    def _set_padding(self, value, strict=True):
        self.__padding = value

    @check_strict(r'9{18}')
    def _check_nines(self, value, strict=True):
        pass

    @staticmethod
    def is_valid(record):
        return isinstance(record, basestring)\
            and (27 <= len(record) <= 80) and (record[0:2] == '88')

    #**** Properties ****

    totalRecords = property(_get_external_total_records,
                            _set_external_total_records, None,
                            "total number of entries")
    padding = property(_get_padding, _set_padding, None, "padding")
