#!/usr/bin/env python
"""
command line blogger
"""

import datetime
import optparse
import os
import subprocess
import sys
import tempfile
import urllib2

from ConfigParser import ConfigParser
from utils import datestamp

# global variable
CONFIG = '.blogme'

def tmpbuffer(editor=None):
    """open an editor and retreive the resulting editted buffer"""
    if not editor:
        editor = os.environ['EDITOR']
    tmpfile = tempfile.mktemp(suffix='.txt')
    cmdline = editor.split()
    cmdline.append(tmpfile)
    edit = subprocess.call(cmdline)
    buffer = file(tmpfile).read().strip()
    os.remove(tmpfile)
    return buffer

def main(args=sys.argv[1:]):

    # parse command line options
    parser = optparse.OptionParser(description=__doc__)
    parser.add_option('-c', '--config',
                      help='configuration file to use [Default: ~/.blogme]')
    parser.add_option('-f', '--file',
                      help='path to blog entries for the user; does not touch net')
    parser.add_option('-H', '--host',
                      help='URL of bitsyblog instance')
    parser.add_option('-u', '--user')
    parser.add_option('-p', '--password')
    parser.add_option('--private', action='store_true', default=False,
                      help='denote this blog entry as private')
    parser.add_option('--secret', action='store_true', default=False,
                      help='denote this blog entry as secret')
    options, args = parser.parse_args()
    
    # sanity check
    if options.private and options.secret:
        print "post can't be secret and private!"
        sys.exit(1)

    if options.file:
        # get the blog
        if args:
            msg = ' '.join(args)
        else:
            msg = tmpbuffer()
        options.file = os.path.join(options.file, 'entries')
        for opt in 'private', 'secret':
            if getattr(options, opt):
                options.file = os.path.join(options.file, opt)
                break
        else:
            options.file = os.path.join(options.file, 'public')
        options.file = os.path.join(options.file, datestamp())
        f = file(options.file, 'w')
        print >> f, msg
        f.close()
        print os.path.abspath(options.file)
        sys.exit(0)

    # parse dotfile config
    config = ConfigParser()
    _config = {} # config to write out
    if not options.config:
        home = os.environ['HOME']
        options.config = os.path.join(home, CONFIG)
    if os.path.exists(options.config):
        config.read(options.config)

    # get default host, if available
    if options.host:
        if not config.has_option('DEFAULTS', 'host'):
            _config['default'] = options.host
    else:
        if config.has_option('DEFAULTS', 'host'):
            options.host = config.get('DEFAULTS', 'host')
        else:
            print "Enter URL of host: ",
            options.host = raw_input()
            _config['default'] = options.host

    # determine user name and password
    fields = [ 'user', 'password' ]
    for field in fields:
        has_option = config.has_option(options.host, field) 

        if getattr(options, field):
            if (not has_option) or (config.get(options.host, field) != getattr(options, field)):
                _config[field] = getattr(options, field)
        else:
            if has_option:
                setattr(options, field, config.get(options.host, field))
            else:
                print "%s: " % field, 
                setattr(options, field, raw_input())
                _config[field] = getattr(options, field)

    # write the dotfile if it doesn't exist
    if _config:
        if 'default' in _config:
            if not config.has_section('DEFAULTS'):
                config.add_section('DEFAULTS')
            config.set('DEFAULTS', 'host', options.host)
        if not config.has_section(options.host):
            config.add_section(options.host)
        for field in fields:
            if not config.has_option(options.host, field):
                config.set(options.host, field, getattr(options, field))
        config.write(file(options.config, 'w'))

    # get the blog
    if args:
        msg = ' '.join(args)
    else:
        msg = tmpbuffer()

    # open the url
    url = options.host
    url += '?auth=digest' # specify authentication method
    if options.private:
        url += '&privacy=private'
    if options.secret:
        url += '&privacy=secret'
    authhandler = urllib2.HTTPDigestAuthHandler()
    authhandler.add_password('bitsyblog', url, options.user, options.password)
    opener = urllib2.build_opener(authhandler)
    urllib2.install_opener(opener)
    attempts = 5
    for i in range(attempts):
        try:
            connection = urllib2.urlopen(url, data=msg)
            print connection.url # print the blog post's url
            break
        except (urllib2.HTTPError, urllib2.URLError, socket.error), e:
            continue
        except:
            print >> sys.stderr, "An error has occured:"
            print >> sys.stderr, sys.exc_info() # XXX pretty crappy
            break
    else:
        with file('blog-%s.txt' % datetime.datetime.now().strftime("%Y%m%d"), 'w') as f:
            f.write(msg)
        print >> sys.stderr, e
        print msg

if __name__ == '__main__':
    main()
