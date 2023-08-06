'''
@license: GNU Lesser General Public License v3.0 (see LICENSE)

This module is not intended to fully implement the OFX Spec. Its final purpose
is the conversion from CSB43 (norma 43 del Consejo Superior Bancario). That is,
only transaction response is (partially) implemented.
'''


DATEFORMAT = "%Y%m%d"  # short date OFX format


def getXMLTag(name, content):
    '''
    Wrap *content* with the XML tag *name*

    Args:
        name    -- tag name
        content -- content of the node
    Return:
        (str)
    '''

    if content is not None:
        return "<{0}>{1}</{0}>".format(name.upper(), content)
    else:
        return ""


def strDate(field):
    '''
    Format a date as specified by OFX

    Args:
        field (datetime)
    Return:
        (str)
    '''
    if field:
        return field.strftime(DATEFORMAT)
    else:
        return None


def strBool(field):
    '''
    Format a boolean as specified by OFX

    Args:
        field (bool)
    Return:
        (str)
    '''
    if field is not None:
        if field:
            return "Y"
        else:
            return "N"
    else:
        return None


def strCurrency(field):
    '''
    Format a ISO-4217 currency entity as specified by OFX

    Args:
        field (pycountry.Currency)
    Return:
        (str)
    '''
    if field is not None:
        # ISO-4217
        return field.letter
    else:
        return None


class OfxObject(object):

    def __init__(self, tagName):
        '''
        Args:
            tagName (str) -- name for the XML tag
        '''
        self._tagName = tagName

    def _get_content(self):
        '''
        Return:
            the xml representation of this object
        '''
        return ""

    def get_tag_name(self):
        '''
        Return:
            the XML tag name
        '''
        return self._tagName

    def set_tag_name(self, name):
        '''
        Set a XML tag name for this object

        Args:
            tagName (str) -- name for the XML tag
        '''
        self._tagName = name

    def __str__(self):
        # return getXMLTag(self._tagName, self._get_content())
        return self._get_content()


class File(OfxObject):
    '''
    An OFX file
    '''

    def __init__(self, tagName="ofx"):
        '''
        Args:
            tagName (str) -- see *OfxObject*
        '''
        super(File, self).__init__(tagName)

#        self.__requests = []
        self.__responses = []

#    def get_requests(self):
#        '''
#        Return:
#            list of requests
#        '''
#        return self.__requests

    def get_responses(self):
        '''
        Return:
            list of responses
        '''
        return self.__responses

#    def add_request(self, value):
#        '''
#        Args:
#            value (Request)
#        '''
#        self.__requests.append(value)

    def add_response(self, value):
        '''
        Add a response to the file

        Args:
            value (Response) -- a response
        '''
        self.__responses.append(value)

    def _get_content(self):
        header = '<?xml version="1.0" encoding="ASCII"?>\n'
        header += """<?OFX OFXHEADER="200" VERSION="211" SECURITY="NONE"
                    OLDFILEUID="NONE" NEWFILEUID="NONE"?>"""
        content = ""
        for r in self.__responses:
            aux = getXMLTag("trnuid", 0)
            aux += getXMLTag("status", getXMLTag("code", 0) +
                             getXMLTag("severity", "INFO"))
            aux += getXMLTag(r.get_tag_name(), r)
            content += getXMLTag("stmttrnrs", aux)
        content = getXMLTag("bankmsgsrsv1", content)
        return header + getXMLTag(self.get_tag_name(), content)


