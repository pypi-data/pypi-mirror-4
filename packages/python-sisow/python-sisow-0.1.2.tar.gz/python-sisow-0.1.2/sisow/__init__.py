"""\
iDeal implementation in Python for the Sisow Payment provider


1. DirectoryRequest
het opvragen van de aangesloten iDEAL banken (alleen voor iDEAL);
2. TransactionRequest
het opvragen van de URL voor het starten van een transactie;
3. StatusRequest
het opvragen van de status van een transactie;

NOT IMPLEMENTED
4. RefundRequest: 
retourneer een iDEAL transactie, geheel of gedeeltelijk;

5. CancelReservation: annuleren van een Sisow ecare reservering;
6. InvoiceRequest: aanmaken van de Sisow ecare factuur;
7. CreditInvoiceRequest: aanmaken van een Sisow ecare creditnota;

TODO: tests
TODO: more error handling
"""
from lxml import etree
import hashlib

import urllib
import urllib2

def _xml_request(url, data=None):
    if data is not None:
        data = urllib.urlencode(data)
        req = urllib2.Request(url, data)
    else:
        req = urllib2.Request(url)
    stream = urllib2.urlopen(req)
    return etree.parse(stream)

def _sha1_signature(signature, data, secret):
    """\
    `signature` is a string to be formatted with given data
    secret is the key that will be used as a last update, to sign the SHA1 hash.
    >>> data {'trxid': 'abcdef0123456789'}
    >>> _sha_signature('%(trxid)s', data, secret)
    """
    sha1 = hashlib.sha1(signature % data)
    sha1.update(secret)
    return sha1.hexdigest()

def _signature(keys):
    """Generate a signature format string for the give keys 
    >>> keys = ('trxid', 'shopid', 'merchantid')
    >>> _signature(keys)
    '%(trxid)s%(shopid)s%(merchantid)s'
    """
    parts = ['%%(%s)s'%i for i in keys]
    return ''.join(parts)

class WebshopURLs(object):
    """\ """
    def __init__(self, returnurl, cancelurl='', notifyurl='', callbackurl=''):
        """Constructor """
        self.returnurl = returnurl
        self.cancelurl = cancelurl
        self.notifyurl = notifyurl
        self.callbackurl = callbackurl


class Transaction(object):
    """\
    
    """
    def __init__(self, purchaseid, amount, issuerid, entrancecode='', description=''):
        """TODO: validation of parameters 
        
        `entrancecode` is optional
        `description` is optional
        """
        self.shopid = ''
        self.payment = ''  # Empty string indicates iDeal
        self.purchaseid = purchaseid
        self.amount = amount  # Amount in cents
        self.issuerid = issuerid
        self.entrancecode = entrancecode
        self.description = description
        # Will be set in SisowAPI.start_transaction
        self.merchantid = ''
        self.testmode = False
    
    def sha1(self, merchantkey):
        """\
        Return SHA1 value for:
        purchaseid/entrancecode/amount/shopid/merchantid/merchantkey
        """
        signature = _signature(('purchaseid', 'entrancecode', 'amount',
                                'shopid', 'merchantid'))
        return _sha1_signature(signature, self.__dict__, merchantkey)
        
    def __str__(self):
        return str(self.__dict__)

class SisowAPI(object):
    """\
    Sisow API abstraction 
    
    
    TODO: embed documentation in docstrings
    TODO: GET or POST method as class variable
    """
    _url_api = 'https://www.sisow.nl/Sisow/iDeal/RestHandler.ashx/'
    _xmlns = 'https://www.sisow.nl/Sisow/REST'
    
    def __init__(self, merchantid, merchantkey, testmode=False):
        """\
        Pass your Sisow credentials.
        With testmode=True, Sisow will process your transaction as a test and no
        money will be withdrawn.
        """
        self.merchantid = merchantid
        self.merchantkey = merchantkey
        self._testmode = testmode
    
    @property
    def providers(self):
        call = 'DirectoryRequest'
        xml = _xml_request(self._url_api+call, data={'test': self._testmode})
        for issuer in xml.iter('{%s}issuer'%SisowAPI._xmlns):
            yield {'id': issuer[0].text, 'name': issuer[1].text}
    
    def start_transaction(self, transaction, urls):
        call = 'TransactionRequest'
        assert isinstance(transaction, Transaction)
        # Testmode
        transaction.testmode = 'true' if self._testmode else ''
        # Add additional attributes
        transaction.merchantid = self.merchantid
        # Extract query parameters, a bit hacky
        data = {}
        data.update(transaction.__dict__)
        data.update(urls.__dict__)
        # SHA encoding!
        data['sha1'] = transaction.sha1(self.merchantkey)
        # Cleanup
        for key in data.keys():
            if data[key] is '':
                del(data[key])
        xml = _xml_request(self._url_api+call, data)
        return TransactionResponse(xml)
    
    def get_transaction_status(self, trxid, shopid=''):
        """\
        https://www.sisow.nl/Sisow/iDeal/RestHandler.ashx/StatusRequest?trxid=...&shopid=...&merchantid=...&sha1=...
        
        trxid: de Transaction ID van de transactie
        shopid: (nabije toekomst) de unieke ID van de webshop
        """
        call = 'StatusRequest'
        data = {
            'trxid': trxid,
            'shopid': shopid,
            'merchantid': self.merchantid,
        }
        # SHA encoding!
        signature = '%(trxid)s%(shopid)s%(merchantid)s'
        data['sha1'] = _sha1_signature(signature, data, self.merchantkey)
        xml = _xml_request(self._url_api+call, data)
        return StatusResponse(xml)
    
