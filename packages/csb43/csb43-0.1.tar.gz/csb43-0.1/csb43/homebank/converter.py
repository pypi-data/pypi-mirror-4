'''
@license: GNU Lesser General Public License v3.0 (see LICENSE)
'''


from transaction import Transaction


PAYMODES = {'01': '2',
            '02': '2',
            '04': '3',
            '12': '5'}


def convertFromCsb(csb):
    '''
    Convert a CSB43 file into a HomeBank CSV file

    Args:
        :csb: (csb43.File)

    Return:
        list of (homebank.Transaction)
    '''

    for ac in csb.accounts:

        hbTrans = []

        for t in ac.transactions:
            record = Transaction()
            record.date = t.valueDate
            record.mode = PAYMODES.get(t.sharedItem, '')
            record.info = t.ownItem
            record.payee = t.reference1.rstrip(' ')

            print t.optionalItems

            info = ["%s: %s" % (x.item1.rstrip(' '), x.item2.rstrip(' '))
                    for x in t.optionalItems]
            record.description = "/".join(info)
            record.amount = "%1.2f" % t.amount

            hbTrans.append(record)

        return hbTrans