class Response(OfxObject):

    def __init__(self, tagName="stmtrs"):
        '''
        Args:
            tagName (str) -- see *OfxObject*
        '''
        super(Response, self).__init__(tagName)

        self.__currency = None
        self.__accountFrom = None
        self.__transactionList = None
        self.__ledgerBalance = None
        self.__availableBalance = None
        self.__balances = []
        self.__mktginfo = None

    def get_currency(self):
        '''
        Return:
            (pycountry.Curency) -- Default currency for the statement
        '''
        return self.__currency

    def get_bank_account_from(self):
        '''
        Return:
            (BankAccount) -- Account-from aggregate
        '''
        return self.__accountFrom

    def get_transaction_list(self):
        '''
        Return:
            (TransactionList) -- Statement-transaction-data aggregate
        '''
        return self.__transactionList

    def get_ledger_balance(self):
        '''
        Return:
            (Balance) -- the ledger balance aggregate
        '''
        return self.__ledgerBalance

    def get_available_balance(self):
        '''
        Return:
            (Balance) -- the available balance aggregate
        '''
        return self.__availableBalance

    def get_balances(self):
        '''
        Return:
            list of miscellaneous other balances
        '''
        return self.__balances

    def get_mktginfo(self):
        '''
        Return:
            marketing info
        '''
        return self.__mktginfo

    def set_currency(self, value):
        '''
        Args:
            value (pycountry.Currency)
        '''
        self.__currency = value

    def set_bank_account_from(self, value):
        '''
        Args:
            value (BankAccount)
        '''
        self.__accountFrom = value

    def set_transaction_list(self, value):
        '''
        Args:
            value (TransactionList)
        '''
        self.__transactionList = value

    def set_ledger_balance(self, value):
        '''
        Args:
            value (Balance)
        '''
        self.__ledgerBalance = value

    def set_available_balance(self, value):
        '''
        Args:
            value (Balance)
        '''
        self.__availableBalance = value

    def add_balance(self, value):
        '''
        Add a complementary balance

        Args:
            value (Balance)
        '''
        self.__balances.append(value)

    def set_mktginfo(self, value):
        '''
        Args:
            value -- marketing info
        '''
        self.__mktginfo = value

    def _get_content(self):
        strC = getXMLTag("curdef", strCurrency(self.__currency))
        strC += getXMLTag("bankacctfrom", self.__accountFrom)
        strC += getXMLTag("banktranslist", self.__transactionList)
        strC += getXMLTag("ledgerbal", self.__ledgerBalance)
        strC += getXMLTag("availbal", self.__availableBalance)
        if len(self.__balances) > 0:
            strC += getXMLTag("ballist",
                              "".join([getXMLTag(x.get_tag_name(), x)
                                       for x in self.__balances]))
        strC += getXMLTag("mktginfo", self.__mktginfo)

        return strC


class TransactionList(OfxObject):
    '''
    Transaction list aggregate
    '''

    def __init__(self, tagName="banktranslist"):
        '''
        Args:
            tagName (str) -- see *OfxObject*
        '''
        super(TransactionList, self).__init__(tagName)

        self.__dateStart = None
        self.__dateEnd = None
        self.__list = []

    def get_date_start(self):
        '''
        Return:
            (datetime) -- date of the first transaction
        '''
        return self.__dateStart

    def get_date_end(self):
        '''
        Return:
            (datetime) -- date of the first transaction
        '''
        return self.__dateEnd

    def get_list(self):
        '''
        Return:
            list of transactions
        '''
        return self.__list

    def set_date_start(self, value):
        '''
        Args:
            value (datetime)
        '''
        self.__dateStart = value

    def set_date_end(self, value):
        '''
        Args:
            value (datetime)
        '''
        self.__dateEnd = value

    def add_transaction(self, value):
        '''
        Add a new transaction to the list

        Args:
            value (Transaction)
        '''
        self.__list.append(value)

    def _get_content(self):
        strC = getXMLTag("dstart", strDate(self.__dateStart))
        strC += getXMLTag("dtend", strDate(self.__dateEnd))
        for t in self.__list:
            strC += getXMLTag(t.get_tag_name(), t)

        return strC


