#encoding: latin-1

""" Module for managing money information. """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software, LLC'
__license__         = 'LGPL'

__maintainer__      = 'Projex Software, LLC'
__email__           = 'team@projexsoftware.com'

import re

_expr = re.compile('^(?P<symbol>[^\w])?(?P<amount>-?[\d,]+\.?\d*)'\
                   '\s*(?P<currency>.*)$')

DEFAULT_CURRENCY = 'USD'

SYMBOLS = {
    'USD': '$',
    'PND': '£',
    'YEN': '¥'
}

def fromString( money ):
    """
    Returns the amount of money based on the inputed string.
    
    :param      money   | <str>
    
    :return     (<double> amount, <str> currency)
    """
    result = _expr.match(money)
    if ( not result ):
        return (0, DEFAULT_CURRENCY)
    
    data = result.groupdict()
    
    amount = float(data['amount'].replace(',', ''))
    
    if ( data['currency'] ):
        return (amount, data['currency'])
    
    symbol = data['symbol']
    for key, value in SYMBOLS.items():
        if ( symbol == value ):
            return (amount, key)
    
    return (amount, DEFAULT_CURRENCY)
    
def toString( amount, currency = None, rounded  = None ):
    """
    Converts the inputed amount of money to a string value.
    
    :param      amount         | <bool>
                currency       | <str>
                rounded        | <bool> || None
    
    :return     <str>
    """
    if ( currency == None ):
        currency = DEFAULT_CURRENCY
    
    symbol = SYMBOLS.get(currency, '')
    
    # insert meaningful commas
    astr   = str(int(abs(amount)))
    alen   = len(astr)
    
    if ( len(astr) > 3 ):
        arange = range(alen, -1, -3)
        parts  = reversed([astr[i-3:i] for i in arange])
        astr   = astr[:alen % 3] + ','.join(parts)
        astr   = astr.strip(',')
    
    if ( amount < 0 ):
        astr = '-' + astr
    
    # use & force decimals when necessary
    if ( (amount % 1 or rounded == False) and rounded != True ):
        astr += ('%0.2f' % (amount % 1)).lstrip('0')
    
    if ( not symbol ):
        return astr + ' ' + currency
    
    return symbol + astr

def symbol( currency ):
    """
    Returns the monetary symbol used for the given currency.
    
    :param      currency | <str.
    
    :return     <str>
    """
    return SYMBOLS.get(currency, '')