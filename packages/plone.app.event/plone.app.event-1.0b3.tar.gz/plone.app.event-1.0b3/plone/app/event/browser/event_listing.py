from Products.CMFPlone.PloneBatch import Batch
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zope.contentprovider.interfaces import IContentProvider

from plone.app.event.base import date_speller
from plone.app.event.base import get_occurrences_from_brains
from plone.app.event.base import get_portal_events
from plone.app.event.base import start_end_from_mode
from plone.app.event.base import guess_date_from


class EventListing(BrowserView):

    def __init__(self, context, request):
        super(EventListing, self).__init__(context, request)

        # Batch parameter
        req = self.request
        self.b_start = 'b_start' in req and int(req['b_start']) or 0
        self.b_size  = 'b_size'  in req and int(req['b_size'])  or 10
        self.orphan  = 'orphan'  in req and int(req['orphan'])  or 1
        self.mode    = 'mode'    in req and req['mode']         or None
        self.date    = 'date'    in req and req['date']         or None

    def get_events(self, start=None, end=None, batch=True, mode=None):
        context = self.context

        mode = mode or self.mode
        if not mode and not start and not end:
            mode = 'future'
        if mode:
            dt = None
            if self.date:
                try:
                    dt = guess_date_from(self.date)
                except TypeError:
                    pass
            start, end = start_end_from_mode(mode, dt, context)

        b_start = b_size = None
        if batch:
            b_start=self.b_start
            b_size=self.b_size

        occs = get_occurrences_from_brains(
                context,
                get_portal_events(context, start, end,
                    #b_start=b_start, b_size=b_size,
                    path=context.getPhysicalPath()),
                start,
                end)

        if batch:
            ret = Batch(occs, size=b_size, start=b_start, orphan=self.orphan)
        else:
            ret = occs

        return ret

    def formated_date(self, occ):
        provider = getMultiAdapter((self.context, self.request, self),
                IContentProvider, name=u"formated_date")
        return provider(occ.context)

    def date_speller(self, date):
        return date_speller(self.context, date)
