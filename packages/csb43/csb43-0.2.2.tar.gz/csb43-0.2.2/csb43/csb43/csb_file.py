# -*- coding: utf-8 -*-
'''
.. note::
    license: GNU Lesser General Public License v3.0 (see LICENSE)
'''

from account import Account
from csb43.utils import check_strict, raiseCsb43Exception, DECIMAL
import csb43.utils.messages as msg
from csb43.i18n import tr as _
import sys


def showInfo(csb, fd=sys.stderr):
    '''
    :param csb: csb file object
    :type csb: :class:`File`

    :param fd: file descriptor
    :type fd: :class:`file`
    '''
    print >> fd, "*", (_("%d\taccount(s) read") % len(csb.accounts)).encode('utf-8')
    print >> fd, "*", (_("File properly closed:\t%s") % csb.is_closed()).encode('utf-8')
    print >> fd, "*", (_("%d\trecord(s) read") % csb.abstract.totalRecords).encode('utf-8')
    for ac in csb.accounts:
        print >> fd, "*" * 60
        print >> fd, "* +", (_("Account:\t%s\t%s") % (ac.accountNumber, ac.shortName)).encode('utf-8')
        print >> fd, "*  ", (_(" From:\t%s") % ac.initialDate.strftime("%Y-%m-%d")).encode('utf-8')
        print >> fd, "*  ", (_(" To:  \t%s") % ac.finalDate.strftime("%Y-%m-%d")).encode('utf-8')
        print >> fd, "*  "
        print >> fd, "*  ", (_("%d\ttransaction(s) read") % len(ac.transactions)).encode('utf-8')
        print >> fd, "*  ", (_("Account properly closed:\t%s") % ac.is_closed()).encode('utf-8')
        print >> fd, "*  "
        print >> fd, "*  ", (_("Previous amount:\t%14.2f\t%s") % \
            (ac.initialBalance, ac.currency.letter)).encode('utf-8')
        print >> fd, "*  ", (_(" Income:        \t%14.2f\t%s") % \
            (ac.abstract.income, ac.abstract.currency.letter)).encode('utf-8')
        print >> fd, "*  ", (_(" Expense:       \t%14.2f\t%s") % \
            (- ac.abstract.expense, ac.abstract.currency.letter)).encode('utf-8')
        print >> fd, "*  ", (_("Balance:        \t%14.2f\t%s") % \
            (ac.abstract.balance, ac.abstract.currency.letter)).encode('utf-8')
        print >> fd, "*" * 60


