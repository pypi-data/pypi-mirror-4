'''
@license: GNU Lesser General Public License v3.0 (see LICENSE)
'''


from ofx_file import (BankAccount, File, Response, Balance,
                      TransactionList, Transaction)

#: conversion table OFX - Homebank for pay modes
PAYMODES = {'01': 10,
            '02': 0,
            '03': 5,
            '04': 9,
            '05': 3,
            # '06':
            '07': 15,
            '08': 3,
            # '09':
            '10': 10,
            '11': 7,
            '12': 8,
            # '13':
            # '14':
            '15': 9,
            # '16':
            '17': 2,
            # '98':
            '99': 16}


def convertFromCsb(csb):
    '''
    Convert a File file into an OFX file

    :param csb: a CSB43 file
    :type csb: :class:`csb43.csb43.File`

    :rtype: :class:`csb43.ofx.File`

    >>> # OFX
    >>> from csb43 import csb_43, ofx
    >>> #
    >>> csbFile = csb_43.File(open("movimientos.csb"), strict=False)
    >>> #
    >>> # print to stdout
    >>> print ofx.convertFromCsb(csbFile)

    '''
    ofxFile = File()

    for ac in csb.accounts:

        r = Response()
        # currency
        r.set_currency(ac.currency)
        # account
        bAcc = BankAccount()
        bAcc.set_bank(ac.bankCode)
        bAcc.set_branch(ac.branchCode)
        bAcc.set_id(ac.accountNumber)
        bAcc.set_key(ac.get_account_key())

        r.set_bank_account_from(bAcc)

        # balance (ledger)
        bal = Balance()

        bal.set_amount(ac.abstract.balance)
        bal.set_date(ac.initialDate)

        r.set_ledger_balance(bal)

        # balance (available)
        # r.set_available_balance(bal)

        # transactions
        tList = TransactionList()
        tList.set_date_start(ac.initialDate)
        tList.set_date_end(ac.finalDate)

        for (number, t) in enumerate(ac.transactions):
            trans = Transaction()

            trans.set_type(
                Transaction.TYPE[PAYMODES.get(t.sharedItem, -1)])
            trans.set_date_posted(t.transactionDate)
            trans.set_date_available(t.valueDate)
            trans.set_transaction_id("%06d" % number)
            trans.set_ref_num(t.reference2)
            trans.set_payeeid(t.reference1)
            # trans.set_name(t.commonItem)
            # trans.set_extended_name(t.particularItem)
            name = ", ".join(
                [x.item1.rstrip(' ') for x in t.optionalItems])
            trans.set_name(name)
            extdname = ", ".join(
                [x.item2.rstrip(' ') for x in t.optionalItems])
            trans.set_memo(extdname)

            trans.set_amount(t.amount)

            if t.exchange is not None:
                trans.set_origin_currency(t.exchange.sourceCurrency)

            tList.add_transaction(trans)

        r.set_transaction_list(tList)

        ofxFile.add_response(r)

    return ofxFile
