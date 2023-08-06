from bitsyauth import BitsyAuth
from bitsyblog import BitsyBlog, BitsierBlog
from getpass import getpass 
from paste.httpexceptions import HTTPExceptionHandler

def get_args(app_conf, app=BitsyBlog):
    """return arguments for bitsyblog and its handlers"""

    # accepted configuration keys, e.g. 'bitsyblog.file_dir'
    config = set(app.defaults.keys())
    
    key_str = app_conf.get('namespace', 'bitsyblog.')
    bitsyblog_args = {}
    handler_args = {}
    for key, value in app_conf.items():
        if key.startswith(key_str):
            if key_str:
                key = key.split(key_str, 1)[-1]
            if key in config:
                bitsyblog_args[key] = value
                continue

        # handler args
        if '.' in key:
            section, key = key.split('.', 1)
            handler_args.setdefault(section, {})[key] = value
    return bitsyblog_args, handler_args

def factory(global_conf, **app_conf):
    """make bitsyauth app and wrap it in middleware"""
    bitsyblog_args, handler_args = get_args(app_conf)
    app = BitsyBlog(bitsyblog_args, handler_args)
    secret = app_conf.get('secret', 'secret')
    return BitsyAuth(HTTPExceptionHandler(app), 
                     global_conf,
                     app.passwords,
                     app.newuser,
                     'bitsyblog', 
                     secret)

def basebitsierfactory(global_conf, bitsyblog_args, handler_args):
    user = bitsyblog_args['user'] # ensure this exists
    app = BitsierBlog(bitsyblog_args, handler_args)
    secret = bitsyblog_args.get('secret', 'secret')
    auth = BitsyAuth(HTTPExceptionHandler(app),
                     global_conf,
                     app.passwords,
                     newuser=None,
                     site=bitsyblog_args.get('site', 'bitsyblog'),
                     secret=secret)
    if not user in app.users:
        pw = getpass('Enter password for %s: ' % user)
        app.newuser(user, auth.hash(app.user, pw))
    return auth

def bitsierfactory(global_conf, **app_conf):
    """make single-user bitsyblog"""
    bitsyblog_args, handler_args = get_args(app_conf, BitsierBlog)
    app = basebitsierfactory(global_conf, bitsyblog_args, handler_args)
    return app
