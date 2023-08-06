"""
a tiny tiny blog.
this is the view class and is more bitsyblog than anything
else can claim to be
"""

### imports

import dateutil.parser

import datetime
import docutils
import docutils.core
import inspect
import os
import PyRSS2Gen
import re

import utils

from blog import FileBlog
from cStringIO import StringIO
from docutils.utils import SystemMessage
from genshi.builder import Markup
from genshi.template import TemplateLoader
from paste.fileapp import FileApp
from pkg_resources import iter_entry_points
from pkg_resources import resource_filename
from StringIO import StringIO
from urlparse import urlparse
from webob import Request, Response, exc

from roles import roles

### exceptions

class BlogPathException(Exception):
    """exception when trying to retrieve the blog"""

### the main course

class BitsyBlog(object):
    """a very tiny blog"""

    ### class level variables
    defaults = { 'date_format': '%H:%M %F', # default date format
                 'file_dir': os.path.dirname(__file__), # where the blog is kept
                 'subject': '[ %(date)s ]:', # default subject
                 'n_links': 5, # number of links for navigation
                 'site_name': 'bitsyblog', # name of the site (needed?)
                 'header': None, # text to insert as first child of body'
                 'template_directories': '', # space separated template_directories
                 'auto_reload': True, # reload the genshi templates
                 'help_file': None, # help to display
                 'feed_items': 10, # number of RSS/atom items to display
                 'post_handlers': '', # post handlers
                 'rss_html': True, # whether to render rss descriptions as HTML
                 }

    cooked_bodies = {}

    def __init__(self, kw, handler_args):

        # set values from defaults and kw
        for key, value in self.defaults.items():
            kw_value = kw.get(key, value)

            # convert kw_value to the proper type
            _type = type(value)
            if isinstance(kw_value, basestring) and not issubclass(_type, basestring) and value is not None:
                if _type == bool:
                    kw_value = kw_value.lower() == 'true'
                else:
                    kw_value = _type(kw_value)
            setattr(self, key, kw_value)

        self.response_functions = {'GET': self.get,
                                   'POST': self.post,
                                   'PUT': self.put
                                   }

        # abstract attributes
        from user import FilespaceUsers
        self.users = FilespaceUsers(self.file_dir)
        self.blog = FileBlog(self.file_dir)
        self.cooker = self.restructuredText

        # template renderer
        self.template_directories = self.template_directories.split() # no spaces in directory names, for now

        for directory in self.template_directories:
            assert os.path.isdir(directory), "Bitsyblog template directory %s does not exist!" % directory

        self.template_directories.append(resource_filename(__name__, 'templates'))
        self.loader = TemplateLoader(self.template_directories,
                                     auto_reload=self.auto_reload)

        # helpfile
        if self.help_file and os.path.exists(self.help_file):
            help = file(self.help_file).read()
            self.help = docutils.core.publish_string(help,
                                                     writer_name='html',
                                                     settings_overrides={'report_level': 5})

        # header
        if self.header:
            if os.path.exists(self.header):
                self.header = file(self.header).read()
            self.header = Markup(self.header)

        # for BitsyAuth
        self.newuser = self.users.new

        # post handlers
        self.post_handlers = [ i for i in self.post_handlers.split() if i ]
        self.handlers = [] # handlers for blog post event
        for entry_point in iter_entry_points('bitsyblog.listeners'):
          if entry_point.name in self.post_handlers:
              try:
                  handler = entry_point.load()(self, **handler_args.get(entry_point.name, {}))
                  self.handlers.append(handler)
              except:
                  print 'Cant load entry point %s' % entry_point.name
                  raise

    ### methods dealing with HTTP

    def __call__(self, environ, start_response):
        request = Request(environ)

        # genshi data dictionary
        request.environ['data'] = { 'site_name': self.site_name,
                                    'request': request,
                                    'link': self.link,
                                    'logo': self.logo(request),
                                    'header': self.header,
                                    'user_url': self.user_url,
                                    'permalink': self.permalink }

        res = self.response_functions.get(request.method, self.error())(request)
        return res(environ, start_response)

    def get_response(self, text, content_type='text/html'):
        # XXX to deprecate
        res = Response(content_type=content_type, body=text)
        return res

    def logo(self, request):
        """link to the logo"""
        _logo = 'bitsyblog.png' # TODO: should go to self.logo
        logo = os.path.join(self.file_dir, _logo)
        if os.path.exists(logo):
            return self.link(request, _logo)

    def get_index(self, request):
        """returns material pertaining to the root of the site"""

        path = request.path_info.strip('/')
        n_posts = self.number_of_posts(request)
        n_links = self.number_of_links(request, n_posts)

        ### the front page
        if not path:
            return Response(content_type='text/html', body=self.index(request, n_links))

        ### feeds

        # site rss
        if path == 'rss':
            if n_posts is None:
                n_posts = self.feed_items
            return Response(content_type='text/xml', body=self.site_rss(request, n_posts))

        # site atom
        if path == 'atom':
            if n_posts is None:
                n_posts = self.feed_items
            return Response(content_type='text/xml', body=self.atom(request, self.blog.latest(self.users.users(), n_posts)))

        ### help
        if path == 'help' and hasattr(self, 'help'):
            return Response(content_type='text/html', body=self.help)

        ### static files

        # site.css
        if path == 'css/site.css':
            css_file = os.path.join(self.file_dir, 'site.css')
            return FileApp(css_file)

        # logo
        if path == 'bitsyblog.png':
            logo = os.path.join(self.file_dir, 'bitsyblog.png')
            if not self.logo(request):
                raise exc.HTTPNotFound
            return FileApp(logo)

    def get_user_space(self, user, path, request):
        """returns a part of the user space"""

