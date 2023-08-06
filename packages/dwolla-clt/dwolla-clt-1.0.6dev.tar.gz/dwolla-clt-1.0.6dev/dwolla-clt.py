#!/usr/bin/python
import argparse
import shelve
import sys
import re
import webbrowser
from dwolla import DwollaUser, DwollaClientApp, DwollaAPIError

config = shelve.open('dwolla-clt')

# Helper functions
def pretty(d, indent=0):
    if type(d) is list:
        for i, item in enumerate(d):
            pretty_print(item, indent)
            if i < (len(d) - 1):
                print '--------------------------------'
    else:
        pretty_print(d, indent)

def pretty_print(d, indent=0):
    if d is not None and d != '':
        for key, value in d.iteritems():
            print str(key) + ": " + str(value)

def gatekeeper():
    if not config.has_key('token'):
        sys.exit("Please login first.")
        return

def is_email(email):
	if len(email) > 7:
		if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
			return True
	return False

def is_dwolla(dwollaId):
    return False    
    
# Main menu
def main():    
    args = parser.parse_args()
    args.func(args)

# Authentication
def logout(args):
    if config.has_key('token'):
        del config['token']
    if config.has_key('client_secret'):
        del config['client_secret']
    config.sync()
    print 'You are now logged out.'
    
def login(args):
    raw_input("Let's get you set up with an OAuth token. We'll send you off to a webpage where you can generate a token. Copy that and paste it in the next step.")
    webbrowser.open('http://developers.dwolla.com/dev/token')

    print ''
    token = raw_input('OAuth Token: ')
    config['token'] = token

    print ''
    print 'Awesome. You should be all set now. Try running "dwolla me"'

    config.sync()
    return True

def showconfig(args):
    pretty(config)
    return True

# User methods
def me(args):
    gatekeeper();
    print 'Fetching your account information...'
    pretty(DwollaUser(config['token']).get_account_info())

def send(args):
    gatekeeper()

    # Ask for required parameters
    while not args.destination_id:
        args.destination_id = raw_input('Destination ID: ')
    while not args.amount:
        args.amount = raw_input('Amount: ')
    while not args.pin:
        args.pin = raw_input('Your PIN: ')

    # Try to determine the destination type
    if is_dwolla(args.destination_id):
        isDwollaQ = raw_input('That destination looks like a Dwolla ID. Is this correct? [y/n] defaults to yes: ')
        if not isDwollaQ or isDwollaQ == 'y':
            args.destination_type = 'Dwolla'

    if is_email(args.destination_id):
        isEmailQ = raw_input('That destination looks like an email address. Is this correct? [y/n] defaults to no: ')
        if isEmailQ == 'y':
            args.destination_type = 'Email'

    # Start request
    print 'Sending...'

    # Required Parameters
    params = {}
    params['dest'] = args.destination_id
    params['amount'] = args.amount
    params['pin'] = args.pin

    # Optional Parameters
    if args.destination_type:
        params['dest_type'] = args.destination_type
    if args.notes:
        params['notes'] = args.notes
    if args.assume_costs:
        params['assume_cost'] = args.assume_costs

    # Send request and print response
    print DwollaUser(config['token']).send_funds(**params)
    print 'Sent!'

def request(args):
    gatekeeper()
    
    # Ask for required parameters
    while not args.source_id:
        args.source_id = raw_input('Source ID: ')
    while not args.amount:
        args.amount = raw_input('Amount: ')

    # Try to determine the destination type
    if is_dwolla(args.source_id):
        isDwollaQ = raw_input('That source looks like a Dwolla ID. Is this correct? [y/n] defaults to yes: ')
        if not isDwollaQ or isDwollaQ == 'y':
            args.source_type = 'Dwolla'

    if is_email(args.source_id):
        isEmailQ = raw_input('That source looks like an email address. Is this correct? [y/n] defaults to no: ')
        if isEmailQ == 'y':
            args.source_type = 'Email'

    # Start request
    print 'Requesting...'

    # Required Parameters
    params = {}
    params['source'] = args.source_id
    params['amount'] = args.amount
    params['pin'] = '' # remove when updating dwolla-lib

    # Optional Parameters
    if args.source_type:
        params['source_type'] = args.source_type
    if args.notes:
        params['notes'] = args.notes

    # Send request and print response
    print DwollaUser(config['token']).request_funds(**params)
    print 'Requested!'

