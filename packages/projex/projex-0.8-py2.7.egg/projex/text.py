#!/usr/bin/python

""" Defines a variety of useful string operators and methods. """

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

import datetime
import re
import logging

# defines the different rules for pluralizing a word
PLURAL_RULES = [
    (re.compile('^goose$'),'geese'),
    (re.compile('^(?P<single>\w+)(=?(?P<suffix>s))$'),'ses'),
    (re.compile('^(?P<single>\w+)(=?(?P<suffix>y))$'), 'ies')
]

# precompile all expressions
EXPR_UPPERCASE  = re.compile('^[A-Z]+$')
EXPR_CAPITALS   = re.compile('^[A-Z0-9]+$')
EXPR_PHRASE     = re.compile('[A-Za-z0-9]+')
EXPR_WORD       = re.compile('^[^A-Z0-9]+|[A-Z0-9]+[^A-Z0-9]*')

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------

def camelHump( text ):
    """
    Converts the inputed text to camel humps by joining all 
    capital letters toegether (The Quick, Brown, 
    Fox.Tail -> TheQuickBrownFoxTail)
    
    :param:      text        <str>       text to be changed
    
    :return:     <str>
    
    :usage:      |import projex.text
                |print projex.text.camelHump('The,Quick, Brown, Fox.Tail')
    """
    # make sure the first letter is upper case
    output = ''.join([ capitalize(word) for word in words(text) ])
    if ( output ):
        output = output[0].lower() + output[1:]
    return output

def capitalize( text ):
    """
    Capitalizes the word using the normal string capitalization 
    method, however if the word contains only capital letters and 
    numbers, then it will not be affected.
    
    :param      text                    |   <str>
    
    :return     <str>
    """
    text = str(text)
    if ( EXPR_CAPITALS.match(text) ):
        return text
    return text.capitalize()

def capitalizeWords( text ):
    """
    Capitalizes all the words in the text.
    
    :param      text    | <str>
    
    :return     <str>
    """
    return ' '.join([capitalize(word) for word in words(text)])

def classname( text ):
    """
    Converts the inputed text to the standard classname format (camel humped 
    with a capital letter to start.
    
    :return     <str>
    """
    text = camelHump(text)
    return text[0].upper() + text[1:]

def dashed( text ):
    """
    Splits all the words from the inputed text into being 
    separated by dashes
    
    :sa         [[#joinWords]]
    
    :param      text        <str>
    
    :return     <str>
    
    :usage      |import projex.text
                |print projex.text.dash('TheQuick, Brown, Fox')
    """
    return joinWords(text, '-').lower()

def joinWords( text, separator = '' ):
    """
    Collects all the words from a text and joins them together
    with the inputed separator.
    
    :sa         [[#words]]
    
    :param      text        <str>
    :param      separator   <str>
    
    :return     <str>
    
    :usage      |import projex
                |print projex.joinWords('This::is.a testTest','-')
    """
    text    = str(text)
    output  = separator.join(words(text.strip(separator)))
    
    # no need to check for bookended items when its an empty string
    if ( not separator ):
        return output
        
    # look for beginning characters
    begin   = re.match('^\%s+' % separator, text)
    if ( begin ):
        output = begin.group() + output
        
        # make sure to not double up
        if ( begin.group() == text ):
            return output
            
    # otherwise, look for the ending results
    end     = re.search('\%s+$' % separator, text)
    if ( end ):
        output += end.group()
    
    return output

def pluralize( word ):
    """
    Converts the inputed word to the plural form of it.
    
    :param      word        <str>
    
    :return     <str>
    """
    word = str(word)
    
    all_upper = EXPR_UPPERCASE.match(word) != None
    
    # go through the different plural expressions, searching for the
    # proper replacement
    for expr, plural in PLURAL_RULES:
        results = expr.match(word)
        if ( results ):
            result_dict = results.groupdict()
            single      = result_dict.get('single','')
            
            # check if its capitalized
            if ( all_upper ):
                return single + plural.upper()
            else:
                return single + plural
    
    # by default, just include 's' at the end
    if ( all_upper ):
        return word + 'S'
    return word + 's'

def pretty( text ):
    """
    Converts the inputed text to "pretty" text by turning camel 
    humps and underscores/dashes to capitalized words. 
    (TheQuickBrownFox -> The Quick Brown Fox, 
    the_quick_fox -> The Quick Fox)
    
    :sa         [[#words]]
    
    :param      text        <str>
    
    :return     <str>
    
    :usage      |import projex.text
                |print projex.text.pretty('TheQuickBrownFox')
                |print projex.text.pretty('the_quick_brown_fox')
    """
    return ' '.join( [word.capitalize() for word in words(text)] )

