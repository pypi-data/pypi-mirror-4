"""\
General tests on general functions in python-sisow
"""
from unittest import TestCase

from hashlib import sha1

#import sisow
from sisow import _signature
from sisow import _sha1_signature


class TestSignature(TestCase):
    def setUp(self):
        self.keys = ('trxid', 'shopid', 'merchantid')
        self.signature = '%(trxid)s%(shopid)s%(merchantid)s'
        self.data = {
            'trxid': 'abcdef0123456789',
            'shopid': '3',
            'merchantid': '132435'
        }
    
    def test_empty(self):
        self.assertEqual(_signature([]), '')
    
    def test_multiple(self):
        self.assertEqual(_signature(self.keys), self.signature)
    
    def test_sha1_empty(self):
        outcome = sha1('').hexdigest()
        self.assertEquals(_sha1_signature('', {}, ''), outcome)
    
    def test_sha1(self):
        signature = _signature(self.keys)
        outcome = sha1(self.signature % self.data).hexdigest()
        self.assertEquals(_sha1_signature(self.signature, self.data, ''),
                          outcome)
    
    def test_sha1_secret(self):
        secret = 'geheim'
        signature = _signature(self.keys)
        outcome = sha1(self.signature % self.data)
        outcome.update(secret)
        outcome = outcome.hexdigest()
        self.assertEquals(_sha1_signature(self.signature, self.data, secret),
                          outcome)
 