# -*- coding: utf-8 -*-
'''
@license: GNU Lesser General Public License v3.0 (see LICENSE)
'''

from csb43.i18n import tr as _

BAD_RECORD = lambda x: _('bad code of record or unexpected length: >>>%s<<<') % x

CURRENCY_EXPECTED = lambda x: _("pycountry.Currencies object or a valid"
                                " ISO 4217 code expected,"
                                " but %s found") % x

INCOMPATIBLE_OBJECT = lambda x: _("incompatible object '%s', type(s) %s expected") % (x[0], ', '.join(x[1:]))

# Account ID
T_BANK_CODE = _('bank_code')
T_BRANCH_CODE = _('branch_code')
T_ACCOUNT_KEY = _('account_key')
T_ACCOUNT_NUMBER = _('account_number')

# Account abstract
T_INFORMATION_MODE = _('information_mode')
T_SHORT_NAME = _('short_name')
T_CURRENCY = _('currency')
T_INITIAL_DATE = _('initial_date')
T_FINAL_DATE = _('final_date')
T_INITIAL_BALANCE = _('initial_balance')
T_FINAL_BALANCE = _('final_balance')
T_INCOME = _('income')
T_EXPENSES = _('expenses')
T_INCOME_ENTRIES = _('income_entries')
T_EXPENSES_ENTRIES = _('expenses_entries')

# Transaction
T_DOCUMENT_NUMBER = _('document_number')
T_SHARED_ITEM = _('shared_item')
T_OWN_ITEM = _('own_item')
T_ITEM_1 = _('item1')
T_ITEM_2 = _('item2')
T_REFERENCE_1 = _('reference1')
T_REFERENCE_2 = _('reference2')
T_TRANSACTION_DATE = _('transaction_date')
T_VALUE_DATE = _('value_date')
T_AMOUNT = _('amount')
T_ORIGINAL_CURRENCY = _('original_currency')
T_ORIGINAL_AMOUNT = _('original_amount')
T_OPTIONAL_ITEMS = _('optional_items')
T_EXCHANGE = _('exchange')

# Item
T_RECORD_CODE = _('record_code')