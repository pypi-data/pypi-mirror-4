""" edw.userhistory init
"""
from zope.i18nmessageid import MessageFactory

UserHistoryMessageFactory = MessageFactory('edw.userhistory')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
