# -*- coding: utf-8 -*-
"""pypel.models, models for pypel.

THIS SOFTWARE IS UNDER BSD LICENSE.
Copyright (c) 2012 Daniele Tricoli <eriol@mornie.org>

Read LICENSE for more informations.
"""

import os.path

import pyexiv2

PRICE_KEY = 'Xmp.pypel.Price'
RETAILER_KEY = 'Xmp.pypel.Retailer'

SUPPORTED_EXT = ('.jpg', '.jpeg', '.png', '.eps')

pyexiv2.xmp.register_namespace('http://mornie.org/xmp/pypel/', 'pypel')

class DoesNotExist(IOError):
    """The file or directory does not exist"""

class IsADirectory(IOError):
    """This is a directory so you can't use it as a receipt"""

class ImageNotSupported(IOError):
    """Image is not supported"""


class Receipt(object):

    def __init__(self, file):
        self.file = file
        self._metadata = pyexiv2.ImageMetadata(file)
        self._metadata.read()

    @property
    def price(self):
        try:
            return float(self._metadata[PRICE_KEY].value)
        except KeyError:
            pass

    @price.setter
    def price(self, price):
        self._metadata[PRICE_KEY] = str(price)
        self._metadata.write()

    @price.deleter
    def price(self):
        try:
            del self._metadata[PRICE_KEY]
        except KeyError:
            pass
        self._metadata.write()

    @property
    def retailer(self):
        try:
            return self._metadata[RETAILER_KEY].value
        except KeyError:
            pass

    @retailer.setter
    def retailer(self, retailer):
        self._metadata[RETAILER_KEY] = retailer
        self._metadata.write()

    @retailer.deleter
    def retailer(self):
        try:
            del self._metadata[RETAILER_KEY]
        except KeyError:
            pass
        self._metadata.write()

def delete_metadata(receipt, price=None, retailer=None):
    """Delete XMP metadata."""
    if not price and not retailer:
        del receipt.price
        del receipt.retailer

    if price:
        del receipt.price

    if retailer:
        del receipt.retailer

def set_metadata(receipt, price=None, retailer=None):
    """Set XMP metadata."""
    if price:
        receipt.price = price

    if retailer:
        receipt.retailer = retailer

def make_receipt(file):
    """Check for errors and create a receipt"""

    if not os.path.exists(file):
        raise DoesNotExist('No such file or directory')
    elif os.path.isdir(file):
        raise IsADirectory('Is a directory')
    elif os.path.splitext(file)[1].lower() not in SUPPORTED_EXT:
        raise ImageNotSupported

    return Receipt(file)
