"""utlity functions for bitsyblog"""

import cgi
import datetime
import os
import urllib
import urllib2

import docutils
import docutils.core

from docutils.utils import SystemMessage

# format to uniquely label blog posts
timeformat = ( 'YYYY', 'MM', 'DD', 'HH', 'MM', 'SS' )
timestamp = '%Y%m%d%H%M%S' # strftime representation

def ReST2html(string):
    """renders a string with restructured text"""

    settings = { 'report_level': 5 }
    string = string.strip()
    try:
        parts = docutils.core.publish_parts(string,
                                            writer_name='html',
                                            settings_overrides=settings)
        body = parts['body']
    except (SystemMessage, UnicodeError), e:
        lines = [ cgi.escape(i.strip()) for i in string.split('\n') ]
        body = '<br/>\n'.join(lines)
    return body

def validate_css(css):
    """use a webservice to determine if the argument is valid css"""
    url = 'http://jigsaw.w3.org/css-validator/validator?text=%s'
    url = url % urllib.quote_plus(css)
    foo = urllib2.urlopen(url)
    text = foo.read()
    return not 'We found the following errors' in text # XXX hacky

def date(datestamp):
    datestamp = os.path.split(datestamp)[-1]
    retval = []
    for i in timeformat:
        retval.append(int(datestamp[:len(i)]))
        datestamp = datestamp[len(i):]
    return datetime.datetime(*retval)

def datestamp(date=None):
    if isinstance(date, float):
        date = datetime.datetime.fromtimestamp(date)
    if date is None:
        date = datetime.datetime.now()
    return date.strftime(timestamp)
