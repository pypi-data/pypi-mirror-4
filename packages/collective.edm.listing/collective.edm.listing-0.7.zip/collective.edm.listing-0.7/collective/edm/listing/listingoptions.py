from zope.interface import implements

from Products.Five.browser import BrowserView

from collective.edm.listing.interfaces import IEDMListingOptions


class DefaultListingOptions(BrowserView):
    implements(IEDMListingOptions)

    sort_mode = 'manual'
    default_sort_on = False
    default_sort_order = 'asc'
    allow_edit_popup = True