class File(object):
    '''
    A CSB43 file

    - Create a :class:`File` object from a file descriptor::

        >>> from csb43.csb43 import File
        >>> with open("csb_file.csb") as fd:
        ...     f = File(fd)
        ...     # do something with f
        ...

    - Create an empty :class:`File` object::

        >>> f = File()

    '''

    def __init__(self, fd = None, strict=True, decimal=DECIMAL, yearFirst=True):
        '''
        :param fd: a csb file
        :type fd: :class:`file`

        :param strict: treat warnings as exceptions when `True`
        :type strict: :class:`bool`

        :param decimal: number of digits to be considered as the decimal part in money
        :type decimal: :class:`int`

        :param yearFirst: switch between YYMMD [`True`] and DDMMYY [`False`] date formats
        :type yearFirst: :class:`bool`

        :raises: :class:`csb43.utils.Csb43Exception`
        '''

        self.__accounts = []
        self.__strict = strict
        self.__closing = None
        self.__decimal = decimal
        self.__yearFirst = yearFirst
        self.__numRecords = 0
        self.__fromFile = False

        if fd is not None:

            self.__fromFile = True

            def skip():
                pass

            launcher = {'00': skip,
                        '11': self.add_account,
                        '22': self.add_transaction,
                        '23': self.add_item,
                        '24': self.add_exchange,
                        '33': self.close_account,
                        '88': self.close_file}

            for line in fd:
                line = line.rstrip('\n\r')
                launcher.get(line[0:2], self.__unknownRecord)(line)
                self.__numRecords += 1

            self.__fromFile = False
        #else:
            #pass

    def __unknownRecord(self, line=''):
        raiseCsb43Exception(msg.BAD_RECORD(line), self.__strict)

    def _get_accounts(self):
        return self.__accounts

    def get_last_account(self):
        '''
        :rtype: the last added :class:`Account`
        '''
        return self.__accounts[-1]

    def add_account(self, record):
        '''
        Add a new account

        :param record: account record
        :type record: :class:`Account` or :class:`basestring`

        :raises: :class:`csb43.utils.Csb43Exception` if `record` is not valid
        '''
        if isinstance(record, Account):
            self.__accounts.append(record)
        else:
            self.__accounts.append(Account(record, self.__strict,
                                        decimal=self.__decimal,
                                        yearFirst=self.__yearFirst))

    def add_transaction(self, record):
        '''
        Add a new transaction to the last added account

        :param record: transaction record
        :type record: :class:`Transaction` or :class:`basestring`

        :raises: :class:`csb43.utils.Csb43Exception`

        .. seealso::

            :func:`Account.add_transaction`
        '''
        self.get_last_account().add_transaction(record)

    def add_item(self, record):
        '''
        Add a new additional item record to the last added transaction

        :param record: item record
        :type record: :class:`Item` or :class:`basestring`

        :raises: :class:`csb43.utils.Csb43Exception` when the record is impossible to parse, or if the         maximum number of complementary items has been reached

        .. seealso::

            :func:`Transaction.add_item`
        '''
        self.get_last_account().add_item(record)

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
        self.get_last_account().add_exchange(record, update)

    def close_account(self, record = None):
        '''
        Close the current account

        :param record: csb record
        :type record: :class:`ClosingAccount` or :class:`basestring`

        :raises: :class:`csb43.utils.Csb43Exception` if `record` is not valid

        .. seealso::

            :func:`csb43.csb43.Account.close_account`
        '''
        self.get_last_account().close_account(record)

    def close_file(self, record = None):
        '''
        Close the file with a termination record

        :param record: csb record
        :type record: :class:`ClosingFile` or :class:`basestring`

        :raises: :class:`csb43.utils.Csb43Exception` if `record` is not valid

        If record is `None`, a new abstract is generated::

            >>> c = csb.File()
            >>> c.is_closed()
            False
            >>> c.close_file()
            >>> c.is_closed()
            True
            >>> c.abstract.totalRecords
            0
            >>> c.add_account(csb.Account())
            >>> c.abstract.totalRecords
            0
            >>> c.close_file()
            >>> c.abstract.totalRecords
            1
            >>> c.is_closed()
            True

        If record is not empty, the number of records of `File` must be coincident
        with the quantity given in `record`::

            >>> cf = csb.ClosingFile()
            >>> cf.totalRecords = 5
            >>> c.close_file(cf)
            Traceback (most recent call last):
            File "<stdin>", line 1, in <module>
            File "csb43/csb43/csb_file.py", line 200, in close_file

            File "csb43/utils/utils.py", line 25, in raiseCsb43Exception
                raise exc
            csb43.utils.utils.Csb43Exception: registro de cierre de fichero incongruente: total de registros 5 != 1
            >>>
        '''
        if self.__fromFile and (self.__closing is not None):
            raiseCsb43Exception(_("trying to close an already closed file"), self.__strict)

        if record is not None:
            if isinstance(record, ClosingFile):
                self.__closing = record
            else:
                self.__closing = ClosingFile(record, self.__strict)

            n_r1 = int(self.__closing.totalRecords)
            n_r2 = self._get_num_records()
            if n_r1 != n_r2:
                raiseCsb43Exception(_('incongruent closing record of file: total records %d != %d') % (n_r1, n_r2),
                                    self.__strict)
        else:
            self.__closing = ClosingFile(strict = self.__strict)
            self.__closing.totalRecords = self._get_num_records()

    def _get_num_records(self):
        if self.__fromFile:
            return self.__numRecords
        else:
            return sum([len([x for x in ac]) for ac in self.accounts])

    def is_closed(self):
        '''
        :rtype: `True` if this File has been properly closed
        '''
        return self.__closing is not None

    def _get_closing(self):
        return self.__closing

    def as_dict(self):
        '''
        :rtype: a representation of this object as a :class:`dict`. The keys will be localised

        >>> import csb43.csb43 as csb
        >>> f = csb.File()
        >>> f.add_account(csb.Account())
        >>> f.add_transaction(csb.Transaction())
        >>> import pprint
        >>> pprint.pprint(f.as_dict())
        {u'cuentas': [{u'balance_inicial': None,
                    u'codigo_de_entidad': None,
                    u'codigo_de_sucursal': None,
                    u'divisa': None,
                    u'fecha_de_comienzo': None,
                    u'fecha_de_fin': None,
                    u'modalidad_de_informacion': None,
                    u'movimientos': [{u'cantidad': None,
                                        u'codigo_de_sucursal': None,
                                        u'concepto_comun': None,
                                        u'concepto_propio': None,
                                        u'fecha_de_operacion': None,
                                        u'fecha_valor': None,
                                        u'numero_del_documento': None,
                                        u'primera_referencia': None,
                                        u'segunda_referencia': None}],
                    u'nombre_abreviado': None,
                    u'numero_de_cuenta': None}]}
        '''
        return {
            _("accounts"): [x.as_dict() for x in self.accounts]
        }

    def __iter__(self):
        ''':rtype: iterator of all the `CSB43` records that this object represents

        >>> import csb43.csb43 as csb
        >>> f = csb.File()
        >>> f.add_account(csb.Account())
        >>> f.add_transaction(csb.Transaction())
        >>> for x in f:
        ...     print x
        ...
        11                  000000000000000000000000000000
        22    0000000000000000000001000000000000000000000000000000000000
        88999999999999999999000002
        >>>

        '''
        if not self.__fromFile:
            self.close_file()
        return _FileIter(self)

    def __str__(self):
        r''':rtype: representation of this object as `CSB43` records (using `\\n` as separator)

        >>> import csb43.csb43 as csb
        >>> f = csb.File()
        >>> f.add_account(csb.Account())
        >>> f.add_transaction(csb.Transaction())
        >>> print f
        11                  000000000000000000000000000000
        22    0000000000000000000001000000000000000000000000000000000000
        88999999999999999999000002
        '''
        return '\n'.join([x for x in self])

    #**** Properties ****

    accounts = property(_get_accounts, None, None, ":rtype: :class:`list` of accounts")
    abstract = property(_get_closing, None, None, ":rtype: :class:`ClosingFile` file abstract")


