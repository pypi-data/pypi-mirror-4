from zope.interface import implements
from zope.formlib.form import Fields

from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.formlib.form import Fields
from plone.memoize.view import memoize
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.i18n.normalizer.interfaces import IIDNormalizer

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.PloneboardPortlet import PloneboardPortletMessageFactory as _

import pdb

class IPloneboardPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    title = schema.TextLine(title=_(u"title_title",
                                default=_(u"Portlet title")),
                        required=True,
                        default=_(u"Ploneboard recent conversations"))

    count = schema.Int(title=_(u"title_count",
                                default=u"Number of conversations to display"),
                       description=_(u"help_count",
                                default=u"How many items to list in portlet."),
                       required=True,
                       default=5)

    pboard = schema.Tuple(title=_(u"Ploneboard"),
                         description=_(u"Select the Ploneboards to get conversations from."),
                         required=True,
                         value_type=schema.Choice(
                             vocabulary="Products.PloneboardPortlet.vocabularies.PloneboardVocabularyFactory")
                         )

    mcp = schema.TextLine(title=_(u"Relative prefix"),
                                                description=_(u"Prefix for ploneboard_recent link, relative to site (portal) root, without / after."),
                                                required=False,
                                                default=u"")


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IPloneboardPortlet)

    title = u"Recent messages"
    count = 5
    mcp = u""

    def __init__(self, title=None, count=None, pboard=None, mcp=None):
        if title is not None:
            self.title_=title
        if count is not None:
            self.count=count
        if pboard is not None:
            self.pboard=pboard
        if mcp is not None:
            self.mcp = mcp
        

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return self.title_ # "PloneboardPortlet"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)

    @memoize
    def results(self):
        ct=getToolByName(self.context, "portal_catalog")
        normalize=getUtility(IIDNormalizer).normalize
        icons=getMultiAdapter((self.context, self.request),
                                name="plone").icons_visible()
        if icons:
            portal=getMultiAdapter((self.context, self.request),
                                    name="plone_portal_state").portal_url()+"/"
        brains=ct(
                object_provides="Products.Ploneboard.interfaces.IConversation",
                sort_on="modified",
                sort_order="reverse",
                sort_limit=self.data.count)[:self.data.count]


        def morph(brain, pboard):
            obj=brain.getObject()
            forum=obj.getForum()
            ploneboard = forum.getBoard()
            for item in pboard:
                if ploneboard.UID() == item:
                    return dict(
                            title = brain.Title,
                            description = brain.Description,
                            url = brain.getURL()+"/view",
                            icon = icons and portal+brain.getIcon or None,
                            forum_url = forum.absolute_url(),
                            forum_title = forum.title_or_id(),
                            review_state = normalize(brain.review_state),
                            portal_type = normalize(brain.portal_type),
                            date = brain.modified)

        list = []
        for brain in brains:
           conversation = morph(brain, self.pboard)
           if conversation is not None:
               list.append(conversation)
        return list

    @property
    def available(self):
        return len(self.results())>0

    def update(self):
        self.conversations=self.results()

    @property
    def title(self):
        return self.data.title
 
    @property
    def pboard(self):
        return self.data.pboard

    @property
    def mcp(self):
        return self.data.mcp

    @property
    def next_url(self):
        try:
            return getToolByName(self, 'portal_url').getPortalObject().absolute_url() +\
                self.data.mcp +\
                "/ploneboard_recent"
        except Exception, value:
            import pdb; pdb.set_trace()

    render = ViewPageTemplateFile('ploneboardportlet.pt')

class AddForm(base.AddForm):
    form_fields = Fields(IPloneboardPortlet)
    label = _(u"label_add_portlet",
                default=u"Add recent conversations in ploneboard portlet.")
    description = _(u"help_add_portlet",
            default=u"This portlet shows conversations with recent comments.")

    def create(self, data):
        return Assignment(title=data.get("title"), count=data.get("count"), pboard=data.get("pboard"), mcp=data.get("mcp"))


class EditForm(base.EditForm):
    form_fields = Fields(IPloneboardPortlet)
    label = _(u"label_add_portlet",
                default=u"Add recent conversations portlet.")
    description = _(u"help_add_portlet",
            default=u"This portlet shows conversations with recent comments.")

