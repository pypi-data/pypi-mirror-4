from zope.interface import implements
from Acquisition import aq_inner
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
from zope.i18nmessageid import MessageFactory
__ = MessageFactory("plone")


class Ifeaturedportlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(Ifeaturedportlet)

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return __(u"CS Featured Portlet")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('featuredportlet.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        portal_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_portal_state')
        self.portal_url = portal_state.portal_url()

    def featured_items(self, count=None):
        context = aq_inner(self.context)
        pcat = getToolByName(context, 'portal_catalog')
        if count is None:
            items = pcat(portal_type='featured')
        else:
            items = pcat(portal_type='featured',
                         sort_on='sortable_title',
                         sort_limit=count)

        return  [f.getObject() for f in items]


class AddForm(base.NullAddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """

    def create(self):
        return Assignment()
