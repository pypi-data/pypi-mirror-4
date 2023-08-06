from zope.interface import implements, Interface
from zope.formlib import form
from zope import schema

from plone.app.controlpanel.widgets import MultiCheckBoxVocabularyWidget
from Products.CMFCore.utils import getToolByName

from collective.local.adduser.interfaces import IAddUserSchemaExtender
from collective.local.addgroup import _


class IAddUserSchema(Interface):

    groups = schema.List(
        title=_(u'Assign the following groups:'),
        description=u'',
        required=False,
        value_type=schema.Choice(vocabulary='LocalGroups'))


class AddUserSchema(object):
    implements(IAddUserSchemaExtender)
    order = 20

    def add_fields(self, fields):
        fields += form.Fields(IAddUserSchema)
        fields['groups'].custom_widget = MultiCheckBoxVocabularyWidget
        return fields

    def handle_data(self, data, context, request):
        pgroups = getToolByName(context, "portal_groups")
        userid = data['username']
        groupids = data['groups']
        for groupid in groupids:
            # you need ManageGroups to use this.
            pgroups.addPrincipalToGroup(userid, groupid)
