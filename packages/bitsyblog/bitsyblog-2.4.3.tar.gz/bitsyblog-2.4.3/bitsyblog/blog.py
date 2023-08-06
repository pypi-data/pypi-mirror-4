"""blog interfaces to data for bitsy"""

import datetime
import os
import utils

from cStringIO import StringIO
from glob import glob
from pkg_resources import iter_entry_points

class BlogEntry(object):
    """interface class for a blog entry"""
    def __init__(self, date, body, privacy, user, modified=None):
        self.date = date
        self.body = body
        self.privacy = privacy
        self._modified = modified
        if user is not None:
            self.user = user

    def title(self, characters=80):

        if '\n' in self.body:
            lines = [i.strip() for i in self.body[:characters].split('\n')]
            if len(lines[0]) > characters:
                retval = self.snippet(charachters)
            elif len(lines) > 1 and not lines[1]:
                retval = lines[0]
            else:
                retval = self.snippet(characters)
        else:
            retval = self.snippet(characters)
        return retval.decode('utf-8')

    def snippet(self, characters=80):
        if characters:
            if len(self.body) > characters:

                text = ' '.join(self.body[:characters].split()[:-1])
                if '\n' in text:
                    lines = [ i.strip() for i in text.split('\n') ]
                    if '' in lines:
                        return '\n'.join(lines[:lines.index('')])

                if text:
                    return '%s ...' % text
            else:
                return self.body
        return ''

    def datestamp(self):
        return utils.datestamp(self.date)

    def modified(self):
        """returns the last modification date"""
        return self._modified or self.datestamp()


class Blog(object):
    """abstract class for a users' blog"""

    def __call__(self, user, permissions=('public',), number=None):
        return self.blog(user, permissions, number=number)

    def latest(self, users, number):
        """return the lastest entries"""
        blog = []
        for user in users:
            blog.extend(self.blog(user, ('public',), number))
        blog.sort(key=lambda entry: entry.date, reverse=True)
        return blog[:number]

    # interfaces for subclasses

    def blog(self, user, permissions, number=None):
        """
        return the user's blog sorted in reverse date order
        if number is None, the entire blog is returned
        """

    def entry(self, user, datestamp, permissions):
        """
        return a single blog entry with the given datestamp:
        'YYYYMMDDHHMMSS'
        """

    def entries(self, user, permissions, year=None, month=None, day=None):
        """return entries by date"""


    def post(self, user, date, text, privacy):
        """post a new blog entry"""
        return BlogEntry(date, text, privacy, user)

    def delete(self, user, datestamp):
        """remove a blog entry"""

class FileBlog(Blog):
    """a blog that lives on the filesystem"""

    def __init__(self, directory):
        self.directory = directory

    def location(self, user, permission, *path):
        """returns which directory files are in based on permission"""
        return os.path.join(self.directory, user, 'entries', permission, *path)

    def body(self, user, datestamp, permission):
        return file(self.location(user, permission, datestamp)).read()

    def get_entry(self, user, datestamp, permission):
        modified = datetime.datetime.fromtimestamp(os.path.getmtime(self.location(user, permission, datestamp)))
        return BlogEntry(utils.date(datestamp),
                         self.body(user, datestamp, permission),
                         permission, user, modified=modified)

    ### interfaces from Blog

    def blog(self, user, permissions, number=None):
        entries = []
        for permission in permissions:
            entries.extend([(entry, permission)
                             for entry in os.listdir(self.location(user, permission)) ])
        entries.sort(key=lambda x: x[0], reverse=True)

        if number is not None:
            entries = entries[:number]

        return [ self.get_entry(user, x[0], x[1]) for x in entries ]

    def entry(self, user, datestamp, permissions):
        for permission in permissions:
            filename = self.location(user, permission, datestamp)
            if os.path.exists(filename):
                return self.get_entry(user, datestamp, permission)

    def entries(self, user, permissions, year=None, month=None, day=None):

        # build a file glob expression
        dateargs = [ year, month, day, None ]
        glob_expr = ''
        for index in range(len(dateargs)):
            value = dateargs[index]
            if value is None:
                break
            length = len(utils.timeformat[index])
            glob_expr += '%0*d' % (length, int(value))
        while index < len(utils.timeformat):
            glob_expr += '[0-9]' * len(utils.timeformat[index])
            index += 1

        # get the blog entries
        entries = []
        for permission in permissions:
            entries.extend([(os.path.split(entry)[-1], permission)
                            for entry in glob(os.path.join(self.location(user, permission), glob_expr))])
        entries.sort(key=lambda x: x[0], reverse=True)
        return [ self.get_entry(user, x[0], x[1]) for x in entries ]

    def post(self, user, datestamp, body, privacy):
        blog = file(self.location(user, privacy, datestamp), 'w')
        print >> blog, body
        return Blog.post(self, user, datestamp, body, privacy)

    def delete(self, user, datestamp):
        for permission in 'public', 'secret', 'private':
            path = self.location(user, permission, datestamp)
            if os.path.exists(path):
                os.remove(path)
