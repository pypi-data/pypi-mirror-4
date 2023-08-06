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
        :param tagName: name for the XML tag
        :type tagName: :class:`str`
        '''
        self._tagName = tagName

    def _get_content(self):
        '''
        :rtype: the xml representation of this object
        '''
        return ""

    def get_tag_name(self):
        '''
        :rtype: the XML tag name
        '''
        return self._tagName

    def set_tag_name(self, name):
        '''
        Set a XML tag name for this object

        :param name: name for the XML tag
        :type name: :class:`str`
        '''
        self._tagName = name

    def __str__(self):
        '''
        :rtype: XML representation of the object
        '''
        # return getXMLTag(self._tagName, self._get_content())
        return self._get_content()


class File(OfxObject):
    '''
    An OFX file

    >>> from csb43.ofx import File
    >>> f = File()
    >>> print f
    <?xml version="1.0" encoding="ASCII"?>
    <?OFX OFXHEADER="200" VERSION="211" SECURITY="NONE"
    OLDFILEUID="NONE" NEWFILEUID="NONE"?><OFX><BANKMSGSRSV1></BANKMSGSRSV1></OFX>
    '''

    def __init__(self, tagName="ofx"):
        '''
        :param tagName: tag's name to be used for this object
        :type tagName: :class:`str`
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
        :rtype: :class:`list` of :class:`Response`
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

        :param value: a response object to include in this object
        :type value: :class:`Response`
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
        :param tagName: name for the XML tag
        :type tagName: :class:`str`
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
        :rtype: :class:`pycountry.dbCurrency` -- Default currency for the statement
        '''
        return self.__currency

    def get_bank_account_from(self):
        '''
        :rtype: :class:`BankAccount` -- Account-from aggregate
        '''
        return self.__accountFrom

    def get_transaction_list(self):
        '''
        :rtype: :class:`TransactionList` -- Statement-transaction-data aggregate
        '''
        return self.__transactionList

    def get_ledger_balance(self):
        '''
        :rtype: :class:`Balance` -- the ledger balance aggregate
        '''
        return self.__ledgerBalance

    def get_available_balance(self):
        '''
        :rtype: `Balance` -- the available balance aggregate
        '''
        return self.__availableBalance

    def get_balances(self):
        '''
        :rtype: :class:`list` of miscellaneous other :class:`Balance` s
        '''
        return self.__balances

    def get_mktginfo(self):
        '''
        :rtype: marketing info
        '''
        return self.__mktginfo

    def set_currency(self, value):
        '''
        :param value: currency
        :type value: :class:`pycountry.db.Currency`
        '''
        self.__currency = value

    def set_bank_account_from(self, value):
        '''
        :param value: value
        :type value: :class:`BankAccount`
        '''
        self.__accountFrom = value

    def set_transaction_list(self, value):
        '''
        :param value: transactions list
        :type value: :class:`TransactionList`
        '''
        self.__transactionList = value

    def set_ledger_balance(self, value):
        '''
        :param value: ledger balance
        :type value: :class:`Balance`
        '''
        self.__ledgerBalance = value

    def set_available_balance(self, value):
        '''
        :param value: available balance
        :type  value: :class:`Balance`
        '''
        self.__availableBalance = value

    def add_balance(self, value):
        '''
        Add a complementary balance

        :param value: a complementary balance
        :type  value: :class:`Balance`
        '''
        self.__balances.append(value)

    def set_mktginfo(self, value):
        '''
        :param value: marketing info
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
        :rtype: :class:`datetime.datetime` -- date of the first transaction
        '''
        return self.__dateStart

    def get_date_end(self):
        '''
        :rtype: :class:`datetime.datetime` -- date of the first transaction
        '''
        return self.__dateEnd

    def get_list(self):
        '''
        :rtype: :class:`list` of :class:`Transaction`
        '''
        return self.__list

    def set_date_start(self, value):
        '''
        :param value: date of start
        :type  value: :class:`datetime.datetime`
        '''
        self.__dateStart = value

    def set_date_end(self, value):
        '''
        :param value: date of end
        :type  value: :class:`datetime.datetime`
        '''
        self.__dateEnd = value

    def add_transaction(self, value):
        '''
        Add a new transaction to the list

        :param value: a transaction
        :type  value: :class:`Transaction`
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

    #: type of transaction
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
        :param tagName: see :class:`OfxObject`
        :type  tagName: :class:`str`
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
        :rtype: :class:`str` -- name of payee or description of transaction
        '''
        return self.__name

    def get_extended_name(self):
        '''
        :rtype: :class:`str` -- extended name of payee or description of transaction
        '''
        return self.__extendedName

    def set_name(self, value):
        '''
        :param value: name of payee or description of transaction
        '''
        self.__name = value

    def set_extended_name(self, value):
        '''
        :param value: extended name of payee or description of transaction
        '''
        self.__extendedName = value

    def get_ref_num(self):
        '''
        :rtype: :class:`str` -- reference number that uniquely indentifies the transaction.
        '''
        return self.__refNum

    def set_ref_num(self, value):
        '''
        :param value: reference number that uniquely indentifies the transaction.
        '''
        self.__refNum = value

    def get_type(self):
        '''
        :rtype: :class:`str` -- transaction type. See :class:`TYPE`. Default ('OTHER')
        '''
        if self.__type is None:
            return Transaction.TYPE[-1]
        else:
            return self.__type

    def get_date_posted(self):
        '''
        :rtype: :class:`datetime.datetime` -- date transaction was posted to account
        '''
        return self.__datePosted

    def get_date_initiated(self):
        '''
        :rtype: :class:`datetime.datetime` -- date user initiated transaction
        '''
        return self.__dateInitiated

    def get_date_available(self):
        '''
        :rtype: :class:`datetime.datetime` -- date funds are available
        '''
        return self.__dateAvailable

    def get_amount(self):
        '''
        :rtype: number -- amount of transaction
        '''
        return self.__amount

    def get_transaction_id(self):
        '''
        :rtype: :class:`str` -- transaction ID issued by financial institution
        '''
        return self.__transactionId

    def get_correct_fit_id(self):
        '''
        correct fit id
        '''
        return self.__correctFitId

    def get_correct_action(self):
        '''
        correct action
        '''
        return self.__correctAction

    def get_server_tid(self):
        '''
        server transaction id
        '''
        return self.__serverTid

    def get_check_num(self):
        '''
        :rtype: :class:`str` -- check (or other reference) number
        '''
        return self.__checkNum

    def get_standard_industrial_code(self):
        '''
        standard industrial code
        '''
        return self.__standardIndustrialCode

    def get_payee(self):
        '''
        :rtype: :class:`Payee`
        '''
        return self.__payee

    def get_payeeid(self):
        '''
        :rtype: :class:`str` -- payee identifier
        '''
        return self.__payeeid

    def get_bank_account_to(self):
        '''
        :rtype: :class:`BankAccount` -- account the transaction is transferring to
        '''
        return self.__bankAccountTo

    def get_cc_account_to(self):
        '''
        cc account to
        '''
        return self.__ccAccountTo

    def get_memo(self):
        '''
        :rtype: :class:`str` -- extra information
        '''
        return self.__memo

    def get_image_data(self):
        '''
        image data
        '''
        return self.__imageData

    def get_currency(self):
        '''
        :rtype: :class:`pycountry.db.Currency` -- currency of the transaction, if different from the one in :class:`BankAccount`
        '''
        return self.__currency

    def get_origin_currency(self):
        '''
        :rtype: :class:`pycountry.db.Currency` -- currency of the transaction, if different from the one in :class:`BankAccount`
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

    #: account type
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
        :rtype: :class:`str` -- type of account. See :class:`TYPE` (default *'SAVINGS'*)
        '''
        if self.__type is None:
            return BankAccount.TYPE[1]
        else:
            return self.__type

    def get_key(self):
        '''
        :rtype: :class:`str` -- checksum (Spain: digitos de control)
        '''
        return self.__key

    def set_type(self, value):
        '''
        :param value: type of account
        :type  value: :class:`str`
        '''
        self.__type = value

    def set_key(self, value):
        '''
        :param value: checksum
        '''
        self.__key = value

    def get_bank(self):
        '''
        :rtype: :class:`str` -- bank identifier (Spain: banco, entidad)
        '''
        return self.__bankId

    def get_branch(self):
        '''
        :rtype: :class:`str` -- branch identifier (Spain: sucursal, oficina)
        '''
        return self.__branchId

    def get_id(self):
        '''
        :rtype: :class:`str` -- account identifier
        '''
        return self.__id

    def set_bank(self, value):
        '''
        :param value: bank identifier
        '''
        self.__bankId = value

    def set_branch(self, value):
        '''
        :param branch: branch identifier
        '''
        self.__branchId = value

    def set_id(self, value):
        '''
        :param value: account id
        '''
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
        :rtype: the amount of the balance
        '''
        return self.__amount

    def get_date(self):
        '''
        :rtype: :class:`datetime` -- date of the balance
        '''
        return self.__date

    def set_amount(self, value):
        '''
        :param value: amount
        '''
        self.__amount = value

    def set_date(self, value):
        '''
        :param value: a date object
        :type  value: :class:`datetime.datetime`
        '''
        self.__date = value

    def _get_content(self):
        return "{amount}{date}".format(amount=getXMLTag("balamt",
                                                        self.__amount),
                                       date=getXMLTag("datasof",
                                                      strDate(self.__date)))