class Transaction(OfxObject):
    '''
    A OFX transaction
    '''

    TYPE = ["CREDIT",  # 0
            "DEBIT",  # 1
            "INT",  # 2
            "DIV",  # 3
            "FEE",  # 4
            "SRVCHG",  # 5
            "DEP",  # 6
            "ATM",  # 7
            "POS",  # 8
            "XFER",  # 9
            "CHECK",  # 10
            "PAYMENT",  # 11
            "CASH",  # 12
            "DIRECTDEP",  # 13
            "DIRECTDEBIT",  # 14
            "REPEATPMT",  # 15
            "OTHER"]  # 16

    def __init__(self, tagName="stmttrn"):
        '''
        Args:
            tagName (str) -- see *OfxObject*
        '''
        super(Transaction, self).__init__(tagName)

        self.__type = None
        self.__datePosted = None
        self.__dateInitiated = None
        self.__dateAvailable = None
        self.__amount = None
        self.__transactionId = None
        self.__correctFitId = None
        self.__correctAction = None
        self.__serverTid = None
        self.__checkNum = None
        self.__refNum = None
        self.__standardIndustrialCode = None
        self.__payee = None
        self.__bankAccountTo = None
        self.__ccAccountTo = None
        self.__memo = None
        self.__imageData = None
        self.__currency = None
        self.__originCurrency = None
        self.__inv401source = None
        self.__payeeid = None
        self.__name = None
        self.__extendedName = None

    def get_name(self):
        '''
        Return:
            (str) -- name of payee or description of transaction
        '''
        return self.__name

    def get_extended_name(self):
        '''
        Return:
            (str) -- extended name of payee or description of transaction
        '''
        return self.__extendedName

    def set_name(self, value):
        self.__name = value

    def set_extended_name(self, value):
        self.__extendedName = value

    def get_ref_num(self):
        '''
        Return:
            (str) -- reference number that uniquely indentifies the transaction.
        '''
        return self.__refNum

    def set_ref_num(self, value):
        self.__refNum = value

    def get_type(self):
        '''
        Return:
            (str) -- transaction type. See *TYPE*. Default ('OTHER')
        '''
        if self.__type is None:
            return Transaction.TYPE[-1]
        else:
            return self.__type

    def get_date_posted(self):
        '''
        Return:
            (datetime) -- date transaction was posted to account
        '''
        return self.__datePosted

    def get_date_initiated(self):
        '''
        Return:
            (datetime) -- date user initiated transaction
        '''
        return self.__dateInitiated

    def get_date_available(self):
        '''
        Return:
            (datetime) -- date funds are available
        '''
        return self.__dateAvailable

    def get_amount(self):
        '''
        Return:
            (number) -- amount of transaction
        '''
        return self.__amount

    def get_transaction_id(self):
        '''
        Return:
            (str) -- transaction ID issued by financial institution
        '''
        return self.__transactionId

    def get_correct_fit_id(self):
        return self.__correctFitId

    def get_correct_action(self):
        return self.__correctAction

    def get_server_tid(self):
        return self.__serverTid

    def get_check_num(self):
        '''
        Return:
            (str) -- check (or other reference) number
        '''
        return self.__checkNum

    def get_standard_industrial_code(self):
        return self.__standardIndustrialCode

    def get_payee(self):
        '''
        Return:
            (Payee)
        '''
        return self.__payee

    def get_payeeid(self):
        '''
        Return:
            (str) -- payee identifier
        '''
        return self.__payeeid

    def get_bank_account_to(self):
        '''
        Return:
            (BankAccount) -- account the transaction is transferring to
        '''
        return self.__bankAccountTo

    def get_cc_account_to(self):
        return self.__ccAccountTo

    def get_memo(self):
        '''
        Return:
            (str) -- extra information
        '''
        return self.__memo

    def get_image_data(self):
        return self.__imageData

    def get_currency(self):
        '''
        Return:
            (pycountry.Currency) -- currency of the transaction,
            if different from the one in *Account*
        '''
        return self.__currency

    def get_origin_currency(self):
        '''
        Return:
            (pycountry.Currency) -- currency of the transaction, if different
            from the one in *Account*
        '''
        return self.__originCurrency

    def get_inv_401source(self):
        return self.__inv401source

    def set_type(self, value):
        self.__type = value

    def set_date_posted(self, value):
        self.__datePosted = value

    def set_date_initialised(self, value):
        self.__dateInitiated = value

    def set_date_available(self, value):
        self.__dateAvailable = value

    def set_amount(self, value):
        self.__amount = value

    def set_transaction_id(self, value):
        self.__transactionId = value

    def set_correct_fit_id(self, value):
        self.__correctFitId = value

    def set_correct_action(self, value):
        self.__correctAction = value

    def set_server_tid(self, value):
        self.__serverTid = value

    def set_check_num(self, value):
        self.__checkNum = value

    def set_standard_industrial_code(self, value):
        self.__standardIndustrialCode = value

    def set_payee(self, value):
        self.__payee = value

    def set_payeeid(self, value):
        self.__payeeid = value

    def set_bank_account_to(self, value):
        self.__bankAccountTo = value

    def set_cc_account_to(self, value):
        self.__ccAccountTo = value

    def set_memo(self, value):
        self.__memo = value

    def set_image_data(self, value):
        self.__imageData = value

    def set_currency(self, value):
        self.__currency = value

    def set_origin_currency(self, value):
        self.__originCurrency = value

    def set_inv_401source(self, value):
        self.__inv401source = value

    def _get_content(self):

        strC = getXMLTag("trntype", self.get_type())
        strC += getXMLTag("dtposted", strDate(self.__datePosted))
        strC += getXMLTag("dtuser", strDate(self.__dateInitiated))
        strC += getXMLTag("dtavail", strDate(self.__dateAvailable))
        strC += getXMLTag("trnamt", self.__amount)
        strC += getXMLTag("fitid", self.__transactionId)
        strC += getXMLTag("correctfitid", self.__correctFitId)
        strC += getXMLTag("correctaction", self.__correctAction)
        strC += getXMLTag("srvrtid", self.__serverTid)
        strC += getXMLTag("checknum", self.__checkNum)
        strC += getXMLTag("refnum", self.__refNum)
        strC += getXMLTag("sic", self.__standardIndustrialCode)
        strC += getXMLTag("payeeid", self.__payeeid)
        strC += getXMLTag("name", self.__name)
        strC += getXMLTag("extdname", self.__extendedName)
        strC += getXMLTag("payee", self.__payee)
        strC += getXMLTag("bankacctto", self.__bankAccountTo)
        strC += getXMLTag("ccacctto", self.__ccAccountTo)
        strC += getXMLTag("memo", self.__memo)
        strC += getXMLTag("imagedata", self.__imageData)
        strC += getXMLTag("currency", strCurrency(self.__currency))
        strC += getXMLTag("origcurrency", strCurrency(self.__originCurrency))
        strC += getXMLTag("inv401source", self.__inv401source)

        return strC


