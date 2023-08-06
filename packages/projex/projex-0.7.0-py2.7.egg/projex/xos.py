"""
Provides additional cross platform functionality to the existing
python os module.
"""

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software, LLC'
__license__         = 'GPL'

__maintainer__      = 'Projex Software, LLC'
__email__           = 'team@projexsoftware.com'

import os
import sys

def appdataPath(appname):
    """
    Returns the generic location for storing application data in a cross
    platform way.
    
    :return     <str>
    """
    if sys.platform == 'darwin':
        from AppKit import NSSearchPathForDirectoriesInDomains
        # NSApplicationSupportDirectory = 14
        # NSUserDomainMask = 1
        # True for expanding the tilde into a fully qualified path
        basepath = NSSearchPathForDirectoriesInDomains(14, 1, True)
        return os.path.join(basepath, appname)
    elif sys.platform == 'win32':
        return os.path.join(os.environ.get('APPDATA'), appname)
    else:
        return os.path.expanduser(os.path.join('~', '.' + appname))