from dateable.chronos.browser.month import MonthView
from dateable.chronos.browser.week import WeekView
from dateable.chronos.browser.day import DayView
from zope.interface import classImplements
from interfaces import ISimpleViewClass, ISimpleViewClassWeek, ISimpleViewClassWeek, ISimpleViewClassDay

getOccurrenceDisplays = MonthView.getOccurrenceDisplays

def new_getOccurrenceDisplays(self, day):
    classImplements(self.__class__, ISimpleViewClass)
    return getOccurrenceDisplays(self, day)

MonthView.getOccurrenceDisplays = new_getOccurrenceDisplays

getEventDisplays = WeekView.getEventDisplays.im_func

def new_getEventDisplays(self):
    classImplements(self.__class__, ISimpleViewClassWeek)
    try:
        return getEventDisplays(self)
    except Exception, value:
        raise
        import pdb
        pdb.set_trace()

WeekView.getEventDisplays = new_getEventDisplays

DayGetEventDisplays = DayView.getEventDisplays.im_func

def new_getEventDisplays(self):
    classImplements(self.__class__, ISimpleViewClassDay)
    return DayGetEventDisplays(self)

DayView.getEventDisplays = new_getEventDisplays

from dateable.chronos.browser.base_view import BaseCalendarView

old_get_action_url = BaseCalendarView.get_action_url

def get_action_url(self, action):
    url = old_get_action_url(self, action)
    if not url.startswith('/') or url.startswith('http://') \
            or url.startswith('https://'):
        return self.context.absolute_url() + '/' + action
    else:
        return action

BaseCalendarView.get_action_url = get_action_url