class BankAccount(OfxObject):
    '''
    A bank account
    '''

    TYPE = ["CHECKING", "SAVINGS", "MONEYMRKT", "CREDITLINE"]

    def __init__(self, tagName="bankaccfrom"):
        super(BankAccount, self).__init__(tagName)

        self.__bankId = None
        self.__branchId = None
        self.__id = None
        self.__type = None
        self.__key = None

    def get_type(self):
        '''
        Return:
            (str) -- type of account. See *TYPE* (default 'SAVINGS')
        '''
        if self.__type is None:
            return BankAccount.TYPE[1]
        else:
            return self.__type

    def get_key(self):
        '''
        Return:
            (str) -- checksum (Spain: digitos de control)
        '''
        return self.__key

    def set_type(self, value):
        self.__type = value

    def set_key(self, value):
        self.__key = value

    def get_bank(self):
        '''
        Return:
            (str) -- bank identifier (Spain: banco, entidad)
        '''
        return self.__bankId

    def get_branch(self):
        '''
        Return:
            (str) -- branch identifier (Spain: sucursal, oficina)
        '''
        return self.__branchId

    def get_id(self):
        '''
        Return:
            (str) -- account identifier
        '''
        return self.__id

    def set_bank(self, value):
        self.__bankId = value

    def set_branch(self, value):
        self.__branchId = value

    def set_id(self, value):
        self.__id = value

    def _get_content(self):

        strContent = getXMLTag("bankid", self.__bankId)
        strContent += getXMLTag("branchid", self.__branchId)
        strContent += getXMLTag("acctid", self.__id)
        strContent += getXMLTag("acctype", self.get_type())
        strContent += getXMLTag("acctkey", self.__key)

        return strContent


class Payee(OfxObject):

    def __init__(self, tagName="payeeid"):
        super(Payee, self).__init__(tagName)

        self.__name = None
        self.__payee = None
        self.__extendedName = None

    def get_name(self):
        return self.__name

    def get_payee(self):
        return self.__payee

    def get_extended_name(self):
        return self.__extendedName

    def set_name(self, value):
        self.__name = value

    def set_payee(self, value):
        self.__payee = value

    def set_extended_name(self, value):
        self.__extendedName = value

    def _get_content(self):

        strContent = ""

        if self.__name:
            strContent += getXMLTag("name", self.__name)
        else:
            strContent += getXMLTag("payee", self.__payee)
            strContent += getXMLTag("extdname", self.__extendedName)

        return strContent


class Balance(OfxObject):
    '''
    A balance
    '''

    def __init__(self, tagName="bal"):
        super(Balance, self).__init__(tagName)

        self.__amount = None
        self.__date = None

    def get_amount(self):
        '''
        Return:
            the amount of the balance
        '''
        return self.__amount

    def get_date(self):
        '''
        Return:
            (datetime) -- date of the balance
        '''
        return self.__date

    def set_amount(self, value):
        self.__amount = value

    def set_date(self, value):
        self.__date = value

    def _get_content(self):
        return "{amount}{date}".format(amount=getXMLTag("balamt",
                                                        self.__amount),
                                       date=getXMLTag("datasof",
                                                      strDate(self.__date)))
