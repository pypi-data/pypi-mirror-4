from string import Template
from Acquisition import aq_inner
from zope.component import getMultiAdapter
from zope.interface import implements

try:
    from Products.CMFPlone import Batch
except ImportError:
    # plone 4.1
    from Products.CMFPlone.PloneBatch import Batch
from Products.Five import BrowserView

from plone.memoize import view

class BlogView(BrowserView):
    """ A blog browser view """

    def __init__(self, context, request):
        super(BlogView, self).__init__(context, request)
        self.context = context
        self.request = request

    @property
    def tools(self):
        return getMultiAdapter((self.context, self.request), name=u'plone_tools')

    @property
    def portal_state(self):
        return getMultiAdapter((self.context, self.request), name=u'plone_portal_state')

    def getFieldValue(self, name, obj=None):
        if obj is None:
            obj = self.context

        field = obj.getField(name)
        if field:
            return field.get(obj)
        return None

    @view.memoize
    def contents(self):
        brains = []
        criteria = {}

        # filter criteria
        subject = self.request.get('subject', None)
        if subject and subject != ['']:
            criteria['Subject'] = subject

        year = self.request.get('publish_year', None)
        if year:
            criteria['publish_year'] = int(year)

        month = self.request.get('publish_month', None)
        if month:
            # Note: months are indexed as for example '03'
            criteria['publish_month'] = month

        criteria['path'] = '/'.join(self.context.getPhysicalPath())
        criteria['portal_type'] = 'Blog Entry'
        criteria['sort_on'] = 'effective'
        criteria['sort_order'] = 'reverse'

        return self.tools.catalog()(criteria)

    def batch(self):
        b_start = self.request.get('b_start', 0)
        return Batch(self.contents(), self.batch_size, int(b_start), orphan=0)

    @property
    def count(self):
        return len(self.contents())

    @property
    def site_props(self):
        pprops = self.tools.properties()
        return getattr(pprops, 'site_properties')

    @property
    def show_body(self):
        field = self.context.getField('enable_full')
        if field:
            return field.get(self.context)
        return False

    @property
    def batch_size(self):
        field = self.context.getField('batch_size')
        if field:
            return field.get(self.context)
        return 10
