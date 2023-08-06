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

#------------------------------------------------------------------------------

import logging
import os
import sys

# initialize the main projex logger class
logger       = logging.getLogger(__name__)

WEBSITES     = {
    'home': 'http://www.projexsoftware.com',
    'docs': 'http://docs.projexsoftware.com',
    'blog': 'http://blog.projexsoftware.com',
    'dev':  'http://dev.projexsoftware.com'
}

SUBCONTEXT_MAP = {
    ('home', 'Product'):      '%(base_url)s/products/%(app)s',
    ('docs', 'UserGuide'):    '%(base_url)s/userguide',
    ('docs', 'APIReference'): '%(base_url)s/api/%(app)s',
    ('dev',  'Project'):      '%(base_url)s/projects/%(app)s'
}

#------------------------------------------------------------------------------

def environ():
    """
    Returns the current environment that is being used.
    
    :return     <projex.envmanager.EnvManager> || None
    """
    from projex.envmanager import EnvManager
    return EnvManager.current()

def importobject( module_name, object_name ):
    """
    Imports the object with the given name from the inputed module.
    
    :param      module_name | <str>
                object_name | <str>
    
    :return     <object> || None
    """
    if ( not module_name in sys.modules ):
        try:
            __import__(module_name)
        except ImportError:
            logger.exception('Could not import module: %s' % module_name)
            return None
    
    module = sys.modules.get(module_name)
    if ( not module ):
        logger.warning('No module %s found.' % module_name)
        return None
    
    if ( not hasattr(module, object_name) ):
        logger.warning('No object %s in %s.' % (object_name, module_name))
        return None
    
    return getattr(module, object_name)

def packageRootPath( path ):
    """
    Retruns the root file path that defines a Python package from the inputed
    path.
    
    :param      path | <str>
    
    :return     <str>
    """
    path = str(path)
    if ( os.path.isfile(path) ):
        path = os.path.dirname(path)
        
    parts = os.path.normpath(path).split(os.path.sep)
    package_parts = []
    
    for i in range(len(parts), 0, -1):
        filename = os.path.sep.join(parts[:i] + ['__init__.py'])
        
        if ( not os.path.isfile(filename) ):
            break
        
        package_parts.insert(0, parts[i-1])
    
    return os.path.abspath(os.path.sep.join(parts[:-len(package_parts)]))

def packageFromPath( path ):
    """
    Determines the python package path based on the inputed path.
    
    :param      path | <str>
    
    :return     <str>
    """
    path = str(path)
    if ( os.path.isfile(path) ):
        path = os.path.dirname(path)
        
    parts = os.path.normpath(path).split(os.path.sep)
    package_parts = []
    
    for i in range(len(parts), 0, -1):
        filename = os.path.sep.join(parts[:i] + ['__init__.py'])
        
        if ( not os.path.isfile(filename) ):
            break
        
        package_parts.insert(0, parts[i-1])
    
    return '.'.join(package_parts)

def refactor( module, name, repl ):
    """
    Convenience method for the EnvManager.refactor 
    """
    environ().refactor( module, name, repl )

def requires( *modules ):
    """
    Convenience method to the EnvManager.current().requires method.
    
    :param      *modules    | (<str>, .. )
    """
    environ().requires(*modules)

def website( app = None, mode = 'home', subcontext = 'UserGuide' ):
    """
    Returns the website location for projex software.
    
    :param      app  | <str> || None
                mode | <str> (home, docs, blog, dev)
    
    :return     <str>
    """
    base_url = WEBSITES.get(mode, '')
    
    if ( app and base_url ):
        opts      = {'app': app, 'base_url': base_url}
        base_url  = SUBCONTEXT_MAP.get((mode, subcontext), base_url)
        base_url %= opts
        
    return base_url