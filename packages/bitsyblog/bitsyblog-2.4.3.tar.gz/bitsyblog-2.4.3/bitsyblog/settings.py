"""user settings / preferences"""

import parser # bitsyblog dateutils.parser with mods to retain strftime format
import urllib2
import utils

class InvalidSettingError(Exception):
    """error when trying to validate a setting"""

class Setting(object):
    def __init__(self, name, value=None):
        self.name = name
        self.value = value
        self.error_message = 'Invalid value for %s' % name

    def validator(self, value):
        return True

    def set(self, value):
        if not self.validator(value):
            raise InvalidSettingError(self.error_message)
        self.value = value

class DateFormat(Setting):
    def __init__(self):
        Setting.__init__(self, 'Date format')

    def set(self, format):
        value = parser.parser()._parse(format)
        if value:
            self.value = value.format
        else:
            raise InvalidSettingError('unrecognized date format: %s' % format)

    
class CSSFile(Setting):
    def __init__(self):
        Setting.__init__(self, 'CSS file')

    def set(self, value):
        if not hasattr(value, 'file'):
            return True # blank set: don't do anything
        css = value.file.read()
        try:
            validcss = utils.validate_css(css)
        except urllib2.URLError:
            raise InvalidSettingError('Could not validate CSS (sorry!)')
        if not validcss:
            raise InvalidSettingError('%s is not valid css' % filename)
        filename = value.filename
        if not filename.endswith('.css'):
            filename = '%s.css' % filename
        self.value = dict(filename=filename, css=css)

user = [ DateFormat(),
         Setting('Subject'),
         Setting('Friends'),
         Setting('Stylesheet'),
         ]

form = user[:]
form += [ CSSFile() ]
