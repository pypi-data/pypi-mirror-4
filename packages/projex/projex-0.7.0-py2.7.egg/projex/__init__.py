#!/usr/bin/python

""" 
This is the core Python package for all of the projex software
projects.  At the bare minimum, this package will be required, and 
depending on which software you are interested in, other packages 
will be required and updated.
"""

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

# define version information (major,minor,maintanence)
__depends__        = []
__version_info__   = (0, 7, 0)
__version__        = '%i.%i.%i' % __version_info__

#------------------------------------------------------------------------------

from projex.init import *