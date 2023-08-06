from zope.component import getMultiAdapter, getAdapters, adapts

from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.publisher.browser import BrowserView
from zope.interface import implements, Interface

from plone.app.content.browser.foldercontents import FolderContentsView as FolderContentsViewOrig
from plone.app.content.browser.foldercontents import FolderContentsTable as FolderContentsTableOrig
from plone.app.content.browser.tableview import Table as TableOrig
from plone.memoize import instance
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IFolderish

from collective.edm.listing.interfaces import IEDMListing, IEDMListingSupplColumn,\
    IEDMListingFolderContents
from collective.edm.listing.utils import get_workflow_policy


class Table(TableOrig):

    render = ViewPageTemplateFile("templates/table.pt")
    batching = ViewPageTemplateFile("templates/batching.pt")

    def __init__(self, *args, **kwargs):
        context = kwargs['context']
        del kwargs['context']
        super(Table, self).__init__(*args, **kwargs)
        self.context = context
        self.mtool = getToolByName(context, 'portal_membership')
        self.wtool = getToolByName(context, 'portal_workflow')
        qitool = getToolByName(self.context, 'portal_quickinstaller')
        portal_url = self.portal_url = getToolByName(context, 'portal_url')()
        self.icon_edit = portal_url + '/edit.png'
        self.icon_cut = portal_url + '/cut_icon.png'
        self.icon_copy = portal_url + '/copy_icon.png'
        self.icon_delete = portal_url + '/delete_icon.png'
        self.icon_history = portal_url + '/history.png'
        self.icon_download = portal_url + '/download_icon.png'
        self.icon_quickview = portal_url + '/search_icon.png'
        self.icon_trash = portal_url + '/ecreall-trashcan.png'
        self.icon_restore = portal_url + '/ecreall-trashcan-restore.png'
        self.listingrights = context.unrestrictedTraverse('@@edmlistingrights')
        self.listingrights.update()
        self.listingoptions = context.unrestrictedTraverse('@@edmlistingoptions')
        self.plone_view = context.unrestrictedTraverse('@@plone')
        self.brains = []
        self.wf_policy = get_workflow_policy(context)
        for item in self.items:
            if not 'brain' in item:
                # bypass items not in page
                continue

            if 'view_url' in item and item['view_url'].endswith('folder_contents'):
                item['view_url'] = item['view_url'].replace('/folder_contents', '')

            if 'url_href_title' in item and item['url_href_title'].endswith(': '):# todo: fix it in plone
                item['url_href_title'] = item['url_href_title'][:-2]

            if item['brain'].getIcon:
                item['icon_url'] = '%s/%s' % (self.portal_url, item['brain'].getIcon)
            else:
                item['icon_url'] = ''

            if self.wf_policy and item['brain'].review_state:
                chain = self._getPlacefulChainForType(item['brain'].portal_type)
                if chain:
                    workflow = self.wtool[chain[0]]
                    state = workflow.states.get(item['brain'].review_state, None)
                    if state:
                        item['state_title'] = state.title

            self.brains.append(item['brain'])

        self.has_ecreall_trashcan = qitool.isProductInstalled('ecreall.trashcan')
        self.sortable_columns = self.listingoptions.sort_mode == 'auto'
        self.show_sort_column = not self.sortable_columns and self.listingrights.globally_show_sort()
        self.show_trashcan_column = self.showTrashcan()
        suppl_columns = getAdapters((context, self.request, self),
                                    IEDMListingSupplColumn)
        self.suppl_columns = []
        for name, column in suppl_columns:
            if hasattr(column, 'available'):
                if not column.available(self.brains):
                    continue

            self.suppl_columns.append(column)

    @instance.memoize
    def _getPlacefulChainForType(self, portal_type):
        return self.wf_policy.getPlacefulChainFor(portal_type, start_here=False)

    @instance.memoize
    def getMemberInfo(self, member):
        return self.mtool.getMemberInfo(member)

    def showDownload(self):
        return self.listingrights.globally_show_download(self.brains)

    def showQuickView(self):
        return self.listingrights.globally_show_quickview(self.brains)

    def downloadItemView(self, item):
        download = self.listingrights.show_download(item['brain'])
        if download and not isinstance(download, basestring):
            download = 'download'

        return download

    def quickViewItemView(self, item):
        quickview = self.listingrights.show_quickview(item['brain'])
        if quickview and not isinstance(quickview, basestring):
            quickview = 'image_large'

        return quickview

    def checkEdit(self):
        return self.listingrights.globally_can_edit(self.brains)

    def checkEditItem(self, item):
        return self.listingrights.can_edit(item['brain'])

    def checkRemove(self):
        return self.listingrights.globally_can_cut(self.brains)

    def checkRemoveItem(self, item):
        """ can trash or cut """
        return self.listingrights.can_delete(item['brain'])

    def checkCopy(self):
        return self.listingrights.globally_can_copy(self.brains)

    def checkCopyItem(self, item):
        return self.listingrights.can_copy(item['brain'])

    def checkDelete(self):
        return self.listingrights.globally_can_delete(self.brains)

    def checkDeleteItem(self, item):
        return self.listingrights.can_delete(item['brain'])

    def useEditPopup(self, item):
        if self.listingoptions.allow_edit_popup:
            return self.listingrights.use_edit_popup(item['brain'])
        else:
            return False

    def showHistory(self):
        return self.listingrights.globally_show_history()

    def showItemHistory(self, item):
        return self.listingrights.show_history(item['brain'])

    def showState(self):
        return self.listingrights.globally_show_state(self.brains)

    def showSize(self):
        return self.listingrights.globally_show_size(self.brains)

    def showAuthor(self):
        return self.listingrights.globally_show_author()

    def itemSize(self, item):
        if not self.listingrights.show_size(item['brain']):
            return u""
        else:
            return item['size'] or u""

    def showModified(self):
        return self.listingrights.globally_show_modified()

    def showTrashcan(self):
        if not self.has_ecreall_trashcan:
            return False
        elif self.context.unrestrictedTraverse('isTrashcanOpened')():
            return False
        else:
            return self.listingrights.globally_show_trashcan(brains=self.brains)

    def showTrashcanRestore(self):
        if not self.has_ecreall_trashcan:
            return False
        elif not self.context.unrestrictedTraverse('isTrashcanOpened')():
            return False
        else:
            return self.listingrights.globally_show_trashcan(brains=self.brains)

    def checkTrashItem(self, item):
        return self.listingrights.can_trash(item['brain'])

    def paste_button(self):
        for button in self.buttons:
            if button['id'] == 'paste':
                try:
                    self.context.cb_dataItems()
                    button['cssclass'] = 'standalone'
                    return button
                except:
                    return None
        else:
            return None

    def listing_buttons(self):
        if not self.listingrights.show_folder_buttons():
            return []

        buttons = []
        for button in self.buttons:
            if button['id'] == 'paste':
                continue
            elif button['id'] == 'cut':
                if self.checkRemove():
                    buttons.append(button)
            elif button['id'] == 'delete':
                if self.checkDelete():
                    buttons.append(button)
            elif button['id'] == 'moveToTrashcan':
                if self.showTrashcan():
                    buttons.append(button)
            elif button['id'] == 'restoreFromTrashcan':
                if self.showTrashcanRestore():
                    buttons.append(button)
            else:
                buttons.append(button)

        return buttons

    def sort_on_size(self):
        return 'sortable_size' in getToolByName(self.context, 'portal_catalog').indexes()

    def arrow(self, sort_index):
        if sort_index != self.request.get('sort_on', None):
            return u""
        elif not 'sort_order' in self.request:
            return u""
        elif self.request.get('sort_order', 'descending') == 'descending':
            return u"""<img class="sortdirection" src="%s/listing-arrowup.gif" />""" % self.portal_url
        else:
            return u"""<img class="sortdirection" src="%s/listing-arrowdown.gif" />""" % self.portal_url


