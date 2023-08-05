""" User history
"""
from itertools import chain
from persistent.list import PersistentList
from zope.component import getUtilitiesFor, getMultiAdapter
from zope.annotation.interfaces import IAnnotations
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Acquisition import aq_inner, aq_parent, aq_base
from AccessControl import Unauthorized
from zExceptions import Forbidden
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions

class UserHistoryView(BrowserView):
    """ User history view
    """
    template = ViewPageTemplateFile('templates/userhistory.pt')

    def __call__(self, **kw):
        if self.request:
            kw.update(self.request.form)
        return self.template(username=kw.get('userid', ''))

    def getMemberHistory(self, memberid):
        """ Get member history
        """
        membership_tool = getToolByName(self.context, 'portal_membership')
        member = membership_tool.getMemberById(memberid)
        member_history = IAnnotations(member).get('login_history', None)
        if not member_history:
            member_history = [{
                'date': member.getProperty('login_time'),
                'ip': ' - '
            }]
        return member_history
