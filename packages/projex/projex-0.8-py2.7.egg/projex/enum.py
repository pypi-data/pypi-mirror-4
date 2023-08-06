#!/usr/bin/python

""" 
Defines the enum class type that can be used to generate 
enumerated types 
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

# use the text module from projex
from projex import text

class enum(dict):
    """ 
    Class for generating enumerated types. 
    
    :usage      |>>> from projex.enum import enum
                |>>> TestType = enum( 'Value1', 'Value2', 'Value3' )
                |>>> TestType.Value1 | TestType.Value2
                |3
                |>>> (3 & TestType.Value1) != 0
                |True
                |>>> TestType['Value1']
                |1
                |>>> TestType[3]
                |'Value1'
                |>>> TestType.Value1
                |1
                |>>> TestType.keys()
                |[1,2,4]
    """
    
    def __getitem__( self, key ):
        """
        Overloads the base dictionary functionality to support
        lookups by value as well as by key.  If the inputed
        type is an integer, then a string is returned.   If the
        lookup is a string, then an integer is returned
        
        :param      key     <str> || <int>
        :return     <int> || <key>
        """
        # lookup the key for the inputed value
        if ( type(key) in (int, long) ):
            result = self.text(key)
            if ( not result ):
                raise AttributeError, key
            return result
        
        # lookup the value for the inputed key
        else:
            return super(enum, self).__getitem__( key )
    
    def __init__( self, *args, **kwds ):
        """
        Initializes the enum type by assigning a binary
        value to the inputed arguments in the order they
        are supplied.
        """
        super(enum, self).__init__()
        
        # update based on the inputed arguments
        kwds.update( dict([(key, 2**index) for index, key in enumerate(args)]))
        
        # set the properties
        for key, value in kwds.items():
            setattr(self, key, value)
        
        # update the keys based on the current keywords
        self.update(kwds)
    
    def all( self ):
        """
        Returns all the values joined together.
        
        :return     <int>
        """
        out = 0
        for key, value in self.items():
            out |= value
        return out
    
    def labels( self ):
        """
        Return a list of "user friendly" labels.
        
        :return     <list> [ <str>, .. ]
        """
        keys = self.keys()
        keys.sort(lambda x, y: cmp(self[x], self[y]))
        return [ text.pretty(key) for key in keys ]
    
    def text( self, value, default = '' ):
        """
        Returns the text for the inputed value.
        
        :return     <str>
        """
        for key, val in self.items():
            if ( val == value ):
                return key
        return default
    
    def valueByLabel( self, label ):
        """
        Determine a given value based on the inputed label.

        :param      label   <str>
        
        :return     <int>
        """
        keys    = self.keys()
        labels  = [ text.pretty(key) for key in keys ]
        if ( label in labels ):
            return self[keys[labels.index(label)]]
        return 0