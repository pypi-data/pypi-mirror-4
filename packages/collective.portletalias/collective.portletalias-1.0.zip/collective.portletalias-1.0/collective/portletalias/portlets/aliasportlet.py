import logging
import cgi

from ZODB.POSException import ConflictError
from zope.interface import implements
from zope.interface import Interface
from zope.component import getMultiAdapter

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portletalias import portletaliasMessageFactory as _

from collective.portletalias import utils

from zope.i18nmessageid import MessageFactory
__ = MessageFactory("plone")


logger = logging.getLogger("portletalias")


class IAliasPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.

    path = schema.ASCIILine(title=_(u"Path"),
                                  description=_(u"Site root relative path where the other portlet is assigned. E.g. /front-page"),
                                  required=True)

    provider = schema.ASCIILine(title=_(u"Provider"),
                                  description=_(u"Portlet provider id. E.g. plone.leftcolumn or plone.rightcolumn"),
                                  required=True)

    assignmentId = schema.ASCIILine(title=_(u"Assignment name"),
                                  description=_(u"What's the portlet id of the assignment. Use @@portlet-info view to show out"),
                                  required=True)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IAliasPortlet)

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "%s %s" % (getattr(self, "assignmentId", None), " alias")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    def cookError(self, message):
        """
        Generate error HTML payload
        """
        return "<p class='error portlet-alias-error'>%s</p>" % cgi.escape(message)

    def cookPortletHTML(self):
        """
        Wicked witch's cauldron.

        Render the target portlet in the target context and grabs its HTML.
        """

        context = self.context.aq_inner

        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')

        portal = portal_state.portal()

        if not self.data.path:
            return self.cookError("No path set")

        path = self.data.path.strip("/")

        try:
            targetContext = portal.unrestrictedTraverse(path)
        except KeyError:
            return self.cookError("Unknown content item path: %s" % path)

        provider = self.data.provider.strip()

        try:
            manager = utils.get_portlet_manager(provider)
        except ConflictError:
            raise
        except Exception, e:
            logger.exception(e)
            return self.cookError("Unknown portlet manager: %s" % provider)

        assignmentId = self.data.assignmentId.strip()

        try:
            html = utils.render_portlet(targetContext, self.request, None, manager, assignmentId)
        except ConflictError:
            raise
        except Exception, e:
            logger.exception(e)
            return self.cookError("Got exception when rendering the aliased portlet %s: %s" % (assignmentId, e))

        return html

    def render(self):
        return self.cookPortletHTML()


# NOTE: If this portlet does not have any configurable parameters, you can
# inherit from NullAddForm and remove the form_fields variable.

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IAliasPortlet)

    def create(self, data):
        return Assignment(**data)


# NOTE: IF this portlet does not have any configurable parameters, you can
# remove this class definition and delete the editview attribute from the
# <plone:portlet /> registration in configure.zcml

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IAliasPortlet)
