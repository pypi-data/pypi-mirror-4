from collections import OrderedDict

import zope.schema

from zope.component import getUtility, getMultiAdapter

from Products.Five import BrowserView

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping


def dump_schemed_data(obj):
    """
    Prints out object variables as defined by its zope.schema Interface.
    """
    out = OrderedDict()

    # Check all interfaces provided by the object
    ifaces = obj.__provides__.__iro__

    # Check fields from all interfaces
    for iface in ifaces:
        fields = zope.schema.getFieldsInOrder(iface)
        for name, field in fields:
            # ('header', <zope.schema._bootstrapfields.TextLine object at 0x1149dd690>)
            out[name] = getattr(obj, name, None)

    return out


class PortletData(BrowserView):
    """
    Show info about the portlet assigned in the location.
    """

    def getPortletData(self):
        """
        """

        content = self.context.aq_inner

        managers = []

        for manager_name in ["plone.leftcolumn", "plone.rightcolumn"]:

            manager = getUtility(IPortletManager, name=manager_name, context=content)

            mapping = getMultiAdapter((content, manager), IPortletAssignmentMapping)

            items = []
            # id is portlet assignment id
            # and automatically generated
            for id, assignment in mapping.items():
                #print "Found portlet assignment:" + id + " " + str(assignment)
                items.append({
                    "name": id,
                    "data": dump_schemed_data(assignment)
                })

            managers.append({
                "name": manager_name,
                "items": items
            })

        return managers

