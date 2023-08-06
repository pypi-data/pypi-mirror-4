"""
calendar navigation for bitsyblog
"""

import cal

class LinkCalendar(cal.HTMLCalendar):

    def __init__(self):
        cal.Calendar.__init__(self, firstweekday=6)

    def formatweekheader(self):
        return '' # no need for listing weekdays