def render( text, options, processed = None ):
    """
    Replaces the templates within the inputed text with the given 
    options.  Templates are defined as text within matching 
    braces, and can include additional formatting options.  
    Any key that is not found in the options will be replaced 
    as it was found in the inputed text.
    
    :param      text        <str>
    :param      options     <dict> { <str> key: <variant> value, .. }
    :param      processed   <list> [ <str> key, .. ]        used internally
    
    :return     <str> formatted text
    
    :usage      |import projex.text
                |options = { 'key': 10, 'name': 'eric' }
                |template = '[name::lower]_[key]_[date::%m-%d-%y].txt'
                |projex.text.render( template, options )
    
    :built-ins  date    will render the current datetime
    
    :options    The following are a list of formatting options text:
                
                lower         | converts the value to lowercase
                upper         | converts the value to uppercase
                camelHump     | converts the value to camel-humped text
                underscore    | converts the value to underscored text
                pretty        | converts the value to pretty text
                capitalized   | converts the value to capltalized words
                words         | converts the value to space separated words
                upper_first   | capitalizes just the first letter
                lower_first   | lowercases just the first letter
                replace(x, y) | replaces the instances of x with y
                lstrip(x)     | removes the beginning instance of x
                rstrip(x)     | removes the ending instance of x
                slice(x, y)   | same as doing string[x:y]
    """
    output      = unicode(text)
    expr        = re.compile( '(\[+([^\[\]]+)\]\]?)' )
    results     = expr.findall( output )
    curr_date   = datetime.datetime.now()
    options_re  = re.compile('(\w+)\(?([^\)]+)?\)?')
    
    if ( processed == None ):
        processed   = []
    
    for repl, key in results:
        # its possible to get multiple items for processing
        if ( repl in processed ):
            continue
        
        # record the repl value as being processed
        processed.append(repl)
        
        # replace templated templates
        if ( repl.startswith('[[') and repl.endswith(']]') ):
            output = output.replace( repl, '[%s]' % key )
            continue
        
        # determine the main key and its options
        splt    = key.split('::')
        key     = splt[0]
        prefs   = splt[1:]
        value   = None
        
        # use the inputed options
        if ( key in options ):
            # extract the value
            value = options[key]
            
            # format a float
            if ( type(value) in (float, int) ):
                if ( prefs ):
                    value = prefs[0] % value
                else:
                    value = str(value)
            
            # convert date time values
            elif ( type(value) in (datetime.datetime,
                                 datetime.date,
                                 datetime.time) ):
                if ( not prefs ):
                    date_format = '%m/%d/%y'
                else:
                    date_format = prefs[0]
                    prefs = prefs[1:]
                
                value = value.strftime(str(date_format))
            
            else:
                value = render(options[key], options, processed)
        
        # look for the built-in options
        elif ( key == 'date' ):
            value = curr_date
            
            if ( not prefs ):
                date_format = '%m/%d/%y'
            else:
                date_format = prefs[0]
                prefs = prefs[1:]
            
            value = value.strftime(str(date_format))
        
        # otherwise, continue
        else:
            continue
        
        # apply the prefs to the value
        if ( value and prefs ):
            
            for pref in prefs:
                result = options_re.match(pref)
                pref, opts = result.groups()
                
                if ( opts ):
                    opts = [opt.strip() for opt in opts.split(',')]
                else:
                    opts = []
                
                if ( 'lower' == pref ):
                    value = value.lower()
                elif ( 'upper' == pref ):
                    value = value.upper()
                elif ( 'upper_first' == pref ):
                    value = value[0].upper() + value[1:]
                elif ( 'lower_first' == pref ):
                    value = value[0].lower() + value[1:]
                elif ( 'camelHump' == pref ):
                    value = camelHump(value)
                elif ( 'underscore' == pref ):
                    value = underscore(value)
                elif ( 'capitalize' == pref ):
                    value = capitalize(value)
                elif ( 'pluralize' == pref ):
                    value = pluralize(value)
                elif ( 'words' == pref ):
                    value = ' '.join(words(value))
                elif ( 'pretty' == pref ):
                    value = pretty(value)
                
                elif ( 'replace' == pref ):
                    if ( len(opts) == 2 ):
                        value = value.replace(opts[0], opts[1])
                    else:
                        logger.warning('Invalid options for replace: %s', 
                                        ', '.join(opts))
                
                elif ( 'slice' == pref ):
                    if ( len(opts) == 2 ):
                        value = value[int(opts[0]):int(opts[1])]
                    else:
                        logger.warning('Invalid options for slice: %s',
                                       ', '.join(opts))
                
                elif ( 'lstrip' == pref ):
                    if ( not opts ):
                        value = value.lstrip()
                    else:
                        for key in opts:
                            if ( value.startswith(key) ):
                                value = value[len(key):]
                    
                elif ( 'rstrip' == pref ):
                    if ( not opts ):
                        value = value.rstrip()
                    else:
                        for key in opts:
                            if ( value.endswith(key) ):
                                value = value[:-len(key)]
                    
        output = output.replace(repl, value)
    
    return output

def underscore( text, lower = True ):
    """
    Splits all the words from the inputed text into being 
    separated by underscores
    
    :sa         [[#joinWords]]
    
    :param      text        <str>
    
    :return     <str>
    
    :usage      |import projex.text
                |print projex.text.underscore('TheQuick, Brown, Fox')
    """
    out = joinWords(text,'_')
    if ( lower ):
        return out.lower()
    return out

def xmlindent( elem, level = 0, spacer = '  ' ):
    """
    Indents the inputed XML element based on the given indent level.
    
    :param      elem    | <xml.etree.Element>
    """
    i = "\n" + level*spacer
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + spacer
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            xmlindent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def wordcount(text):
    """
    Returns the number of words in the inputed text block.
    
    :return     <int>
    """
    return len(re.findall('\w+', str(text)))

def words( text ):
    """
    Extracts a list of words from the inputed text, parsing 
    out non-alphanumeric characters and splitting camel 
    humps to build the list of words
    
    :param      text            <str>
    
    :return     <str>
    
    :usage      |import projex.text
                |print projex.text.words('TheQuick, TheBrown Fox.Tail')
    """
    stext = str(text)
    if ( not stext ):
        return []
   
    # first, split all the alphanumeric characters up
    phrases = EXPR_PHRASE.findall(stext)
    
    # second, split all the camel humped words
    output = []
    for phrase in phrases:
        output += EXPR_WORD.findall( phrase )
    
    return output
