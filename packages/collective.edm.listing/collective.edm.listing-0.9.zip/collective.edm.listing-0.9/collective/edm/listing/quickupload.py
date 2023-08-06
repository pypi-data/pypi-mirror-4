from Acquisition import aq_inner

from collective.quickupload.interfaces import IQuickUploadNotCapable
from collective.quickupload.portlet.quickuploadportlet import JAVASCRIPT

from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class QuickUploadViewlet(ViewletBase):

    index = ViewPageTemplateFile('templates/quickupload.pt')

    def __init__(self, context, request, view, manager=None):
        super(ViewletBase, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    def javascript(self):
        return JAVASCRIPT

    def available(self):
        return not IQuickUploadNotCapable.providedBy(self.context)

    def getUploadUrl(self):
        """
        return upload url
        in current folder
        """
        context = aq_inner(self.context)
        folder_url = context.restrictedTraverse('@@plone').getCurrentFolderUrl()
        return '%s/@@quick_upload' %folder_url
