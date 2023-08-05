# -*- coding: utf-8 -*-
"""pypel.cli, CLI interface for pypel.

THIS SOFTWARE IS UNDER BSD LICENSE.
Copyright (c) 2012 Daniele Tricoli <eriol@mornie.org>

Read LICENSE for more informations.
"""

import argparse
import time
import os
import warnings

from datetime import datetime

try:
    from pygments.console import ansiformat
except ImportError:
    ansiformat = None

from pypel import get_version
try:
    from pypel.gpg import sign, verify
    gnupg = True
except ImportError:
    gnupg = False
from pypel.models import (delete_metadata, set_metadata, make_receipt,
    DoesNotExist, IsADirectory, ImageNotSupported)

PYPELKEY = os.environ.get('PYPELKEY')

def make_parsers():
    """Create the parsers for the CLI tool."""

    parser = argparse.ArgumentParser(description='Easy receipts management.',
                                     version=get_version())
    subparsers = parser.add_subparsers(dest='command_name', help='commands')

    # A show command
    show_parser = subparsers.add_parser('show', help='Show receipts\' metadata')
    show_parser.add_argument('-v', '--verify', action='store_true',
                             help='verify receipts')
    show_parser.add_argument('-c', '--color', action='store_true',
                             help='colorize the output')
    show_parser.set_defaults(action=do_show)

    # A set command
    set_parser = subparsers.add_parser('set', help='Set receipts\' metadata')
    set_parser.add_argument('-p', '--price', action='store', type=float,
                            help='set receipts\' price')
    set_parser.add_argument('-r', '--retailer', action='store', type=str,
                            help='set receipts\' retailer')
    set_parser.set_defaults(action=do_set)

    # A delete command
    del_parser = subparsers.add_parser('del', help='Delete receipts\' metadata')
    del_parser.add_argument('-p', '--price', action='store_true',
                            help='delete receipts\' price')
    del_parser.add_argument('-r', '--retailer', action='store_true',
                            help='delete receipts\' retailer')
    del_parser.set_defaults(action=do_del)

    # A sum command
    sum_parser = subparsers.add_parser('sum', help='Sum receipts\' price')
    sum_parser.set_defaults(action=do_sum)

    # A gpg command
    gpg_parser = subparsers.add_parser('gpg', help='Sign or verify receipts')
    gpg_group = gpg_parser.add_mutually_exclusive_group()
    gpg_group.add_argument('-s', '--sign', action='store_true',
                            help='sign receipts')
    gpg_group.add_argument('-v', '--verify', action='store_true',
                            help='verify receipts')
    gpg_parser.set_defaults(action=do_gpg)

    all_subparsers = dict(
        show_parser=show_parser,
        set_parser=set_parser,
        del_parser=del_parser,
        sum_parser=sum_parser,
        gpg_parser=gpg_parser)

    # HACK: This can be fixed when http://bugs.python.org/issue9540 will be
    # closed.
    for subparser in all_subparsers:
        all_subparsers[subparser].add_argument('receipts',
                                               metavar='receipt',
                                               nargs='+',
                                               help='one or more receipts in a '
                                                    'supported format')

    return parser, all_subparsers

def receipts(args):
    for receipt_file in args.receipts:

        try:
            receipt = make_receipt(receipt_file)
            yield receipt
        except DoesNotExist as e:
            print('{}: {}'.format(receipt_file, e))
            continue
        except IsADirectory as e:
            print('{}: {}'.format(receipt_file, e))
            continue
        except ImageNotSupported as e:
            # Skip if receipt_file is not a supported file.
            continue

def do_show(args):
    # TODO: use jinja2
    table = []
    max_len_receipt_filename = 0
    max_len_price = 0

    for receipt in receipts(args):
        row = dict(receipt=receipt.file,
                   price=receipt.price,
                   retailer=receipt.retailer)

        # Verify signature for the receipt if needed. If signature is
        # missing `verified' must be False.
        if args.verify:
            if not gnupg:
                warnings.warn('You must install gnupg module to sign and'
                              ' verify receipts.')
            try:
                verified = verify(receipt.file).valid
            except (ValueError, IOError, NameError):
                verified = False

            row.update(dict(verified=verified))

        table.append(row)
        max_len_receipt_filename = max([len(receipt.file),
                                        max_len_receipt_filename])
        max_len_price = max([len(str(receipt.price)), max_len_price])

    for row in table:
        if row['price'] is None:
            price_fmt = '{2:^{3}}'
        else:
            price_fmt = '{2:{3}.2f}'

        fmt_str = '{0:{1}} -- ' + price_fmt + ' -- {4}'

        if args.verify and not args.color:
            fmt_str += ' | {}'.format(row['verified'])

        if args.verify and args.color:
            if ansiformat:
                if row['verified']:
                    fmt_str = ansiformat('green', fmt_str)
                else:
                    fmt_str = ansiformat('red', fmt_str)
            else:
                warnings.warn('You must install pygments to have colored '
                              'output.')

        print(fmt_str.format(row['receipt'],
                             max_len_receipt_filename,
                             row['price'],
                             max_len_price + 1,
                             row['retailer']))

def do_set(args):
    for receipt in receipts(args):
        set_metadata(receipt, args.price, args.retailer)

def do_del(args):
    for receipt in receipts(args):
        delete_metadata(receipt, args.price, args.retailer)

def do_sum(args):
    price_sum = 0
    for receipt in receipts(args):
        if receipt.price is not None:
            price_sum += receipt.price

    print('{0:.2f}'.format(price_sum))

def do_gpg(args):
    if gnupg:
        for receipt in receipts(args):
            if args.sign:
                sign(receipt.file, keyid=PYPELKEY)

            if args.verify:
                try:
                    verified = verify(receipt.file)
                    if verified:
                        print('Good signature from "{}"'.format(
                                verified.username))
                        d = datetime.fromtimestamp(float(verified.timestamp))
                        print('Signature made {} {} using key ID {}'.format(
                                d.isoformat(' '),
                                time.tzname[time.daylight],
                                verified.key_id))
                except ValueError as err:
                    print('{}: {}'.format(receipt.file, err))
                except IOError as err:
                    print('{}: {}'.format(err.filename, err.strerror))
    else:
        warnings.warn('You must install gnupg module to sign and verify'
                      ' receipts.')

def main():

    parser, subparsers = make_parsers()
    args = parser.parse_args()

    if args.command_name == 'set':
        if args.price is None and args.retailer is None:
            subparsers['set_parser'].error('You must provide at least '
                                           '--price or --retailer')
    elif args.command_name == 'gpg':
        if not args.sign and not args.verify:
            subparsers['gpg_parser'].error('You must provide at least '
                                           '--sign or --verify')
    args.action(args)
