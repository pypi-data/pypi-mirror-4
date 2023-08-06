# -*- coding: utf-8 -*-
'''
.. note::

    license: GNU Lesser General Public License v3.0 (see LICENSE)
'''

import re
import datetime
#import pycountry
import sys
import functools

from csb43.i18n import tr as _

class Csb43Exception(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return unicode(self.value).encode('utf-8')

def raiseCsb43Exception(value='', strict=False):
    '''
    raise a :class:`Csb43Exception` or print the exception's message to standard error

    :param value: message of the exception
    :param strict: print to standard error instead of raising an exception if not `strict`

    :raises: :class:`Csb43Exception`
    '''
    exc = Csb43Exception(value)
    if strict:
        raise exc
    else:
        print >> sys.stderr, exc


def check_string(pattern = '', field = '', strict = True):
    '''
    :param pattern: pattern description using regular expressions
    :type  pattern: :class:`basestring`

    :param field: variable to be checked

    :param strict: treat exceptions as warnings if `False`
    :type  strict: :class:`bool`

    :raises: :class:`Csb43Exception` if `field` doesn't match `pattern` and `strict` is `True`
    '''

    if len(re.findall(pattern, field)) != 1:
        raiseCsb43Exception(_("Bad format: content '%s' mismatches the expected format r'%s' for this field") % (field, pattern), strict)

def check_strict(pattern):
    """
    .. note::

        decorator

    :param pattern: pattern description using regular expressions
    :type  pattern: :class:`basestring`

    :param field: variable to be checked

    :param strict: treat exceptions as warnings if `False`
    :type  strict: :class:`bool`

    :raises: :class:`Csb43Exception` if `field` doesn't match `pattern` and `strict` is `True`
    """
    def _decorator(f):

        @functools.wraps(f)
        def _wrapped(self, *args, **kw):
            check_string(pattern, *args, **kw)
            return f(self, *args, **kw)

        return _wrapped

    return _decorator

DECIMAL = 2
DATEFORMAT = ["%d%m%y", "%y%m%d"]

def raw2currency(value, decimal=DECIMAL, debit='2'):
    '''
    Format the CSB composite type for amounts as a real number

    Args:
        value (long or str) -- absolute amount without decimal separator
        decimal (int)       -- number of digits reserved for decimal numbers
        debit ('1','2')     -- '1' debit, '2' credit

    Return:
        (float) the amount as a real number

    Examples:

    >>> utils.raw2currency('123456')
    1234.56
    >>> utils.raw2currency('12345',debit='1')
    -123.45

    '''
    val = -long(value) if debit=='1' else long(value)
    return val/float(10**decimal)

def currency2raw(value, decimal=DECIMAL):
    '''
    Convert a real to the CSB amount format

    Args:
        value (float) -- quantity as a real number
        decimal (int) -- number of digits reserved for decimal numbers

    Return:
        tuple of absolute amount and debit flag

    Examples:

    >>> utils.currency2raw(-123.456)
    (12345L, '1')
    >>> utils.currency2raw(123.45)
    (12345L, '2')
    '''
    return abs(long(value*(10**decimal))), '1' if value<0 else '2'

def raw2date(value, yearFirst = True):
    '''
    Convert the CSB date format to a datetime.datetime object

    Args:
        value (str)      -- date using the CSB format
	yearFirst (bool) -- if *False*, consider the CSB format is DDMMYY instead of YYMMDD

    Return:
    	(datetime.datetime) the date object

    Examples:

    >>> utils.raw2date('020301')
    datetime.datetime(2002, 3, 1, 0, 0)
    '''
    f = DATEFORMAT[1] if yearFirst else DATEFORMAT[0]
    return datetime.datetime.strptime(value, f)

def date2raw(value, yearFirst = True):
    '''
    Convert a datetime object to a CSB formatted date

    Args:
        value (datetime.datetime) -- datetime object
	yearFirst (bool) -- if *False*, consider the CSB format is DDMMYY instead of YYMMDD

    Return:
        (str) the CSB date

    Examples:

    >>> a = utils.raw2date('020301')
    >>> utils.date2raw(a)
    '020301'
    '''
    if isinstance(value, (datetime.datetime, datetime.date)):
        f = DATEFORMAT[1] if yearFirst else DATEFORMAT[0]
        return value.strftime(f)
    else:
        raise Csb43Exception(_("instance of datetime or date expected, but '%s' found") % type(value))

class CurrencyLite(object):

    def __init__(self, letter, numeric):
        self.letter = letter
        self.numeric = numeric

from currency_data import CURRENCY_DATA

__CUR_LETTER = {}
__CUR_NUMERIC = {}

for el in CURRENCY_DATA:
    __tmp = CurrencyLite(el[0], el[1])
    if el[0]:
        __CUR_LETTER[el[0]] = __tmp
    if el[1]:
        __CUR_NUMERIC[el[1]] = __tmp

def currencyISO(numeric):
    '''
    :param code: a ISO 4217 numeric code
    :type  code: :class:`str`
    :rtype: :class:`pycountry.db.Currency` object from its numeric code
    '''
    if hasattr(sys, 'frozen'):
        return __CUR_NUMERIC[numeric]
    else:
        import pycountry
        return pycountry.currencies.get(numeric=numeric)

def currencyISOByLetter(letter):
    '''
    :param code: a ISO 4217 numeric code
    :type  code: :class:`str`
    :rtype: :class:`pycountry.db.Currency` object from its numeric code
    '''
    if hasattr(sys, 'frozen'):
        return __CUR_LETTER[letter]
    else:
        import pycountry
        return pycountry.currencies.get(letter=letter)

def isCurrency(obj):
    if hasattr(sys, 'frozen'):
        return isinstance(obj, CurrencyLite)
    else:
        import pycountry
        return isinstance(obj, pycountry.db.Data)

# items
CONCEPTOS = {
             '01': "TALONES - REINTEGROS",
             '02': "ABONARES - ENTREGAS - INGRESOS",
             '03': "DOMICILIADOS - RECIBOS - LETRAS - PAGOS POR SU CUENTA",
             '04': "GIROS - TRANSFERENCIAS - TRASPASOS - CHEQUES",
             '05': "AMORTIZACIONES, PRESTAMOS, CREDITOS, ETC.",
             '06': "REMESAS, EFECTOS",
             '07': "SUSCRIPCIONES - DIV. PASIVOS - CANJES",
             '08': "DIV. CUPONES - PRIMA JUNTA - AMORTIZACIONES",
             '09': "OPERACIONES DE BOLSA Y/O COMPRA/VENTA VALORES",
             '10': "CHEQUES GASOLINA",
             '11': "CAJERO AUTOMATICO",
             '12': "TARJETAS DE CREDITO - TARJETAS DE DEBITO",
             '13': "OPERACIONES EXTRANJERO",
             '14': "DEVOLUCIONES E IMPAGADOS",
             '15': "NOMINAS - SEGUROS SOCIALES",
             '16': "TIMBRES - CORRETAJE - POLIZA",
             '17': "INTERESES - COMISIONES - CUSTODIA - GASTOS E IMPUESTOS",
             '98': "ANULACIONES - CORRECCIONES ASIENTO",
             '99': "VARIOS"
             }
