'''
@license: GNU Lesser General Public License v3.0 (see LICENSE)
'''

import re
import datetime
import pycountry
import sys

class Csb43Exception(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

def raiseCsb43Exception(value='', strict=False):
    exc = Csb43Exception(value)
    if strict:
        raise exc
    else:
        print >> sys.stderr, exc


def check_string(pattern = '', field = '', strict = True):
    '''
    Expected parameters:
        pattern (str) -- pattern description using regular expressions
        field         -- variable to be checked
        strict (bool) -- treat exceptions as warnings if *False*
    '''

    if len(re.findall(pattern, field)) != 1:
        raiseCsb43Exception("Bad format: content '%s' mismatches the expected format r'%s' for this field" % (field, pattern), strict)

def check_strict(pattern):
    """
    decorator

    Expected parameters:
        pattern (str) -- pattern description using regular expressions
        field         -- variable to be checked
        strict (bool) -- treat exceptions as warnings if *False*
    """
    def decorator(f):

        def wrapped(self, *args, **kw):
            check_string(pattern, *args, **kw)
            return f(self, *args, **kw)

        return wrapped

    return decorator

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
    f = DATEFORMAT[1] if yearFirst else DATEFORMAT[0]
    return value.strftime(f)

def currencyISO(code):
    '''
    Returns a pycountry.currency object from its numeric code
    '''
    return pycountry.currencies.get(numeric=code)

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
