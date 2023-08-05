from zope.interface import implements
from dateable.chronos.interfaces import IEvent
from Products.ATContentTypes.interfaces import IATEvent
from zope import component

from Products.ATContentTypes.utils import DT2dt

class Event(object):

    implements(IEvent)
    component.adapts(IATEvent)

    def __init__(self, event):
        self.event = event

    def __cmp__(self, other):
        return cmp(self.event.start, other.event.start)

    @property
    def title(self): return self.event.Title()
    @property
    def description(self): return self.event.Description()
    @property
    def start(self): return DT2dt((self.event.start()))
    @property
    def end(self): return DT2dt((self.event.end()))
    @property
    def location(self): return ''
    @property
    def local_url(self): return self.event.absolute_url()
    @property
    def url(self): return self.event.absolute_url()
    @property
    def type(self): return ','.join(self.event.getEventType())
    @property
    def timezone(self): return self.event.start.timezone()

from zope.component import getGlobalSiteManager
gsm = getGlobalSiteManager()
gsm.registerAdapter(Event, (IATEvent,), IEvent, 'CalendarEventAdapter')

try:
    from Products.RadioSchedule.contents.interfaces import IRadioshow

    class RadioEvent(object):

        implements(IEvent)
        component.adapts(IRadioshow)

        def __init__(self, event):
            self.event = event

        def __cmp__(self, other):
            return cmp(self.event.start, other.event.start)

        @property
        def title(self): return self.event.Title()
        @property
        def description(self): return self.event.Description()
        @property
        def start(self): return DT2dt((self.event.start()))
        @property
        def end(self): return DT2dt((self.event.end()))
        @property
        def location(self): return ''
        @property
        def local_url(self): return self.event.absolute_url()
        @property
        def url(self): return self.event.absolute_url()
        @property
        def type(self): return 'Radio show'
        @property
        def timezone(self): return self.event.start.timezone()

    from zope.component import getGlobalSiteManager
    gsm = getGlobalSiteManager()
    gsm.registerAdapter(RadioEvent, (IRadioshow,), IEvent,
                        'RadioshowCalendarEventAdapter')

except ImportError: pass