class _FileIter(object):

    def __init__(self, f):
        self.__output = []
        self.__output.extend(f.accounts)
        if f.abstract:
            self.__output.append(f.abstract)

        self.__iter = iter(self.__output)
        self.__acc = None

    def next(self):
        if self.__acc:
            try:
                return self.__acc.next()
            except StopIteration:
                self.__acc = None
        now = self.__iter.next()

        if isinstance(now, Account):
            self.__acc = iter(now)
            return self.next()
        else:
            return str(now)

class ClosingFile(object):
    '''
    A File abstract, given by a termination record

    Create a :class:`ClosingFile` object from a `CSB43` string record::

        >>> from csb43.csb43 import ClosingFile
        >>> c = ClosingFile(record)

    From an empty object to a `CSB43` string record::

        >>> c = ClosingFile()
        >>> c.totalRecords = 123
        >>> str(c)
        '88999999999999999999000123                                                      '

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

        self.__totalRecords = None
        self.__padding = None

        if record is not None:
            if not ClosingFile.is_valid(record):
                raiseCsb43Exception(msg.BAD_RECORD(record), self.__strict)

            self._check_nines(record[2:20], self.__strict)
            self._set_total_records(record[20:26], self.__strict)
            self._set_padding(record[26:80], self.__strict)

    def _get_total_records(self):
        if self.__totalRecords is None:
            return None
        return int(self.__totalRecords)

    def _get_external_total_records(self):
        if self.__totalRecords is None:
            return None
        return int(self.__totalRecords)

    def _get_padding(self):
        return self.__padding

    @check_strict(r'^\d{6}$')
    def _set_total_records(self, value, strict=True):
        self.__totalRecords = value

    def _set_external_total_records(self, value):
        self._set_total_records(str(value).rjust(6,'0'))

    @check_strict(r'^.{0,54}$')
    def _set_padding(self, value, strict=True):
        self.__padding = value

    @check_strict(r'^9{18}$')
    def _check_nines(self, value, strict=True):
        pass

    @staticmethod
    def is_valid(record):
        return isinstance(record, basestring)\
            and (27 <= len(record) <= 80) and (record[0:2] == '88')

    def __str__(self):
        r''':rtype: representation of this object as `CSB43` records (using `\\n` as separator)'''
        return "88{nines}{records:0>6}{padding: <54}".format(
                nines = '9'*18,
                records = self._get_total_records() or '',
                padding = self._get_padding() or ''
            )

    #**** Properties ****

    totalRecords = property(_get_external_total_records,
                            _set_external_total_records, None,
                            """total number of entries

>>> c.totalRecords = 34
>>> c.totalRecords
34
>>> c.totalRecords = '115'
>>> c.totalRecords
115

""")
    padding = property(_get_padding, _set_padding, None, "padding")
