""" The mako """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2012, Projex Software'
__license__         = 'LGPL'

# maintenance information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

__depends__         = ['mako']

import logging
import projex

projex.requires('mako')

logger = logging.getLogger(__name__)

try:
    import mako
    import mako.template
    import mako.lookup

except ImportError:
    logger.warning('The projex.makotext package requires mako to be installed.')
    mako = None

# import useful modules for the template
from datetime import datetime, date
import projex.text

def renderfile( filename, options, templatePaths = None ):
    """
    Renders a file to text using the mako templating system.
    
    To learn more about mako and its usage, see [[www.makotemplates.org]]
    
    :return     <str> formatted text
    """
    if ( not mako ):
        logger.error('mako is not installed')
        return ''
    
    if ( not mako ):
        logger.error('mako is not installed.')
        return ''
    
    # update the default options
    scope = {}
    scope['projex_text'] = projex.text
    scope['date']        = date
    scope['datetime']    = datetime
    scope.update(options)
    
    logger.debug('rendering mako file: %s', filename)
    if ( templatePaths ):
        lookup = mako.lookup.TemplateLookup(directories = templatePaths)
        templ = mako.template.Template(filename = filename, lookup = lookup)
    else:
        templ = mako.template.Template(filename = filename)
    
    return templ.render(**scope)

def render( text, options, templatePaths = None ):
    """
    Renders a template text to a resolved text value using the mako templating
    system.
    
    Provides a much more robust templating option to the projex.text system.  
    While the projex.text method can handle many simple cases with no
    dependencies, the makotext module makes use of the powerful mako templating
    language.  This module provides a simple wrapper to the mako code.
    
    To learn more about mako and its usage, see [[www.makotemplates.org]]
    
    :param      text        <str>
    :param      options     <dict> { <str> key: <variant> value, .. }
    
    :return     <str> formatted text
    
    :usage      |import projex.makotext
                |options = { 'key': 10, 'name': 'eric' }
                |template = '${name.lower()}_${key}_${date.today()}.txt'
                |projex.makotext.render( template, options )
    """
    if ( not mako ):
        logger.error('mako is not installed.')
        return ''
    
    # update the default options
    scope = {}
    scope['projex_text'] = projex.text
    scope['date']        = date
    scope['datetime']    = datetime
    scope.update(options)
    
    if ( templatePaths ):
        lookup = mako.lookup.TemplateLookup(directories = templatePaths)
        templ = mako.template.Template(text, lookup = lookup)
    else:
        templ = mako.template.Template(text)
    
    return templ.render(**scope)