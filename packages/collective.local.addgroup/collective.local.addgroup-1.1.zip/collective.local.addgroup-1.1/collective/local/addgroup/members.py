from AccessControl import Unauthorized
from Acquisition import aq_inner
from zope.annotation.interfaces import IAnnotations
from zope.component import getAdapter

from Products.CMFCore.utils import getToolByName
from plone.app.controlpanel.security import ISecuritySchema
from plone.app.controlpanel.usergroups import GroupMembershipControlPanel

from collective.local.addgroup import getGroupIds


class ManageMembers(GroupMembershipControlPanel):

    @property
    def email_as_username(self):
        portal = getToolByName(aq_inner(self.context), 'portal_url').getPortalObject()
        return getAdapter(portal, ISecuritySchema).get_use_email_as_login()

    def update(self):
        groupname = self.request.form['groupname']
        if groupname is None:
            raise Unauthorized

        allowed_groups = getGroupIds(self.context)
        if groupname not in allowed_groups:
            raise Unauthorized

        super(ManageMembers, self).update()
