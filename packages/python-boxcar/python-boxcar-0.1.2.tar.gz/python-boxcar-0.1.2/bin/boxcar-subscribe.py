#!/usr/bin/env python

from boxcar import Provider
from boxcar.exc import UserAlreadySubscribed, UserDoesNotExist
import argparse
import sys

parser = argparse.ArgumentParser(
    description='Subscribe a user to a Boxcar.io provider.')
parser.add_argument('--key', help='the Boxcar.io API key', required=True)
parser.add_argument('--email', help='the Boxcar.io user email address.',
    required=True)
args = parser.parse_args()

p = Provider(key=args.key)
try:
    p.subscribe(email=args.email)
except UserAlreadySubscribed:
    print 'User %s is already subscribed to this provider.' % (
        args.email)
    sys.exit(1)
except UserDoesNotExist:
    print 'User %s is not a registered Boxcar.io user.' % (
        args.email)
    sys.exit(1)
except Exception as e:
    print 'Unknown error: %s' % e
    sys.exit(1)
else:
    print 'User %s subscribed successfully.' % args.email
