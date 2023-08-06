'''
@license: GNU Lesser General Public License v3.0 (see LICENSE)
'''

import csb43.utils as utils


class Record(object):
    '''
    Generic record in a CSB43 file
    '''

    def __init__(self, decimal=utils.DECIMAL, yearFirst=True):
        '''
        Constructor
        '''
        self._decimal = decimal
        self._yearFirst = yearFirst

    def set_decimal_precision(self, decimal):
        self._decimal = decimal

    def set_year_first(self, yearFirst=True):
        self._yearFirst = yearFirst

    def _format_date(self, value):
        '''
        Args:
            value (str) -- CSB date
        Return:
            (datetime)  -- date object
        '''
        return utils.raw2date(value, self._yearFirst)

    def _unformat_date(self, value):
        '''
        Args:
            value (datetime) -- date object
        Return:
            (str)            -- CSB date
        '''
        return utils.date2raw(value, self._yearFirst)

    def _format_currency(self, value, debit='2'):
        '''
        Args:
            value (str)     -- CSB raw amount
            debit (r'[12]') -- flag to indicate credit or debit
        Return:
            (int)           -- formatted numeric amount
        '''
        return utils.raw2currency(value, self._decimal, debit)

    def _unformat_currency(self, value):
        '''
        Args:
            value (int) -- amount
        Return:
            pair (raw amount), (debit [2] or credit [1])
        '''
        return utils.currency2raw(value, self._decimal)