#        request.user = self.users[user] # user whose blog is viewed
        check = self.check_user(user, request) # is this the authenticated user?

        feed = None # not an rss/atom feed by default (flag)
        n_posts = self.number_of_posts(request, user)
        n_links = self.number_of_links(request, n_posts, user)

        # special paths
        if path == [ 'post' ]:
            if check is not None:
                return check
            return Response(content_type='text/html', body=self.form_post(request, user))

        if path == [ 'preferences' ]:
            if check is not None:
                return check
            return Response(content_type='text/html', body=self.preferences(request, user))

        if path == [ 'rss' ]:
            feed = 'rss'
            path = []
            if n_posts is None:
                n_posts = self.feed_items # TODO: allow to be configurable

        if path == [ 'atom' ]:
            feed = 'atom'
            path = []
            if n_posts is None:
                n_posts = self.feed_items # TODO: allow to be configurable

        if len(path) == 2:
            if path[0] == 'css':
                for i in request.user.settings['CSS']:
                    # find the right CSS file
                    if i['filename'] == path[1]:
                        return Response(content_type='text/css', body=i['css'])
                else:
                    return exc.HTTPNotFound('CSS "%s" not found' % path[1])

        role = self.role(user, request)

        # get the blog
        try:
            blog = self.get_blog(user, path, role, n_items=n_posts)
        except BlogPathException, e:
            return exc.HTTPNotFound(str(e))
        except exc.HTTPException, e:
            return e.wsgi_response

        if feed == 'rss':
            content = self.rss(request, user, blog) # XXX different signatures
            return Response(content_type='text/xml', body=content)

        if feed == 'atom':
            content = self.atom(request, blog, user) # XXX different signatures
            return Response(content_type='text/xml', body=content)

        # reverse the blog if necessary
        if request.GET.get('sort') == 'forward':
            blog = list(reversed(blog))

        # write the blog
        if request.GET.get('format') == 'text':
            content = self.text_blog(blog)
            content_type = 'text/plain'
        else:
            content = self.write_blog(user, blog, request.path_info, n_links, request)
            content_type = 'text/html'

        # return the content
        return Response(content_type=content_type, body=content)

    def get(self, request):
        """
        respond to a get request
        """

        # front matter of the site
        index = self.get_index(request)
        if index is not None:
            return index

        ### user space
        user, path = self.userpath(request)
        return self.get_user_space(user, path, request)

    def post(self, request):
        """
        write a blog entry and other POST requests
        """

        # find user + path
        user, path = self.userpath(request)

        # check to make sure the user is authenticated
        # and is the resource owner
        check = self.check_user(user, request)
        if check is not None:
            return check

        if len(path):

            if path == [ 'preferences' ]:

                # make the data look like we want
                settings = {}
                settings['Date format'] = request.POST.get('Date format')
                settings['Subject'] = '%(date)s'.join((request.POST['Subject-0'], request.POST['Subject-2']))
                settings['Stylesheet'] = request.POST['Stylesheet']
                settings['CSS file'] = request.POST.get('CSS file')
                settings['Friends'] = ', '.join(request.POST.getall('Friends'))

                errors = self.users.write_settings(user, **settings)
                if errors: # re-display form with errors
                    return self.get_response(self.preferences(request, user, errors))

                return self.get_response(self.preferences(request, user, message='Changes saved'))
            elif len(path) == 1 and self.isentry(path[0]):
                entry = self.blog.entry(user, path[0], roles['author'])
                if entry is None:
                    return exc.HTTPNotFound("Blog entry %s not found %s" % path[0])
                privacy = request.POST.get('privacy')
                datestamp = entry.datestamp()
                if privacy:
                    self.blog.delete(user, datestamp)
                    self.blog.post(user, datestamp, entry.body, privacy)
                return exc.HTTPSeeOther("Settings updated", location=self.user_url(request, user, datestamp))
            else:
                return exc.HTTPMethodNotAllowed("Not sure what you're trying to do")

        # get the body of the post
        body = request.body
        body = request.POST.get('form-post', body)
        body = body.strip()
        if not body:
            return exc.HTTPSeeOther("Your post has no content!  No blog for you",
                                    location=self.user_url(request, user, 'post'))

        # determine if the post is secret or private
        privacy = request.GET.get('privacy') or request.POST.get('privacy') or 'public'

        # write the file
        now = utils.datestamp(datetime.datetime.now())
        location = self.user_url(request, user, now, permalink=True)
        blog_entry = self.blog.post(user, now, body, privacy)

        # fire event handlers
        # XXX could be done asynchronously
        for handler in self.handlers:
          try:
            handler(blog_entry, location)
          except:
            pass

        # point the user at the post
        return exc.HTTPSeeOther("Post blogged by bitsy", location=location)

    def put(self, request):
        """
        PUT several blog entries from a file
        """

        # find user + path
        user, path = self.userpath(request)

        if user not in self.users.users():
            return exc.HTTPNotFound("No blog found for %s" % user)

        if len(path):
            return exc.HTTPMethodNotAllowed("Not sure what you're trying to do")

        # find the dates + entries in the file
        regex = '\[.*\]:'
        entries = re.split(regex, request.body)[1:]
        dates = [ date.strip().strip(':').strip('[]').strip()
                  for date in re.findall(regex, request.body) ]
        dates = [ dateutil.parser.parse(date) for date in dates ]

        # write to the blog
        for i in range(len(entries)):
            datestamp = utils.datestamp(dates[i])
            self.blog.post(user, datestamp, entries[i], 'public')

        return exc.HTTPOk("%s posts blogged" % len(entries))


    def error(self):
        """deal with non-supported methods"""
        methods = ', '.join(self.response_functions.keys()[:1])
        methods += ' and %s' % self.response_functions.keys()[-1]
        return exc.HTTPMethodNotAllowed("Only %s operations are allowed" % methods)

    ### auth/auth functions

    def passwords(self):
        return self.users.passwords()

    def authenticated(self, request):
        """return authenticated user"""
        return request.environ.get('REMOTE_USER')

    def check_user(self, user, request):
        """
        determine authenticated user
        returns None on success
        """
        authenticated = self.authenticated(request)
        if authenticated is None:
            return exc.HTTPUnauthorized('Unauthorized')
        elif user != authenticated:
            return exc.HTTPForbidden("Forbidden")

    def role(self, user, request):
        """
        determine what role the authenticated member has
        with respect to the user
        """
        auth = self.authenticated(request)
        if not auth:
            return 'public'
        if auth == user:
            return 'author'
        else:
            if auth in request.user.settings['Friends']:
                return 'friend'
            else:
                return 'public'

    ### user methods

    def userpath(self, request):
        """user who's blog one is viewing"""
        path = request.path_info.strip('/').split('/')
        name = path[0]
        path = path[1:]
        if name:
            if name not in self.users:
                exc.HTTPNotFound("No blog found for %s" % name)
            request.user = self.users[name]
        else:
            name = None
        return name, path

    ### methods for linking and URLs

    def link(self, request, path='', permanant=False):
        if isinstance(path, basestring):
            path = [ path ]
        if not path:
            path = ['']
        path = [ i.strip('/') for i in path ]
        if permanant:
            application_url = request.application_url
        else:
            application_url = urlparse(request.application_url)[2]
        path = [ application_url ] + list(path)
        return '/'.join(path)

    def user_url(self, request, user, *args, **kw):
        """link to a user resource"""
        permalink = kw.get('permalink', False)
        path = [ user ]
        path.extend(args)
        return self.link(request, path, permalink)

    def permalink(self, request, blogentry):
        """permalink for a blog entry"""
        return self.user_url(request, blogentry.user, blogentry.datestamp(), permalink=True)

    def mangledurl(self, request, blogentry):
        """return a mangled url for obfuscated sharing"""
        return self.user_url(request, blogentry.user, 'x%x' % (int(blogentry.datestamp()) * self.users.secret(blogentry.user)), permalink=True)

    def unmangleurl(self, url, user):
        """unmangle a url for obfuscated sharing"""
        url = url.strip('x')
        try:
            value = int(url, 16)
        except ValueError:
            return None

        # XXX once one has a mangled url, one can obtain the secret
        value /= self.users.secret(user)

        entry = str(value)
        if self.isentry(entry):
            return self.blog.entry(user, entry, ['public', 'secret', 'private'])

    ### blog retrival methods

    def isentry(self, string): # TODO -> blog.py
        """returns whether the string is a blog entry"""
        return (len(string) == len(''.join(utils.timeformat))) and string.isdigit()

    def number_of_posts(self, request, user=None):
        """return the number of blog posts to display"""
        # determine number of posts to display (None -> all)
        n_posts = request.GET.get('posts', None)
        if n_posts is not None:
            try:
                n_posts = int(n_posts)
            except (TypeError, ValueError):
                n_posts = None
        return n_posts

    def number_of_links(self, request, n_posts=None, user=None):
        """return the number of links to display in the navigation"""
        n_links = request.GET.get('n')
        if n_links == 'all':
            return -1
        try:
            n_links = int(n_links)
        except (TypeError, ValueError):
            n_links = self.n_links
        if n_posts and n_links > 0 and n_links > n_posts:
            n_links = n_posts # don't display more links than posts
        return n_links

    def get_blog(self, user, path, role='public', n_items=None):
        """retrieve the blog entry based on the path"""

        notfound = "blog entry not found"

        # get permissions
        allowed = roles[role]

        # entire blog
        if not path:
            return self.blog(user, allowed, n_items)

        # mangled urls
        if len(path) == 1 and path[0].startswith('x'):
            entry = self.unmangleurl(path[0], user)
            if entry:
                return [ entry ]
            else:
                raise BlogPathException(notfound)

        # individual blog entry
        if (len(path) == 1) and self.isentry(path[0]):
            blog = self.blog.entry(user, path[0], allowed)
            if not blog:
                raise BlogPathException(notfound)
            return [ blog ]

        # parse the path into a date path
        n_date_vals = 3 # year, month, date
        if len(path) > n_date_vals:
            raise BlogPathException(notfound)

        # ensure the path conforms to expected values (ints):
        try:
            [ int(i) for i in path]
        except ValueError:
            raise BlogPathException(notfound)

        # get the blog
        return self.blog.entries(user, allowed, *path)

    ### methods for markup

    def stylesheets(self, request):
        user = getattr(request, 'user', None)
        if user:
            stylesheets = request.user['CSS']
            stylesheets = [ (self.user_url(request, user.name, 'css', css['filename']),
                             css['name']) for css in stylesheets ]
        else:
            stylesheets = [(self.link(request, "css/site.css"), "Default")]
        return stylesheets

    def site_nav(self, request):
        """returns HTML for site navigation"""

        links = [(self.link(request), '/')]
        user = self.authenticated(request)
        if user:
            links.extend([(self.user_url(request, user), user),
                          (self.user_url(request, user, 'post'), 'post'),
                          (self.user_url(request, user, 'preferences'), 'preferences'),
                          (self.link(request, 'logout'), 'logout')])
        else:
            links.extend([(self.link(request, 'login'), 'login'), 
                          (self.link(request, 'join'), 'join')])

        if hasattr(self, 'help'):
            links.append((self.link(request, 'help'), 'help'))

        request.environ['data']['links'] = links


    def index(self, request, n_links):
        data = request.environ['data']
        data['n_links'] = n_links
        self.site_nav(request)

        # get the blogs
        blogs = {}
        for user in self.users:
            blog = self.blog(user, ('public',), n_links)
            if blog:
                blogs[user] = blog
        users = blogs.keys()

        # display latest active user first
        users.sort(key=lambda user: blogs[user][0].date, reverse=True)

        data['blogs'] = blogs
        data['users'] = users
        data['date_formats'] = dict([(user, self.users[user].settings.get('Date format', self.date_format)) for user in users])

        # render the template
        template = self.loader.load('index.html')
        return template.generate(**request.environ['data']).render()

    def cooked_entry(self, entry):
        """cook the entry"""
        if (entry.user, entry.datestamp()) not in self.cooked_bodies:
           self.cooked_bodies[(entry.user, entry.datestamp())] = (self.cooker(entry.body), entry.modified())
        body, modified = self.cooked_bodies[(entry.user, entry.datestamp())]
        if entry.modified() > modified:
            body = self.cooker(entry.body)
            self.cooked_bodies[(entry.user, entry.datestamp())] = (body, entry.modified())
        return body

    def write_blog(self, user, blog, path, n_links, request):
        """return the user's blog in HTML"""

        # cook the entry
        for entry in blog:
            entry.cooked_body = Markup(self.cooked_entry(entry))

        # site nav
        # XXX def site_nav() puts directly in request.environ['data']
        # should return instead
        self.site_nav(request)

        # user data -> should be moved up the chain
        data = request.environ['data']
        data['user'] = user
        data['role'] = self.role(user, request)
        data['stylesheets'] = self.stylesheets(request)
        data['subject'] = request.user.settings.get('Subject', self.subject)
        data['date_format'] = request.user.settings.get('Date format', self.date_format)
        data['mangledurl'] = self.mangledurl

        # blog data
        data['blog'] = blog
        data['n_links'] = n_links

        # render the template
        template = self.loader.load('blog.html')
        try:
            return template.generate(**data).render()
        except UnicodeDecodeError:
            # TODO: better error handling
            raise

    def text_blog(self, blog):
        """raw text format of blog"""

        if len(blog) == 1:
            return blog[0].body.strip() + '\n'

        buffer = StringIO()
        for entry in blog:
            print >> buffer, '[ %s ]\n' % entry.date.strftime(self.date_format)
            print >> buffer, entry.body.strip() + '\n'
        return buffer.getvalue()

    def restructuredText(self, string):
        """renders a string with restructured text"""
        body = utils.ReST2html(string)
        retval = '<div class="blog-body">%s</div>' % body
        return retval