def requests(args):
    gatekeeper()

    if args.request_id:
        if args.cancel:
            if raw_input('Are you sure you wish to cancel this request? [y/n] defaults to no: ') == 'y':
                print 'Canceling request with ID "%s"...' % args.request_id
                DwollaUser(config['token']).cancel_request(args.request_id)
                return pretty('Request canceled!')
        if args.fulfill:
            return pretty('too bad')
        else:
            print 'Retrieving request with ID "%s"...' % args.request_id
            return pretty(DwollaUser(config['token']).get_request(args.request_id))
    else:
        print 'Retrieving requests...'
        return pretty(DwollaUser(config['token']).get_pending_requests())

def fundingSources(args):
    gatekeeper()

    if args.funding_id:
        print 'Retrieving funding source with ID "%s"...' % args.funding_id
        pretty(DwollaUser(config['token']).get_funding_source(args.funding_id))
    else:
        print 'Retrieving funding sources...'
        pretty(DwollaUser(config['token']).get_funding_sources())

def transactions(args):
    gatekeeper()

    if args.transaction_id:
        print 'Retrieving transaction with ID "%s"...' % args.transaction_id
        pretty(DwollaUser(config['token']).get_transaction(args.transaction_id))
    else:
        print 'Retrieving transactions...'
        pretty(DwollaUser(config['token']).get_transaction_list())

def balance(args):
    gatekeeper()
    print 'Retrieving balance...'
    print 'Your account balance is: $' + str(DwollaUser(config['token']).get_balance())


# Init CLT
parser = argparse.ArgumentParser(description='Dwolla tools.')
subparsers = parser.add_subparsers()

# Subcommand: Login
login_parser = subparsers.add_parser('login', help='Authenticate')
login_parser.set_defaults(func=login)

# Subcommand: Logout
logout_parser = subparsers.add_parser('logout', help='Logout')
logout_parser.set_defaults(func=logout)

# Subcommand: Config
config_parser = subparsers.add_parser('config', help='Show config')
config_parser.set_defaults(func=showconfig)

# Subcommand: Send
send_parser = subparsers.add_parser('send', help='Send money')
send_parser.add_argument('-d', '--destination-id', metavar='destination_id', dest='destination_id', help='Destination ID')
send_parser.add_argument('-t', '--destination-type', metavar='destination_type', dest='destination_type', help='Destination Type', default=None)
send_parser.add_argument('-a', '--amount', metavar='amount', dest='amount', help='Amount')
send_parser.add_argument('-p', '--pin', metavar='pin', dest='pin', help='PIN')
send_parser.add_argument('-c', '--assume-costs', metavar='assume_costs', dest='assume_costs', help='Assume Costs?', default=False)
send_parser.add_argument('-n', '--notes', metavar='notes', dest='notes', help='Notes', default=None)
send_parser.set_defaults(func=send)

# Subcommand: Request
request_parser = subparsers.add_parser('request', help='Request money')
request_parser.add_argument('-d', '--source-id', metavar='source_id', dest='source_id', help='Source ID')
request_parser.add_argument('-t', '--source-type', metavar='source_type', dest='source_type', help='Source Type', default=None)
request_parser.add_argument('-a', '--amount', metavar='amount', dest='amount', help='Amount')
request_parser.add_argument('-n', '--notes', metavar='notes', dest='notes', help='Notes', default=None)
request_parser.set_defaults(func=request)

# Subcommand: Requests
requests_parser = subparsers.add_parser('requests', help='Money requests')
requests_parser.add_argument('request_id', nargs='?', default=None, help='Request ID')
requests_parser.add_argument('-c', '--cancel', dest='cancel', action='store_true', help='Cancel Request')
requests_parser.add_argument('-f', '--fulfill', dest='fulfill', action='store_true', help='Fulfill Request')
requests_parser.set_defaults(func=requests)

# Subcommand: Transactions
transactions_parser = subparsers.add_parser('transactions', help='Transactions')
transactions_parser.add_argument('transaction_id', nargs='?', help='Transaction ID', default=None)
transactions_parser.set_defaults(func=transactions)

# Subcommand: Me
me_parser = subparsers.add_parser('me', help='My information')
me_parser.set_defaults(func=me)

# Subcommand: Balance
balance_parser = subparsers.add_parser('balance', help='Account balance')
balance_parser.set_defaults(func=balance)

# Subcommand: Funding
funding_parser = subparsers.add_parser('funding', help='Funding source(s)')
funding_parser.add_argument('funding_id', nargs='?', help='Funding Source ID', default=None)
funding_parser.set_defaults(func=fundingSources)

# Start CLT, and wrap for exceptions
try:
    main()
except DwollaAPIError:
    print 'Oops, Dwolla said: ', sys.exc_info()[1]