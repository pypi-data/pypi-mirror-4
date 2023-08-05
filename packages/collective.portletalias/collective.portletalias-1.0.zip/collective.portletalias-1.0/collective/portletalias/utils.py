from zope.component import getUtility, getMultiAdapter, queryMultiAdapter
from plone.portlets.interfaces import IPortletRetriever, IPortletManager, IPortletRenderer
from plone.portlets.interfaces import IPortletManagerRenderer


from Products.Five import BrowserView


class FakeView(BrowserView):
    """
    Portlet manager code goes down well with cyanide.
    """


def get_portlet_manager(column):
    """ Return one of default Plone portlet managers.

    @param column: "plone.leftcolumn" or "plone.rightcolumn"

    @return: plone.portlets.interfaces.IPortletManagerRenderer instance
    """
    manager = getUtility(IPortletManager, name=column)
    return manager


def render_portlet(context, request, view, manager, assignmentId):
    """ Render a portlet defined in external location.

    .. note ::

        Portlets can be idenfied by id (not user visible)
        or interface (portlet class). This method supports look up
        by interface and will return the first matching portlet with this interface.

    @param context: Content item reference where portlet appear

    @param manager: IPortletManager instance through get_portlet_manager()

    @param view: Current view or None if not available

    @param interface: Marker interface class we use to identify the portlet. E.g. IFacebookPortlet

    @return: Rendered portlet HTML as a string, or empty string if portlet not found
    """

    if not view:
        # manager(context, request, view) does not accept None as multi-adapter lookup parameter
        view = FakeView(context, request)

    retriever = getMultiAdapter((context, manager), IPortletRetriever)

    portlets = retriever.getPortlets()

    assignment = None

    if len(portlets) == 0:
        raise RuntimeError("No portlets available for manager %s in the context %s" % (manager.__name__, context))

    for portlet in portlets:

        # portlet is {'category': 'context', 'assignment': <FacebookLikeBoxAssignment at facebook-like-box>, 'name': u'facebook-like-box', 'key': '/isleofback/sisalto/huvit-ja-harrasteet
        # Identify portlet by interface provided by assignment
        print portlet
        if portlet["name"] == assignmentId:
            assignment = portlet["assignment"]
            break

    if assignment is None:
        # Did not find a portlet
        raise RuntimeError("No portlet found with name: %s" % assignmentId)

    # Note: Below is tested only with column portlets

    # PortletManager provides convenience callable
    # which gives you the renderer. The view is mandatory.
    managerRenderer = manager(context, request, view)

    # PortletManagerRenderer convenience function
    renderer = managerRenderer._dataToPortlet(portlet["assignment"].data)

    if renderer is None:
        raise RuntimeError("Failed to get portlet renderer for %s in the context %s" % (assignment, context))

    renderer.update()
    # Does not check visibility here... force render always
    html = renderer.render()

    return html
