import os
import random
import settings
import shutil
from roles import roles
from webob import exc

class BitsyUser(object):
    """interface class for a bitsyblog user"""
    settings = {} 
    def __init__(self, name, password=''):
        self.name = name
        self.password = password

    # user behaves like a dictionary of settings

    def __getitem__(self, key):
        return self.settings[key]

    def get(self, key, default=None):
        return self.settings.get(key, default)

class BitsyUsers(object):
    """abstract class for bitsyblog user management"""

    def __iter__(self): return self.users()

    def __contains__(self, user):
        return user in self.users()

    def __getitem__(self, user):
        """return a user"""
        if user not in self.users():
            raise KeyError
        user = BitsyUser(user, self.password(user))
        user.settings = self.settings(user.name)
        return user

    def passwords(self):
        """returns a dictionary of { user: password }"""
        passwords = {}
        for user in self.users():            
            passwords[user] = self.password(user)
        return passwords

    ### interface methods to be specified by the child class
    def new(self, name, password):
        """create a new user"""

    def users(self):
        """returns the ids of all users (generator)"""

    def password(self, user):
        """return the password for the user"""

    def settings(self, user):
        """get user settings"""

    def write_settings(self, user, **kw):
        """set attributes on a user"""


class FilespaceUsers(BitsyUsers):
    """users that live on the filesystem"""

    def __init__(self, directory):
        BitsyUsers.__init__(self)
        self.directory = directory # directory to store user information in

    def home(self, user, *path):
        return os.path.join(self.directory, user, *path)

    def pw_file(self, user):
        return self.home(user, '.password')

    def secret(self, user):
        secretfile = self.home(user, '.secret')
        if os.path.exists(secretfile):
            secret = int(file(secretfile).read().strip())
        else:
            secret = random.randint(1024, 1024**4)
            secretfile = file(secretfile, 'w')
            print >> secretfile, secret
        return secret

    def preferences_file(self, user):
        return self.home(user, 'preferences.txt')

    def css(self, user, default):
        css_dir = self.home(user, 'css')
        css_files = [ i for i in os.listdir(css_dir) if i.endswith('.css') ]
        if default:
            default = '%s.css' % default
            try:
                index = css_files.index(default)
                css_files.insert(0, css_files.pop(index))
            except ValueError:
                pass
        retval = [ dict(filename=i, name=i.rsplit('.css',1)[0],
                        css=file(os.path.join(css_dir, i)).read())
                   for i in css_files ]
        return retval

    ### interfaces for BitsyUsers

    def new(self, name, password):
        """create a new user account"""
        # XXX this shouldn't use HTTP exceptions

        if name in self.users():
            raise exc.HTTPForbidden("The name %s is already taken" % name).exception

        # characters forbidden in user name
        forbidden = ' |<>./?,'
        urls = [ 'join', 'login', 'logout', 'css', 'rss', 'atom', 'help' ]
        if [ i for i in forbidden if i in name ]:
            raise exc.HTTPForbidden("The name '%s' contains forbidden characters [%s]" % (user, forbidden)).exception
        if name in urls:
            raise exc.HTTPForbidden("The name '%s' is already used for a url"  % user).exception

        home = self.home(name)
        os.mkdir(home)
        pw_file = file(self.pw_file(name), 'w')
        print >> pw_file, password

        # setup entries structure for blog
        entries = os.path.join(home, 'entries') 
        os.mkdir(entries)
        for setting in roles['author']:
            os.mkdir(os.path.join(entries, setting))

        # setup user CSS
        css_dir = os.path.join(home, 'css') 
        os.mkdir(css_dir)
        shutil.copyfile(os.path.join(self.directory, 'site.css'),
                        os.path.join(css_dir, 'default.css'))


    def users(self):
        ignores = set(['.svn'])
        for user in os.listdir(self.directory):
            # ensure integrity of user folder
            if user in ignores:
                continue
            if os.path.isdir(os.path.join(self.directory, user)):
                yield user

    def password(self, user):
        pw_file = '.password' # name of the password file on the filesystem
        password = self.home(user, pw_file)
        if os.path.exists(password):
            return file(password).read().strip()
        return  '' # unspecified password

    def settings(self, name):
        """returns a dictionary of user preferences from a file"""
        filename = self.home(name, 'preferences.txt')
        prefs = {}
        if os.path.exists(filename):
            prefs = file(filename).read().split('\n')
            prefs = [ i for i in prefs if i.strip() ]
            prefs = [ [ j.strip() for j in i.split(':', 1) ] 
                      for i in prefs if ':' in i]
            prefs = dict(prefs)

        # assemble friends from a list
        friends = prefs.get('Friends') # can see secret blog posts
        if friends:
            prefs['Friends'] = friends.split(', ')
        else:
            prefs['Friends'] = []

        # CSS files
        prefs['CSS'] = self.css(name, prefs.get('Stylesheet'))
        
        return prefs

    def write_settings(self, name, **kw):
        """write user settings to disk"""
        
        # generic stuff; could factor out
        
        newsettings = {}
        errors = {}

        for setting in settings.form:
            if kw.has_key(setting.name):
                try:
                    setting.set(kw[setting.name])
                    newsettings[setting.name] = setting.value
                except settings.InvalidSettingError, e:
                    errors[setting.name] = str(e)

        if errors:
            return errors

        # this makes the function depend on implemention
        # i don't like this
        new_css = newsettings.pop('CSS file')
        if new_css:
            filename = new_css['filename']
            css_file = file(self.home(name, 'css', filename), 'w')
            print >> css_file, new_css['css']
            newsettings['CSS'] = filename.rsplit('.css', 1)[0]
                
        prefs = self.settings(name)
        prefs.update(newsettings)

        # write the preferences to a file
        preferences = file(self.preferences_file(name), 'w')
        for key, value in prefs.items():
            print >> preferences, '%s: %s' % ( key, value )
