from webob import Request

import os

def getpw(basedir, user):
    file = os.path.join(basedir, user, '.password')

    try:
        fp = open(file)
    except IOError:
        return None

    pw = fp.read().strip()
    fp.close()
    return pw

# from paste.auth.digest
try:
    from hashlib import md5
except ImportError:
    from md5 import md5
def hash(user, pw, realm):
    return md5("%s:%s:%s" % (user, realm, pw)).hexdigest()

class BitsyblogFilespaceAuth(object):
    def __init__(self, realm, basedir):
        self.realm = realm
        self.basedir = basedir
    def __call__(self, user, pw):
        stored = getpw(self.basedir, user)
        if stored is None:
            return False
        return hash(user, pw, self.realm) == stored

def filter_factory(global_conf, realm=None, basedir=None):
    #from paste.util.import_string import eval_import
    #authfunc = eval_import(authfunc)

    authfunc = BitsyblogFilespaceAuth(realm, basedir)

    def filter(app):        
        return BasicAuthMiddleware(app, realm, authfunc)
    return filter

class BasicAuthMiddleware(object):
    def __init__(self, app, realm, auth_checker):
        self.app = app
        self.realm = realm
        self.auth_checker = auth_checker

    def __call__(self, environ, start_response):
        req = Request(environ)

        header = req.authorization
        if not header:
            return self.app(environ, start_response)

        (method, auth) = header.split(' ', 1)
        if method.lower() != 'basic':
            return self.app(environ, start_response)

        auth = auth.strip().decode('base64')
        
        username, password = auth.split(':', 1)

        if self.auth_checker(username, password):
            environ['REMOTE_USER'] = username
        
        return self.app(environ, start_response)
