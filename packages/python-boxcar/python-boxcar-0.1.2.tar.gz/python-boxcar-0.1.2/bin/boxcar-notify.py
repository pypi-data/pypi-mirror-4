#!/usr/bin/env python

from boxcar import Provider
from boxcar.exc import UserNotSubscribed, UserDoesNotExist
import argparse
import sys
import random

parser = argparse.ArgumentParser(
    description='Send a Boxcar.io notification.')
parser.add_argument('--key', help='the Boxcar.io API key', required=True)
parser.add_argument('--email', help='the Boxcar.io user email addresses',
    nargs='+', required=True)
parser.add_argument('--from', help='a string identifying the sender',
    dest='from_screen_name', required=True)
parser.add_argument('--message', help='the message body', required=True)
parser.add_argument('--id',
    help='a unique ID to help deduplicate. random int by default',
    default=random.randint(0, 4294967295))
parser.add_argument('--source_url', help='URL to send user to')
parser.add_argument('--icon_url',
        help='URl for icon to display with message')
args = parser.parse_args()

p = Provider(key=args.key)
try:
    p.notify(
        emails=args.email,
        from_screen_name=args.from_screen_name,
        message=args.message,
        from_remote_service_id=args.id,
        source_url=args.source_url,
        icon_url=args.icon_url)
except UserNotSubscribed:
    print 'User %s is not subscribed to this provider.' % (
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
    print 'Sent.'
