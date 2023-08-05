from zope.interface import implements

from plone.app.portlets.portlets.search import ISearchPortlet, Renderer as baseRenderer, AddForm as BaseAddForm, EditForm as BaseEditForm
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from redturtle.portlet.contextualsearch import ContextualSearchPortletMessageFactory as _

from zope.component import getMultiAdapter

from Acquisition import aq_inner


class IContextualSearchPortlet(ISearchPortlet):
    """A portlet that allows contextual search and extend search portlet base
    """
    portletTitle = schema.TextLine(title=_(u"portlet_title", default=u"Portlet title"),
                                   description=_(u"Insert the portlet title"),
                                   required=False)

    searchFolder = schema.Choice(title=_(u"Target folder"),
                                 required=False,
                                 description=_(u"Choose the folder to use for searches. If left blank, the search will use the current context as the starting folder"),
                                 source=SearchableTextSourceBinder({'is_folderish': True},
                                                                    default_query='path:'))


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IContextualSearchPortlet)

    def __init__(self, portletTitle='', enableLivesearch=True, searchFolder='', showAdvanced=False):
        self.enableLivesearch = enableLivesearch
        self.portletTitle = portletTitle
        self.searchFolder = searchFolder
        self.showAdvanced = showAdvanced

    @property
    def title(self):
        title = "Contextual search portlet"
        if self.data.portletTitle:
            return title + ": " + self.data.portletTitle
        return title


class Renderer(baseRenderer):
    """Portlet renderer."""

    render = ViewPageTemplateFile('contextualsearchportlet.pt')

    def getPosition(self):
        """returns the actual position for the contextual search"""
        if self.data.searchFolder:
            root_path = '/'.join(self.context.portal_url.getPortalObject().getPhysicalPath())
            return root_path + self.data.searchFolder
        else:
            folder = self.getRightContext()
            return '/'.join(folder.getPhysicalPath())

    def getPortletTitle(self):
        """return the portlet title"""
        if self.data.portletTitle:
            return self.data.portletTitle
        else:
            return "search"

    def getRightContext(self):
        """
        """
        plone_view = getMultiAdapter((aq_inner(self.context), self.request), name='plone')
        if plone_view.isDefaultPageInFolder():
            return plone_view.getParentObject()
        else:
            return self.context


class AddForm(BaseAddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IContextualSearchPortlet)
    form_fields['searchFolder'].custom_widget = UberSelectionWidget

    def create(self, data):
        return Assignment(**data)


class EditForm(BaseEditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IContextualSearchPortlet)
    form_fields['searchFolder'].custom_widget = UberSelectionWidget
