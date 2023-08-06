from zope.interface import implements
from plone.app.workflow.interfaces import ISharingPageRole

from Products.CMFPlone import PloneMessageFactory as _


"""
Adding a Site Administrator role to the sharing tab
"""


class SiteAdministratorRole(object):
    implements(ISharingPageRole)

    title = _(u"title_can_manage", default=u"Can manage")
    required_permission = "Sharing page: Delegate Site Administrator role"
