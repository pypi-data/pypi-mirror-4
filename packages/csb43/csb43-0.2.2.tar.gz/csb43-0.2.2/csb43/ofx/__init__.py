'''
.. note::

    license: GNU Lesser General Public License v3.0 (see LICENSE)

Partial implementation of a OFX file writer.

This package is not intended to fully implement the OFX Spec. Its final purpose
is the conversion from CSB43 (norma 43 del Consejo Superior Bancario). That is,
only transaction response is (partially) implemented.

.. seealso::

    References:

    - (http://www.ofx.net/)
'''

from ofx_file import *
from converter import convertFromCsb, PAYMODES