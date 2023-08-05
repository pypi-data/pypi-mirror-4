#!/usr/bin/env python
"""\
Run a Sisow iDeal demo
2012-10-21 R.R. Nederhoed

This program demos the use of the Sisow API using python-sisow. It will open a 
browser window.

Make sure there is an `account-sisow.secret` file next to `demo.py`, with on the
first line the `merchantid` and on the second line your secret `merchantkey`:
123456789
abe6cdba7abe6523bcde87623fa54cd45ade2787etc

Default the program will run in testmode, ensuring no money will be transferred.
To override this, add --no-test:
$ demo.py --no-test
...

You can pick your own bank (issuer) using:
$ demo.py --list --no-test
Available banks
05 ING
09 Triodos Bank
$ demo.py --bank 09 --no-test
...
"""
import time
from datetime import datetime
import random
import webbrowser
import urllib


from sisow import sisow_account
from sisow import SisowAPI
from sisow import Transaction
from sisow import WebshopURLs

def list_banks(testmode=True):
    api = SisowAPI(None, None, testmode)
    print "Available banks"
    # Pick random bank from API
    for item in api.providers:
        print item['id'], item['name']

def run_demo(merchantid, merchantkey, amount, issuerid=None, testmode=True):
    api = SisowAPI(merchantid, merchantkey, testmode)
    
    if issuerid is None:
        # Pick random bank from API
        bank = random.choice(tuple(api.providers))
    else:
        for bank in api.providers:
            if bank['id'] == issuerid:
                break
    print "Picked %(name)s (%(id)s)" % bank
    entrance = datetime.now().strftime("E%Y%m%dT%H%M")
    
    # Build transaction
    t = Transaction(entrance, amount, bank['id'], entrance, 'Some demo product')
    
    #Send transaction
    urls = WebshopURLs('https://github.com/nederhoed/python-sisow/')
    response = api.start_transaction(t, urls)
    if not response.is_valid(merchantid, merchantkey):
        raise ValueError('Invalid SHA1')
    
    # Browser part
    url_ideal = urllib.url2pathname(response.issuerurl)
    print url_ideal
    webbrowser.open(url_ideal)
    
    while True:
        status = api.get_transaction_status(response.trxid)
        if not status.is_valid(merchantid, merchantkey):
            raise ValueError('Invalid SHA1')
        print datetime.now().strftime('%H:%M:%S'), status.status
        if status.status != 'Open':
            break
        time.sleep(5)

def main():
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--list", action="store_true", default=False,
                        help="show available banks")
    parser.add_argument("--no-test", action="store_true", default=False,
                        help="demo a real transaction")
    parser.add_argument("-f", type=str, default='account-sisow.secret',
                        metavar='FILENAME',
                        help="file with your Sisow account info: id on first line, secret key on second line")
    parser.add_argument("--bankid", type=str, default=None,
                        metavar='BANKID',
                        help="Bank ID, format '01' to '09'. Run `demo.py --list` for all available banks")
    parser.add_argument("--amount", type=int, default=123,
                        metavar='EUROCENT',
                        help="Amount in eurocents to demo, defaults to 123 (EUR 1,23)")
    args = parser.parse_args()
    
    # Extract merchant info
    if args.no_test:
        print "\nWARNING: testmode OFF\n"
    if args.list:
        list_banks(not args.no_test)
    else:
        # Run!
        (merchantid, merchantkey) = sisow_account(args.f)
        run_demo(merchantid, merchantkey, args.amount, args.bankid, not args.no_test)

if __name__ == "__main__":
    main()