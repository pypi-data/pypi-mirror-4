#!/usr/bin/python

""" 
Encryption module for encrypting and testing information. If you want to \
properly use this module for safest encryption, you will need to download \
the PyCrypto module and install it from \
[https://www.dlitz.net/software/pycrypto/ the pycrpto website].

:warning    If you choose to not install the crypto information, then the \
            module will encrypt/decrypt by encoding using the base64 encoder.
"""

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

#------------------------------------------------------------------------------

import base64
import logging

logger = logging.getLogger(__name__)

try:
    from Crypto.Cipher import AES
    
except ImportError:
    warn = 'The PyCrypto module was not found.  It is highly recommended for '\
           'security purposes to download and install this module for use '\
           ' with the security module.'
           
    logger.warning(warn)
    AES = None

# applications that use encryption should define their own encryption key
# and assign it to this value - this will need to be the same size as the
# block size
ENCRYPT_KEY = ''

# character used to pad the encryption when a string provided is too shorts
PADDING     = '{'

def check( a, b ):
    """
    Checks to see if the two values are equal to each other.
    
    :param      a | <str>
                b | <str>
    
    :return     <bool>
    """
    aencrypt = encrypt(a)
    bencrypt = encrypt(b)
    
    return (a == b or a == bencrypt or aencrypt == b)
    
def decrypt( text, useBase64=False ):
    """
    Decrypts the inputed text.  If the PyCrypto module is not included \
    this will just decode it from base64.
    
    :param      text | <str>
    
    :return     <str>
    """
    text = str(text)
    
    if ( not AES or useBase64 ):
        return base64.b64decode(text)
    
    cipher = AES.new(ENCRYPT_KEY)
    return cipher.decrypt(base64.b64decode(text)).rstrip(PADDING)

def encrypt( text, bits = 32, useBase64 = False ):
    """
    Encrypts the inputed text using the current settings.  If the PyCrypto \
    module is not included, this will simply encode the inputed text to \
    base64 format.
    
    :param      text      | <str>
                bits      | <int> | 16, 24, 32 bit encryption
                useBase64 | <bool>
    
    :return     <str>
    """
    text = str(text)
    
    # if crypto does not exist, then just return the text as encoded in base64
    if ( not AES or useBase64 ):
        return base64.b64encode(text)
    
    pad = lambda s: s + (bits - len(s) % bits) * PADDING
    
    cipher = AES.new(ENCRYPT_KEY)
    return base64.b64encode(cipher.encrypt(pad(text)))

def generateKey( password, bits = 32 ):
    """
    Generates a new random encryption key.  When you are designing a new \
    application, you should generate a new key and assign it to the global \
    ENCRYPT_KEY value for this module to properly convert your data.
    
    :warning    Do not leave the ENCRYPT_KEY at its default value.  It will \
                be a security risk.
    
    :param      password    | <str>
                bits        | <int>  | 16, 24, or 32 bits
    
    :return     <str>
    """
    pad = lambda s, c: s + (bits - len(s) % bits) * c
    return pad(base64.b64encode(password), 'xYie')[:bits]

# by default, just setting the encryption key as 'password'
# THIS SHOULD BE RESET FOR YOUR APPLICATION
ENCRYPT_KEY = generateKey('password')