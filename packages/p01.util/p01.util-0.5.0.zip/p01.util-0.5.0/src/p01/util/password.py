##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: __init__.py 39 2007-01-28 07:08:55Z roger.ineichen $
"""

from hashlib import md5
from hashlib import sha1
from random import randint
from codecs import getencoder

_encoder = getencoder("utf-8")


# md5
def encodeMD5Password(password, salt=None):
    if salt and len(salt) != 8:
        raise ValueError("Wrong salt lenght given.")
    if salt is None:
        salt = "%08x" % randint(0, 0xffffffff)
    return unicode(salt + md5.new(_encoder(password)[0]).hexdigest())


def checkMD5Password(storedPassword, password):
    salt = storedPassword[:-32]
    return storedPassword == encodeMD5Password(password, salt)


def compareMD5Password(storedPassword, md5Password):
    return storedPassword[8:] == md5Password[8:]


# sha1
def encodeSHA1Password(password, salt=None):
    if salt is None:
        salt = "%08x" % randint(0, 0xffffffff)
    return unicode(salt + sha1(_encoder(password)[0]).hexdigest())


def checkSHA1Password(storedPassword, password):
    salt = storedPassword[:-32]
    return storedPassword == encodeSHA1Password(password, salt)


def compareSHA1Password(storedPassword, sha1Password):
    return storedPassword[8:] == sha1Password[8:]
