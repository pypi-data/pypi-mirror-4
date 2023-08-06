# -*- coding: utf-8 -*-
'''
.. note::

    license: GNU Lesser General Public License v3.0 (see LICENSE)
'''

from csb43.utils import check_strict, raiseCsb43Exception
import csb43.utils.messages as msg
#from csb43.i18n import tr as _

class Item(object):
    '''
    Complementary item / (es) Concepto adicional (registro 23)

    - Create an :class:`Item` object from a `CSB43` string record::

        >>> from csb43.csb43 import Item
        >>> record = '2301primer concepto adicional             segundo concepto adicional            '
        >>> i = Item(record)
        >>> i.item1
        'primer concepto adicional'
        >>> i.item2
        'segundo concepto adicional'
        >>> i.recordCode
        1

    - From an empty object to a `CSB43` string record::

        >>> i = Item()
        >>> i.item1 = 'primer concepto adicional'
        >>> i.item2 = 'segundo concepto adicional'
        >>> i.recordCode = 1
        >>> str(i)
        '2301primer concepto adicional             segundo concepto adicional            '
    '''

    def __init__(self, record=None, strict=True):
        '''
        :param record: csb record
        :type record: :class:`basestring` or `None`

        :param strict: treat warnings as exceptions when `True`
        :type strict: :class:`bool`

        :raises: :class:`csb43.utils.Csb43Exception`

        '''
        self.__strict = strict

        self.__recordCode = None
        self.__item1 = None
        self.__item2 = None

        if record is not None:
            if not self.is_valid(record):
                raiseCsb43Exception(msg.BAD_RECORD(record), self.__strict)

            self._set_record_code(record[2:4], self.__strict)
            self._set_item_1(record[4:42], self.__strict)
            self._set_item_2(record[42:80], self.__strict)

    def is_valid(self, record):
        return isinstance(record, basestring) and\
            (len(record) == 80) and (record[0:2] == '23')

    def _get_record_code(self):
        if self.__recordCode is None:
            return None
        return int(self.__recordCode)

    def _get_item_1(self):
        return self.__item1

    def _get_item_2(self):
        return self.__item2

    @check_strict(r'^0[12345]$')
    def _set_record_code(self, value, strict=True):
        self.__recordCode = value

    def _set_external_record_code(self, value):
        self._set_record_code('%02d' % int(value))

    @check_strict(r'^.{38}$')
    def _set_item_1(self, value, strict=True):
        self.__item1 = value.rstrip(' ')

    def _set_external_item_1(self, value):
        self._set_item_1('{: <38}'.format(value))

    @check_strict(r'^.{38}$')
    def _set_item_2(self, value, strict=True):
        self.__item2 = value.rstrip(' ')

    def _set_external_item_2(self, value):
        self._set_item_2('{: <38}'.format(value))

    def __str__(self):
        ':rtype: representation of this object as a `CSB43` record'
        return "23{record_code:0>2}{item1: <38}{item2: <38}".format(
                record_code = self.__recordCode or '',
                item1 = self.__item1 or '',
                item2 = self.__item2 or ''
            )

    def __iter__(self):
        return iter([str(self)])

    def as_dict(self):
        '''
        :rtype: a representation of this object as a :class:`dict`. The keys will be localised

            >>> i.as_dict()
            {u'concepto1': 'primer concepto adicional', u'concepto2': 'segundo concepto adicional', u'codigo_de_registro': 1}

        '''
        return {
            msg.T_RECORD_CODE: self.recordCode,
            msg.T_ITEM_1: self.item1,
            msg.T_ITEM_2: self.item2,
        }

    recordCode = property(_get_record_code, _set_external_record_code, None,
                          """code of record / (es) codigo de registro

Code can be assigned as a number or as a string::

    >>> i.recordCode = 1
    >>> i.recordCode
    1
    >>> i.recordCode = '2'
    >>> i.recordCode
    2
    >>> i.recordCode = '01'
    >>> i.recordCode
    1
    >>> try:
    ...     i.recordCode = 10
    ... except Exception, e:
    ...     print e
    ...
    mal formato: el contenido '10' no concuerda con el formato esperado r'^0[12345]$' para este campo

""")
    item1 = property(_get_item_1, _set_external_item_1, None,
                     "first additional item / (es) primer concepto adicional")
    item2 = property(_get_item_2, _set_external_item_2, None,
                     "second additional item / (es) segundo concepto adicional")
