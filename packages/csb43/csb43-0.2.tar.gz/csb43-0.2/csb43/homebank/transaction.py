# -*- coding: utf-8 -*-
'''
@license: GNU Lesser General Public License v3.0 (see LICENSE)
'''

import datetime as date

from csb43.utils import check_strict, raiseCsb43Exception
from csb43.i18n import tr as _

'''
0. tarjeta de credito
1. cheque
2. efectivo
3. transferencia
4. transferencia interna
5. tarjeta de debito
6. orden de posicion
7. pago electronico
8. deposito
9. honorarios FI
'''


class Transaction(object):
    '''
    Hombebank CSV transaction

    - Creating a record::

        >>> from csb43.homebank import Transaction
        >>> t = Transaction()
        >>> t.amount = 12.45
        >>> from datetime import datetime
        >>> t.date = datetime.now()
        >>> print t
        19-03-13;;;;;12.45;

    - Parsing a record::

        >>> t = Transaction("19-03-13;;;;;12.45;")
        >>> t.amount
        12.45
        >>> t.date
        datetime.datetime(2013, 3, 19, 0, 0)


    '''

    def __init__(self, record=None):
        '''
        :param record: a Hombeank csv record
        :type record: :class:`str`

        :raises: :class:`csb43.utils.Csb43Exception`
        '''
        self.__date = None
        self.__mode = None
        self.__info = None
        self.__payee = None
        self.__description = None
        self.__amount = None
        self.__category = None

        if record is not None:
            fields = record.split(";")
            if len(fields) < 6:
                raiseCsb43Exception(_("bad format, 6 fields expected, but"
                                    "%d found") % len(fields), True)

            self._set_date_str(fields[0])
            self._set_mode(fields[1])
            self._set_info(fields[2])
            self._set_payee(fields[3])
            self._set_description(fields[4])
            self._set_amount(fields[5])
            if len(fields) >= 7:
                self._set_category(fields[6])
            else:
                self._set_category(None)

    def _get_date(self):
        return self.__date

    def _get_mode(self):
        return self.__mode

    def _get_info(self):
        return self.__info

    def _get_payee(self):
        return self.__payee

    def _get_description(self):
        return self.__description

    def _get_amount(self):
        return self.__amount

    def _get_category(self):
        return self.__category

    def _set_date(self, value):
        import datetime
        if not isinstance(value, datetime.date):
            raiseCsb43Exception(_("datetime.date expected"), strict=True)
        self.__date = value

    @check_strict(r"^(\d{2}\-\d{2}\-\d{2})?$")
    def _set_date_str(self, value, strict=True):
        if value == '':
            self.__date = None
        else:
            self.__date = date.datetime.strptime(value, "%d-%m-%y")

    def _set_mode(self, value):
        self.__mode = int(value) if value != '' else None

    def _set_info(self, value):
        self.__info = value

    def _set_payee(self, value):
        self.__payee = value

    def _set_description(self, value):
        self.__description = value

    def _set_amount(self, value):
        self.__amount = float(value)

    def _set_category(self, value):
        self.__category = value

    def __str__(self):
        '''
        :rtype: :class:`str` representation of this record as a row of a Homebank CSV file
        '''
        f = lambda x: '' if x is None else str(x)
        if self.__date is not None:
            mdate = self.__date.strftime("%d-%m-%y")
        else:
            mdate = None

        l = (f(x) for x in [mdate,
                            self.__mode,
                            self.__info,
                            self.__payee,
                            self.__description,
                            "%.2f" % self.__amount,
                            self.__category])

        return ";".join(l)

    date = property(_get_date, _set_date, None, "date of transaction (:class:`datetime.datetime`)")
    mode = property(_get_mode, _set_mode, None, "mode of transaction")
    info = property(_get_info, _set_info, None, "transaction's info")
    payee = property(_get_payee, _set_payee, None, "payee of the transaction")
    description = property(_get_description, _set_description, None,
                           "description of the transaction")
    amount = property(_get_amount, _set_amount, None, "amount of the transaction")
    category = property(_get_category, _set_category, None,
                        "transaction category, according to HomeBank")
