from Acquisition import aq_base, aq_inner, aq_parent
from zope.interface import implements
from zope.component import getUtility

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import DeleteObjects, AddPortalContent,\
    ReviewPortalContent, ModifyPortalContent, RequestReview

from Products.CMFEditions.Permissions import AccessPreviousVersions
from plone.memoize.instance import memoize

from collective.edm.listing.interfaces import IListingRights
from collective.edm.listing.utils import get_workflow_policy

from collective.externaleditor.browser.controlpanel import IExternalEditorSchema
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot


class DefaultListingRights(BrowserView):

    implements(IListingRights)

    def update(self):
        """Update global information
        """
        self.mtool = getToolByName(self.context, 'portal_membership')
        self.wtool = getToolByName(self.context, 'portal_workflow')
        self.portal = getToolByName(self.context, 'portal_url').getPortalObject()
        portal_repository = getToolByName(self.context, 'portal_repository')
        self.member = self.mtool.getAuthenticatedMember()
        self.memberid = self.member.getId()
        self.anonymous = self.mtool.isAnonymousUser()

        roles = self.member.getRolesInContext(self.context)
        self.ismanager = self.member.has_role(('Manager', 'Site Administrator'),
                                              self.context)
        self.isowner = 'Owner' in roles
        self.iseditor = 'Editor' in roles
        self.iscontributor = 'Contributor' in roles
        self.isreviewer = 'Reviewer' in roles
        self.canreview = not self.anonymous \
                    and self._checkPermission(self.context, ReviewPortalContent)
        self.canadd = not self.anonymous \
                    and self._checkPermission(self.context, AddPortalContent)
        self.caneditcontainer = not self.anonymous \
                    and self._checkPermission(self.context, ModifyPortalContent)
        self.candeletecontents = not self.anonymous \
                    and self._checkPermission(self.context, DeleteObjects)
        self.versionable_types = portal_repository.getVersionableContentTypes()
        self.canaccessversions = not self.anonymous \
                    and self._checkPermission(self.context, AccessPreviousVersions)
        self.canaccessreviewhistory = self.canreview or not self.anonymous \
                    and self._checkPermission(self.context, RequestReview)

        self.wfpolicy = get_workflow_policy(self.context)

        externaleditor_schema = IExternalEditorSchema(getUtility(IPloneSiteRoot))
        self.canexternaledit = not self.anonymous \
                    and self.member.getProperty('ext_editor', False) \
                    and getattr(externaleditor_schema,'ext_editor', False)
        self.external_editable_types = getattr(externaleditor_schema,
                                            'externaleditor_enabled_types', [])

    def _checkPermission(self, obj, permission):
        return self.member.checkPermission(permission, obj)

    def _checkAPermission(self, obj, permissions):
        for permission in permissions:
            if self._checkPermission(obj, permission):
                return True
        else:
            return False

    @memoize
    def _getChainForType(self, portal_type):
        chain = ()
        if self.wfpolicy:
            chain = self.wfpolicy.getPlacefulChainFor(portal_type, start_here=False)
        else:
            chain = self.wtool.getChainForPortalType(portal_type)

        return chain

    @memoize
    def _isUniqueStateWorkflow(self, workflow_id):
        return len(self.wtool[workflow_id].states) <= 1

    def globally_show_author(self):
        """View author column
        """
        if self.anonymous:
            return getToolByName(self.context, 'portal_properties').site_properties.getProperty('allowAnonymousViewAbout', True)
        else:
            return True

    def globally_can_delete(self, brains):
        """View delete column
        """
        return self.candeletecontents

    def globally_can_edit(self, brains):
        """View edit column
        """
        if self.iseditor or self.isowner or self.ismanager \
            or self.canreview or self.caneditcontainer:
            return True
        elif self.canadd:
            for brain in brains:
                if brain.Creator == self.memberid:
                    return True
            else:
                return False
        else:
            return False

    def globally_can_copy(self, brains):
        """View copy column
        """
        return not self.anonymous

    def globally_can_cut(self, brains):
        """View cut column
        """
        return self.globally_can_delete(brains)

    def can_delete(self, brain):
        """View delete button associated to this brain
        """
        if self.iseditor or self.ismanager or self.isowner:
            return True
        elif brain.Creator == self.memberid:
            return True
        else:
            return False

    def can_edit(self, brain):
        """View edit button associated to this brain
        """
        if self.use_edit_popup(brain):
            return True
        elif self.ismanager or self.caneditcontainer:
            return True
        elif self.memberid == brain.Creator:
            return True
        else:
            return False

    def can_copy(self, brain):
        """View copy button associated to this brain
        """
        return True

    def can_cut(self, brain):
        """View cut button associated to this brain
        """
        return self.can_delete(brain)

    def use_edit_popup(self, brain):
        """Determine if, when user can edit content (True), popup is used
        or if we just have a link towards base_edit (False)
        Try to avoid popup for users that may have only one edit option
        """
        chain = self._getChainForType(brain.portal_type)
        if not chain or self._isUniqueStateWorkflow(chain[0]):
            # unique state workflow
            if not self.canexternaledit:
                return False
            elif not brain.portal_type in self.external_editable_types:
                return False
            else:
                return self._checkPermission(brain.getObject(), ModifyPortalContent)

        if self.ismanager or self.canreview:
            return True
        if self.canexternaledit and brain.portal_type in self.external_editable_types:
            return True
        elif self._checkPermission(brain.getObject(), ReviewPortalContent):
            return True
        else:
            return False

    def globally_show_history(self):
        """If false, never show history link
        """
        return self.canaccessreviewhistory or self.canaccessversions or self.canadd

    def show_history(self, brain):
        """View history button
        """
        # show history button if content is versioned or has a workflow
        # or has'nt been modified yet
        if not (self.canaccessreviewhistory
                or self.canaccessversions
                or self.memberid == brain.Creator):
            return False

        if brain.portal_type in self.versionable_types \
                and brain.modified != brain.created:
            return True

        chain = self._getChainForType(brain.portal_type)
        if chain and self.wtool[chain[0]].initial_state != brain.review_state:
            return True
        else:
            return False

    def globally_show_download(self, brains):
        """View download column
        """
        for brain in brains:
            if self.show_download(brain):
                return True
        else:
            return False

    def show_download(self, brain):
        """View download column,
        return download view
        """
        return brain.meta_type in ('ATBlob', 'ATImage', 'ATFile') and 'download' or False

    def globally_show_quickview(self, brains):
        """View quickview column
        """
        for brain in brains:
            if self.show_quickview(brain):
                return True
        else:
            return False

    def show_quickview(self, brain):
        """View quick view cell,
        return true or quick view
        """
        return brain.portal_type in ('Image',) and 'image_large' or False

    def globally_show_state(self, brains):
        """View state column
        """
        if self.anonymous:
            return False
        else:
            for brain in brains:
                if brain.review_state:
                    return True
            else:
                return False

    def globally_show_size(self, brains):
        """View size column
        """
        for brain in brains:
            if self.show_size(brain):
                return True
        else:
            return False

    def show_size(self, brain):
        """View size value on item
        """
        if brain.portal_type in ('File', 'Image'):
            return True
        else:
            return False

    def globally_show_sort(self):
        """View sort column
        """
        return self.caneditcontainer

    def globally_show_modified(self):
        """View modification date column
        """
        return True

    def show_folder_buttons(self):
        """Check if buttons are hidden even for allowed users
        """
        return True

    def sortable_columns(self):
        return False

    def can_trash(self, brain):
        return self.can_delete(brain)

    def globally_show_trashcan(self, brains=[]):
        return self.candeletecontents
