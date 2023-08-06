# -*- coding: utf8 -*-
'''
@license: GNU Lesser General Public License v3.0 (see LICENSE)
'''

from csb43.utils import check_strict, raiseCsb43Exception


class Item(object):
    '''
    Complementary item
    (es) Concepto adicional (registro 23)
    '''

    def __init__(self, record=None, strict=True):
        '''
        Args:
            record (str)  -- csb record (defalt=None)
            strict (bool) -- treat warning as exceptions when *True*

        Raise:
            Csb43Exception
        '''
        self.__strict = strict

        self.__recordCode = None
        self.__item1 = None
        self.__item2 = None

        if record is not None:
            if not self.is_valid(record):
                raiseCsb43Exception('bad code of record', self.__strict)

            self._set_record_code(record[2:4], self.__strict)
            self._set_item_1(record[4:42], self.__strict)
            self._set_item_2(record[42:80], self.__strict)

    def is_valid(self, record):
        return isinstance(record, basestring) and\
            (len(record) == 80) and (record[0:2] == '23')

    def _get_record_code(self):
        return self.__recordCode

    def _get_item_1(self):
        return self.__item1

    def _get_item_2(self):
        return self.__item2

    @check_strict(r'^0[12345]$')
    def _set_record_code(self, value, strict=True):
        self.__recordCode = value

    @check_strict(r'^.{38}$')
    def _set_item_1(self, value, strict=True):
        self.__item1 = value.rstrip(' ')

    @check_strict(r'^.{38}$')
    def _set_item_2(self, value, strict=True):
        self.__item2 = value.rstrip(' ')

    recordCode = property(_get_record_code, _set_record_code, None,
                          """code of record
                          (es) código de registro""")
    item1 = property(_get_item_1, _set_item_1, None,
                     """first additional item
                     (es) primer concepto adicional""")
    item2 = property(_get_item_2, _set_item_2, None,
                     """second additional item
                     (es) segundo concepto adicional""")
