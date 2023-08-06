'''
.. note::

    license: GNU Lesser General Public License v3.0 (see LICENSE)

Parsing and validation utilites for the Spanish standard norm 43 by the
"Consejo Superior Bancario" (CSB) for storing bank account transactions.

(es) Herramientas para leer y validar datos almacenados siguiendo la norma 43
del Consejo Superior Bancario (CSB).

.. seealso::

    References:

    - (https://empresas.bankinter.com/www2/empresas/es/inicio/descarga/formato_de_ficheros)
    - (http://empresa.lacaixa.es/deployedfiles/empreses/Estaticos/PDF/TransferenciaFicheros/Q43euro.pdf)
    - (http://www.tesoreria.com/oldweb/index.php?option=com_content&view=article&id=128:la-norma-43-del-consejo-superior-bancario-csb&catid=59:normativa-nacional-e-internacional&Itemid=90)
'''

from csb_file import File, ClosingFile, showInfo
from account import Account, ClosingAccount
from exchange import Exchange
from item import Item
from record import Record
from transaction import Transaction
