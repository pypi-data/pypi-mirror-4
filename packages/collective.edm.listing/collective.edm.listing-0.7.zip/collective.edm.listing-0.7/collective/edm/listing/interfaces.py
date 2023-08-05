from zope.interface import Interface, Attribute
from zope import schema
from zope.interface.interface import Attribute


class IEDMListing(Interface):
    """Interface of IEDMListing view
    """

class IEDMListingLayer(Interface):
    """Layer marker interface
    """

class IListingRights(Interface):
    """View to be customized on your project
    provides the more intelligent way
    to compute if listing actions are displayed or not
    """

    def globally_show_author():
        """View author column
        """

    def globally_can_delete(brains):
        """View delete column
        """

    def globally_can_edit(brains):
        """View edit column
        """

    def globally_can_copy(brains):
        """View copy column
        """

    def globally_can_cut(brains):
        """View cut column
        """

    def can_delete(brain):
        """View delete button associated to this brain
        """

    def can_edit(brain):
        """View edit button associated to this brain
        """

    def can_copy(brain):
        """View copy button associated to this brain
        """

    def can_cut(brain):
        """View cut button associated to this brain
        """

    def use_edit_popup(brain):
        """Determine if, when user can edit content (True), popup is used
        or if we just have a link towards base_edit (False)
        Try to avoid popup for users that may have only one edit option
        """

    def globally_show_history():
        """If false, never show history link
        """

    def show_history(brain):
        """View history button
        """

    def globally_show_state(brains):
        """View state column
        """

    def globally_show_size(brains):
        """View size column
        """

    def show_size(brain):
        """View size value on item
        """

    def globally_show_sort():
        """View sort column
        """
        return self.caneditcontainer

    def globally_show_modified():
        """View modification date column
        """

    def show_folder_buttons():
        """Check if buttons are hidden even for allowed users
        """
        return True


class IEDMListingOptions(Interface):

    sort_mode = Attribute("""returns 'manual' or 'auto'
        manual sort uses object position in parent
        automatic sort allows visitors to sort on columns
        """)

    default_sort_on = Attribute(
        """If sort_mode is automatic, sort by default on this index
        """)

    default_sort_order = Attribute(
        """If sort_mode is automatic, sort by default on this index
        """)

    allow_edit_popup = Attribute(
        """If it is false,
        edit buttons do not display a popup but only redirect to edit form
        """)


class IEDMListingSettings(Interface):
    """
    """

    downloadZopeedit = schema.TextLine()


class IEDMListingSupplColumn(Interface):

    header = Attribute("Column header")
    sort_index = Attribute("If defined, the column is sortable on this index")

    def value(item):
        """Column value for item
        """

    def available(items):
        """Returns True if column should be displayed, False if not
        if this method doesn't exist, always display the column
        """