class Response(object):
    """General response base class 
    
    TODO: factory class method to `from_xml` that instantiates the corresponding
    TODO: response class from an XML message.
    """
    def __init__(self, xml):
        """Constructor of Response base class
        
        Define extra class attributes in your subclass. For example:
        self.trxid = ''
        Set the signature to be used for sha1 validation. For example:
        self._signature = '%(trxid)s%(merchantid)s'
        Do not add the secret `merchantkey` to the signature, it will be added
        implicitly.
        """
        self._xml = xml
        self.sha1 = ''
        # Define _signature in subclass
        self._signature = None
        # Detect errorresponse
        root = xml.getroot()
        if root.tag == "{%s}errorresponse" % SisowAPI._xmlns:
            raise ErrorResponse(xml)
    
    def _process_xml(self):
        """Fill the class attributes from XML 
        Read all elements at the second level and set them on the object, if 
        the class has the element as an attribute.
        
        Call `_process_xml` from the constructor of your subclass.
        """
        offset = 2 + len(SisowAPI._xmlns)  # Strip namespace from element
        # Level 2 elements:
        for element in self._xml.findall(".//*/*"):
            tag = element.tag[offset:]
            if tag in self.__dict__:
                # Replace None with empty string!
                self.__dict__[tag] = element.text or ''
    
    def _validate_type(self, root_element):
        """Raise a ValueError if the root element does not correspond 
        
        Call from the constructor of your subclass.
        """
        root = self._xml.getroot()
        if not root.tag == "{%s}%s" % (SisowAPI._xmlns, root_element):
            msg = 'Root node not "%s".\n\n' % root_element
            raise ValueError(msg+etree.tostring(xml))
    
    def is_valid(self, merchantid, merchantkey):
        """\
        Validate the SHA1 using our merchantid and secret merchantkey
        """
        data = dict(merchantid=merchantid)
        data.update(self.__dict__)
        try:
            sha1 = _sha1_signature(self._signature, data, merchantkey)
        except TypeError:
            # Ensure `self._signature` has a string value.
            raise ValueError('Response._signature has not been set.')
        return sha1 == self.sha1
        
class TransactionResponse(Response):
    """Specific transaction respons.
    
    From Sisow PDF documentation 3.2.1 page 10:
    <?xml version="1.0" encoding="UTF-8"?>
    <transactionresponse xmlns="https://www.sisow.nl/Sisow/REST" version="1.0.0">
        <transaction>
            <issuerurl>IssuerURL</issuerurl>
            <trxid>TransactionID</trxid>
        </transaction>
        <signature>
            <sha1>SHA1 trxid + issuerurl + merchantid + merchantkey</sha1>
        </signature>
    </transactionresponse>
    
    TODO: Sisow server is returning a transactionrequest!!!
    """
    def __init__(self, xml):
        """Constructor  """
        # Superclass will also fill `trxid` and `issuerurl` from XML
        super(TransactionResponse, self).__init__(xml)
        # Initiate
        self.issuerurl = ''
        self.trxid = ''
        # Validation
        # <sha1>SHA1 trxid + issuerurl + merchantid + merchantkey</sha1>
        # merchantkey will be added implicitly in `_sha_signature`
        self._signature = "%(trxid)s%(issuerurl)s%(merchantid)s"
        # Process XML to fill object attributes
        self._process_xml()
        # Root element validation
        self._validate_type('transactionrequest')

class StatusResponse(Response):
    """Specific transaction status respons.
    
    From Sisow PDF documentation 3.2.1 page 14:
    
    <?xml version="1.0" encoding="UTF-8"?>
    <statusresponse xmlns="https://www.sisow.nl/Sisow/REST" version="1.0.0">
        <transaction>
            <trxid>TransactionID</trxid>
            <status>Status</status>
            <amount>Bedrag in centen</amount>
            <purchaseid>Kenmerk</purchaseid>
            <description>Omschrijving</description>
            <entrancecode>EntranceCode</entrancecode>
            <timestamp>Tijdstip</timestamp>
            <consumername>Naam rekeninghouder</consumername>
            <consumeraccount>Bankrekening</consumeraccount>
            <consumercity>Plaats rekening</consumercity>
        </transaction>
        <signature>
            <sha1>SHA1 trxid + status + amount + purchaseid + entrancecode +
        consumeraccount + merchantid + merchantkey</sha1>
        </signature>
    </statusresponse>
    """
    def __init__(self, xml):
        """Constructor  """
        # Superclass will also fill `trxid` and `issuerurl` from XML
        super(StatusResponse, self).__init__(xml)
        # Initiate
        self.trxid = ''
        self.status = ''
        self.amount = ''
        self.purchaseid = ''
        self.description = ''
        self.entrancecode = ''
        self.timestamp = ''
        self.consumername = ''
        self.consumeraccount = ''
        self.consumercity = ''
        # Validation
        self._signature = _signature(('trxid', 'status', 'amount',
                                      'purchaseid', 'entrancecode',
                                      'consumeraccount', 'merchantid'))
        # Process XML to fill object attributes
        self._process_xml()
        # Root element validation
        self._validate_type('statusresponse')

class ErrorResponse(Exception):
    def __init__(self, xml):
        # Extract info from XML
        ns = SisowAPI._xmlns
        code = xml.find(".//{%s}errorcode"%ns).text
        message = xml.find(".//{%s}errormessage"%ns).text
        super(ErrorResponse, self).__init__("%s %s"%(code, message))
        self.code = code
        self.message = message

def sisow_account(filename):
    with file(filename) as f:
        return f.readline().strip(), f.readline().strip()