#         # XXX this should be reenabled if 'system-message's again appear in the markup
#         try:
#             foo = etree.fromstring(retval)
#         except etree.XMLSyntaxError:
#             return retval
#         # should cleanup the <div class="system-message">
#         for i in foo.getiterator():
#             if dict(i.items()).get('class') ==  'system-message':
#                 i.clear()
#         return etree.tostring(foo)


    ### feeds

    def site_rss(self, request, n_items=10):
        blog = self.blog.latest(list(self.users.users()), n_items)
        title = self.site_name + ' - rss'
        link = request.application_url
        description = "latest scribblings on %s" % self.site_name
        lastBuildDate = datetime.datetime.now()
        items = [ self.rss_item(request, entry.user, entry) for entry in blog ]
        rss = PyRSS2Gen.RSS2(title=title,
                             link=link,
                             description=description,
                             lastBuildDate=lastBuildDate,
                             items=items)
        return rss.to_xml()

    def rss(self, request, user, blog):
        """
        rss feed for a user's blog
        done with PyRSS2Gen:
        http://www.dalkescientific.com/Python/PyRSS2Gen.html
        """
        title = "%s's blog" % user
        link = os.path.split(request.url)[0]
        description = "latest blog entries for %s on %s" % (user, self.site_name)
        lastBuildDate = datetime.datetime.now() # not sure what this means

        items = [ self.rss_item(request, user, entry) for entry in blog ]
        rss = PyRSS2Gen.RSS2(title=title,
                             link=link,
                             description=description,
                             lastBuildDate=lastBuildDate,
                             items=items)
        return rss.to_xml()

    def rss_item(self, request, user, entry):
        if hasattr(request, 'user') and request.user.name == user:
            prefs = request.user.settings
        else:
            prefs = self.users[user].settings
        subject = prefs.get('Subject', self.subject)
        date_format = prefs.get('Date format', self.date_format)
        title = entry.title()
        link = self.permalink(request, entry)

        # item description
        if self.rss_html:
            body = self.cooked_entry(entry)
        else:
            body = entry.body
            body = unicode(body, errors='replace')

        return PyRSS2Gen.RSSItem(title=title,
                                 link=link,
                                 description=body,
                                 author=user,
                                 guid=PyRSS2Gen.Guid(link),
                                 pubDate=entry.date)


    def atom(self, request, blog, author=None):

        # data for genshi template
        date = blog[0].date.isoformat()
        data = request.environ['data']
        data['blog'] = blog
        data['author'] = author
        data['date'] = date

        # render the template
        template = self.loader.load('atom.xml')
        return template.generate(**data).render()


    ### forms

    def form_post(self, request, user):

        # genshi data
        self.site_nav(request)
        data = request.environ['data']
        data['user'] = user
        data['stylesheets'] = self.stylesheets(request)

        # render the template
        template = self.loader.load('post.html')
        return template.generate(**data).render()


    def preferences(self, request, user, errors=None, message=None):
        """user preferences form"""
        
        # genshi data
        self.site_nav(request)
        data = request.environ['data']
        data['user'] = user
        data['stylesheets'] = self.stylesheets(request)

        # form data
        prefs = request.user.settings
        data['date_format'] = prefs.get('Date format', self.date_format)
        data['now'] = datetime.datetime.now().strftime(data['date_format'])
        subject = prefs.get('Subject', self.subject)
        data['subject'] = subject.split('%(date)s', 1)
        data['css_files'] = [ i['name'] for i in prefs['CSS' ] ]
        data['users'] = [ i for i in list(self.users.users()) 
                          if i != user ]
        data['message'] = message
        data['errors'] = errors or {}

        # render the template
        template = self.loader.load('preferences.html')
        return template.generate(**data).render()
            

