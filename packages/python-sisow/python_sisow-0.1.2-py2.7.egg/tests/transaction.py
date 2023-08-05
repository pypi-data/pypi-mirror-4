"""\
"""
import unittest
from StringIO import StringIO

from lxml import etree

from sisow import Transaction
from sisow import Response, ErrorResponse
from sisow import TransactionResponse
from sisow import StatusResponse


class TestTransactionSha1FromManual(unittest.TestCase):
    """\
    # SHA! value copied from the Sisow manual 3.2.1 page 10
    
    https://www.sisow.nl/Sisow/iDeal/RestHandler.ashx/TransactionRequest?shopid=&merchantid
=0123456&purchaseid=123456789&amount=1000&payment=ecare&entrancecode=uniqueentrance&descriptio
n=Bestelling+webshop.nl&returnurl=http%3a%2f%2fwww.webshop.nl&callbackurl=http%3a%2f%2fwww.webshop.nl%2f/ca
llback&sha1=cb2461bd40ed1a77a6d837a560bfcbc3e03d6c3c

    #sha1("123456789uniqueentrance10000123456b36d8259346eaddb3c03236b37ad3a1d7a67cec6")

    """
    def setUp(self):
        self.transaction = Transaction('123456789', 1000, '01', 'uniqueentrance')
        self.transaction.merchantid = '0123456'
        self.merchantkey = 'b36d8259346eaddb3c03236b37ad3a1d7a67cec6'
    
    def test_sha1_value(self):
        outcome = 'cb2461bd40ed1a77a6d837a560bfcbc3e03d6c3c'
        self.assertEqual(self.transaction.sha1(self.merchantkey), outcome)


class TestErrorResponse(unittest.TestCase):
    error = """\
<errorresponse xmlns="https://www.sisow.nl/Sisow/REST" version="1.0.0">
<error><errorcode>TEST</errorcode><errormessage>MESSAGE</errormessage></error>
</errorresponse>"""
    def setUp(self):
        self._xml = etree.parse(StringIO(TestErrorResponse.error))
    
    def test_error_from_xml(self):
        response = ErrorResponse(self._xml)
        self.assertEqual(response.code, 'TEST')
        self.assertEqual(response.message, 'MESSAGE')


class TestResponses(unittest.TestCase):
    response = """<errorresponse xmlns="https://www.sisow.nl/Sisow/REST" version="1.0.0"><error><errorcode>TA3340</errorcode><errormessage>SHA1 incorrect</errormessage></error></errorresponse>"""
    def setUp(self):
        self._xml = etree.parse(StringIO(TestResponses.response))
    
    def test_detect_error_response(self):
        self.assertRaises(ErrorResponse, Response, self._xml)
    
    def test_detect_error_transactionresponse(self):
        self.assertRaises(ErrorResponse, TransactionResponse, self._xml)
    
    def test_detect_error_statusresponse(self):
        self.assertRaises(ErrorResponse, StatusResponse, self._xml)


class TestTransactionResponse(unittest.TestCase):
    response = """\
<transactionrequest xmlns="https://www.sisow.nl/Sisow/REST" version="1.0.0">
<transaction>
<issuerurl>https%3a%2f%2fwww.sisow.nl%2fSisow%2fiDeal%2fSimulator.aspx%3fmerchantid%3d2537492455%26txid%3dTEST080484779698%26sha1%3dbb9e98fff00960aa705560a56ff9c64e8e764b41</issuerurl>
<trxid>TEST080484779698</trxid>
</transaction>
<signature><sha1>f451df1bcb8a0c1c578a0778401ad686caa535b2</sha1></signature>
</transactionrequest>"""
    def setUp(self):
        self._xml = etree.parse(StringIO(TestTransactionResponse.response))
    
    def test_transactionresponse_values(self):
        response = TransactionResponse(self._xml)
        self.assertEquals(response.trxid, 'TEST080484779698')
        self.assertEquals(
            response.issuerurl,
            'https%3a%2f%2fwww.sisow.nl%2fSisow%2fiDeal%2fSimulator.aspx%3fmerchantid%3d2537492455%26txid%3dTEST080484779698%26sha1%3dbb9e98fff00960aa705560a56ff9c64e8e764b41'
        )
        self.assertEquals(response.sha1, 'f451df1bcb8a0c1c578a0778401ad686caa535b2')


class TestTransactionResponseFromManual(unittest.TestCase):
    """\
    # SHA! value copied from the Sisow manual 3.2.1 page 10
    """
    response = """\
<transactionrequest xmlns="https://www.sisow.nl/Sisow/REST" version="1.0.0">
<transaction>
<issuerurl>https%3a%2f%2fbetalen.rabobank.nl%2fide%2fide.cgi%3fX009%3dBETAAL%26X010%3d20%26X015%3d%26V020%3d0050000513599081%26V022%3d01%26V021%3d9470173121213998</issuerurl>
<trxid>0050000513599081</trxid>
</transaction>
<signature><sha1>10bc163e9cb2050297514ad4db320ec1a16074d4</sha1></signature>
</transactionrequest>"""
    def setUp(self):
        self._xml = etree.parse(StringIO(TestTransactionResponseFromManual.response))
        self.merchantid = '0123456'
        self.merchantkey = 'b36d8259346eaddb3c03236b37ad3a1d7a67cec6'
    
    def test_transactionresponse_values(self):
        response = TransactionResponse(self._xml)
        self.assertEquals(response.trxid, '0050000513599081')
        self.assertEquals(
            response.issuerurl,
            'https%3a%2f%2fbetalen.rabobank.nl%2fide%2fide.cgi%3fX009%3dBETAAL%26X010%3d20%26X015%3d%26V020%3d0050000513599081%26V022%3d01%26V021%3d9470173121213998'
        )
        self.assertEquals(response.sha1, '10bc163e9cb2050297514ad4db320ec1a16074d4')
    
    def test_transactionresponse_valid_sha1(self):
        response = TransactionResponse(self._xml)
        outcome = response.is_valid(self.merchantid, self.merchantkey)
        self.assertEquals(outcome, True)