class FolderContentsTable(FolderContentsTableOrig):
    """
    The foldercontents table renders the table and its actions.
    """
    implements(IEDMListingFolderContents)
    adapts(IFolderish, Interface)

    __table__ = Table

    def __init__(self, context, request, contentFilter=None):
        self.context = context
        self.request = request
        self.contentFilter = contentFilter is not None and contentFilter or {}
        self.listingoptions = self.context.unrestrictedTraverse('@@edmlistingoptions')
        if self.listingoptions.sort_mode == 'auto':
            default_sort_on = self.listingoptions.default_sort_on
            default_sort_order = self.listingoptions.default_sort_order
        else:
            default_sort_on, default_sort_order = False, False

        sort_order = self.request.get('sort_order', default_sort_order)
        if sort_order:
            self.request['sort_order'] = sort_order
            self.contentFilter['sort_order'] = sort_order

        sort_on = self.request.get('sort_on', default_sort_on)
        if sort_on:
            # if there is a sortable_xx index matching
            # (ex : sortable_title, sortable_creator), use it
            catalog = getToolByName(self.context, 'portal_catalog')
            sortable_index = 'sortable_%s' % sort_on.lower()
            if sortable_index in catalog.indexes():
                self.contentFilter['sort_on'] = sortable_index
                self.request['sort_on'] = sortable_index
            else:
                self.contentFilter['sort_on'] = sort_on
                self.request['sort_on'] = sort_on

        self.items = self.folderitems()
        url = context.absolute_url()
        view_url = url + '/edm_folder_listing'
        self.table = self.__table__(request, url, view_url, self.items,
                           show_sort_column=self.show_sort_column,
                           buttons=self.buttons, context=context)


class FolderContentsView(FolderContentsViewOrig):
    """
    """
    implements(IEDMListing)

    def __init__(self, context, request):
        # avoids setting IContentsPage on our FolderContentsView
        BrowserView.__init__(self, context, request)

    def contents_table(self):
        table = getMultiAdapter((self.context, self.request), IEDMListingFolderContents)
        return table.render()

