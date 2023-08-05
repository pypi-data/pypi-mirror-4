from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from edw.userhistory.browser.userlisthistory import get_member_list
from AccessControl import getSecurityManager
from Products.CMFCore import permissions


class IUserHistory(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.

    # some_field = schema.TextLine(title=_(u"Some field"),
    #                              description=_(u"A field to use"),
    #                              required=True)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IUserHistory)

    # TODO: Set default values for the configurable parameters here

    # some_field = u""

    # TODO: Add keyword parameters for configurable parameters here
    # def __init__(self, some_field=u""):
    #    self.some_field = some_field

    def __init__(self):
        pass

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "User login history"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('userhistory.pt')

    @property
    def available(self):
        sm = getSecurityManager()
        return sm.checkPermission(permissions.ManagePortal, self.context)

    def getHistoryData(self):
        user_list = [x for x in get_member_list(self.context)]
        user_list.sort(key=lambda k: k['date'].replace(tzinfo=None),
                       reverse=True)
        return user_list[:10]


class AddForm(base.NullAddForm):
    """Portlet add form.
    """
    def create(self):
        return Assignment()