class BitsierBlog(BitsyBlog):
    """single user version of bitsyblog"""

    defaults = BitsyBlog.defaults.copy()
    defaults['user'] = None

    def __init__(self, kw, handler_args):
        BitsyBlog.__init__(self, kw, handler_args)
        assert self.user, 'BitsierBlog: no user given'

    def get(self, request):

        ### user space
        user, path = self.userpath(request)
        if user not in self.users:
            return exc.HTTPNotFound("Blog entry not found")

        return self.get_user_space(user, path, request)

    def userpath(self, request):
        path = request.path_info.strip('/').split('/')
        if path == ['']:
            path = []
        request.user = self.users[self.user]
        return self.user, path

    def user_url(self, request, user, *args, **kw):
        permalink = kw.get('permalink', False)
        return self.link(request, args, permalink)

    def passwords(self):
        return { self.user: self.users.password(self.user) }

    def site_nav(self, request):
        """returns HTML for site navigation"""
        links = [(self.user_url(request, self.user), self.user), ]
        user = self.authenticated(request)
        if user:
            links.extend([(self.user_url(request, user, 'post'), 'post'),
                          (self.user_url(request, user, 'preferences'), 'preferences'),
                          (self.link(request, 'logout'), 'logout')])
        else:
            links.append((self.link(request, 'login'), 'login'))

        if hasattr(self, 'help'):
            links.append((self.link(request, 'help'), 'about'))


        request.environ['data']['links'] = links

