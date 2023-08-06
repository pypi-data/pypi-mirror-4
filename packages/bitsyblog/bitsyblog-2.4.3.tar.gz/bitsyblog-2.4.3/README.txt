bitsyblog
=========

*bitsyblog doesn't do much, but it could do less*


Why another blog?
-----------------

My ideal blog would invoke my favorite editor, take a bunch of text, and 
throw it on the web.  Sometimes I like to write long elaborate posts.
Othertimes I just want to make a quick note.

Meet `bitsyblog <http://bitsyblog.biz>`_, 
a tiny tiny `python <http://python.org/>`_
`weblog <http://pypi.python.org/pypi/bitsyblog/>`_.  
Posting is done with a POST request, so while you can use
a web form to do this, its just as easy to use curl, urllib, or anything else 
to post.


How does it work?
-----------------

A user URLs is like

http://bitsyblog.biz/k0s

k0s is my user name here .  If you are 1337h4x0r, this will be 
http://bitsyblog.biz/1337h4x0r .
Posting to this will take the body of the POST request and add a date stamp
Blog entries are thrown in files and are displayed with markup 
available with `restructured text 
<http://docutils.sourceforge.net/docs/user/rst/quickref.html>`_.

You can also get a more specific range of posts 
by specifying up to the year, month
and day in the URL:

http://bitsyblog.biz/k0s/2008/2/1

Not all of this needs to be specified.

Permalinks are also available in the form of the date stamp:

http://bitsyblog.biz/k0s/20080201141502

You can find the permalink by clicking on the subject of the blog post.

If you really want to post through the web, support is at 

http://bitsyblog.biz/k0s/post

If you're more friendly with python scripts, 
`blogme.py <https://svn.openplans.org/svn/standalone/bitsyblog/trunk/blogme.py>`_
is available: 
https://svn.openplans.org/svn/standalone/bitsyblog/trunk/blogme.py


Get me a blog!
--------------

Create an account at http://bitsyblog.biz/join .  All you need is a
username and password (and I threw a 
`CAPTCHA <http://skimpygimpy.sourceforge.net/>`_ in there at some
point).
Then...you're ready to blog!  The auth is a minimal thing
I threw together out of `paste.auth <http://pythonpaste.org/>`_.

Once you're signed in, you'll notice the navigation links at the top
of the page have changed.  You can now post and change your preferences.

In your preferences, you can change the date format and set the
subject format of your blog posts.  You can also upload 
verifiable CSS to theme your blog.  For the date format, I have patched
`dateutil.parser <http://labix.org/python-dateutil>`_
to return the format string that the date was originally in and hope
that my changes can make it back to the source sometime.

When posting, you have the option to make your post 'public' (everyone
can see it), 'secret' (only your friends can see it), 'private' (only
you can see it.  Friends are settable in your preferences.


What bitsyblog doesn't do
-------------------------

* Commenting:  this should done with 
`WSGI middlware
<http://groovie.org/articles/2005/10/06/wsgi-and-wsgi-middleware-is-easy>`_.  
There's nothing specific about commenting on a blog post that is any
different from commenting on a paragraph in (for instance) a wiki article.

* Tagging:  again, this should be done with middleware

* Hosting files:  Its a blog, not a file repo!  Any markup doable with 
`restructured text <http://docutils.sourceforge.net/rst.html>`_
is doable with bitsyblog, but images, videos, whatever must
be held off-site.


What is next for bitsyblog?
---------------------------

Other than that, its a pretty small project.  No templates and
currently about 700 lines of code. (I'll get it back to 500, I
swear). bitsyblog is designed as a personal blog that should be strong
in both workflow as well as "niceness" of code.

I'm guessing your blog doesn't do much...but could it do less?


bitsyblog is built on top of `paste <http://pythonpaste.org/>`_
and `webob <http://pythonpaste.org/webob/>`_.  You'll need the 
trunk version of paste for a change made to 
`paste.auth.auth_tkt
<http://svn.pythonpaste.org/Paste/trunk/paste/auth/auth_tkt.py>`_ 
in order to have cookies work correctly (r7261).

Thanks to `The Open Planning Project <http://www.openplans.org>`_ 
and my friends there for making this possible.

Please email jhammel at openplans dot org with any questions.

