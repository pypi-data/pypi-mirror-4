from zope.interface import implements
from zope import component
from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.registry.interfaces import IRegistry
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from collective.portlet.socialnetworks import SocialNetworksMessageFactory as _
from Products.CMFPlone import PloneMessageFactory
_p = PloneMessageFactory


class ISocialNetworks(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    header = schema.TextLine(
        title=_p(u"Portlet header"),
        description=_p(u"Title of the rendered portlet"),
                             required=True)

    omit_border = schema.Bool(
        title=_p(u"Omit portlet border"),
        description=_p(u"Tick this box if you want to render the text above "
                       "without the standard header, border or footer."),
        required=True,
        default=False)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ISocialNetworks)

    omit_border = False

    def __init__(self, header=u"", omit_border=False):
        self.header = header
        self.omit_border = omit_border

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        if self.header:
            return self.header
        return _(u"Social Networks")


class Renderer(base.Renderer):
    """Portlet renderer.
    """

    render = ViewPageTemplateFile('socialnetworks.pt')

    def site_url(self):
        if not hasattr(self, '_site_url'):
            self._site_url = self.context.portal_url()
        return self._site_url

    def get_socialnetworks(self):
        networks = []
        registry = component.getUtility(IRegistry)
        record = registry.get('collective.portlet.socialnetworks', [])
        unknown = 0

        for row in record:

            if row.startswith('http'):
                #unknow network
                networks.append({'id': 'unknown%s' % unknown})
                unknown += 1
            else:
                splited = row.split('|')
                if len(splited) == 2:
                    networks.append({'id': splited[0],
                                     'url': splited[1]})

        return networks


class AddForm(base.AddForm):
    """Portlet add form.
    """
    form_fields = form.Fields(ISocialNetworks)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.
    """
    form_fields = form.Fields(ISocialNetworks)
