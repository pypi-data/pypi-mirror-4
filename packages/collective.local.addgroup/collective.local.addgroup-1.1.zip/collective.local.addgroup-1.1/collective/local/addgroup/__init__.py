from AccessControl import getSecurityManager
from persistent.list import PersistentList

from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.event import notify
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
from zope.schema.interfaces import IVocabularyFactory

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import normalizeString
from Products.Five import BrowserView

from plone.app.controlpanel.usergroups import GroupDetailsControlPanel
from plone.app.layout.viewlets.common import ViewletBase

from collective.local.addgroup.event import GroupRemoved


PMF = MessageFactory('plone')
_ = MessageFactory('addgroup')

ANNOTATION_KEY = 'collective.local.addgroup.groups'


def addGroup(groupid, context):
    annotations = IAnnotations(context)
    groups = annotations.setdefault(ANNOTATION_KEY, PersistentList())
    if groupid not in groups:
        groups.append(groupid)


def removeGroup(groupid, context):
    annotations = IAnnotations(context)
    groups = annotations.get(ANNOTATION_KEY, ())
    if groupid in groups:
        groups.remove(groupid)
        notify(GroupRemoved(context, groupid))


def getGroupIds(context):
    annotations = IAnnotations(context)
    groups = annotations.get(ANNOTATION_KEY, ())
    return tuple(groups)


class AddGroupInSharing(ViewletBase):

    def update(self):
        gtool = getToolByName(self.context, 'portal_groups')
        groups = getGroupIds(self.context)
        self.groups = []
        for gid in groups:
            g = gtool.getGroupById(gid)
            if g is not None:
                self.groups.append(g)

        self.groups.sort(key=lambda g: normalizeString(g.getProperty('title'),
                                                       context=self.context))
        sm = getSecurityManager()
        self.can_add_groups = sm.checkPermission(
                'Add Groups', self.context)
        self.can_manage_groups = sm.checkPermission(
                'Manage users', self.context)
        self.delete_confirmation_msg = translate(
                _(u"Are you sure you want to delete?"),
                context=self.request)

    def content(self):
        return u"""
<script type="text/javascript">
  jQuery(document).ready(function(){
    jQuery('#new-group-link').prepOverlay({
      subtype: 'ajax',
      filter: common_content_filter,
      formselector: 'form[name="groups"]',
      noform: function(el) {return jQuery.plonepopups.noformerrorshow(el, 'redirect');},
      redirect: function () {return location.href;}
    });
  });
</script>
<p><a href="%s" id="new-group-link">%s</a></p>""" % (
                '%s/@@add-new-group' % self.context.absolute_url(),
                translate(PMF(u"label_add_new_group", default=u"Add New Group"),
                    context=self.request),
                )


class RemoveGroupFromList(BrowserView):
    def __call__(self):
        form = self.request.form
        if 'groupname' in form:
            groupname = form['groupname']
            removeGroup(groupname, self.context)
        target_url = self.context.absolute_url() + "/@@sharing"
        self.request.response.redirect(target_url)


class AddGroupForm(GroupDetailsControlPanel):

#    index = ViewPageTemplateFile(
#        pkg_resources.resource_filename('plone.app.controlpanel',
#            'usergroups_groupdetails.pt'))

    def __call__(self):
#        groupname = self.request.form.get('groupname', None)
#        if groupname is None:
#            addname = normalizeString(safe_unicode(self.context.Title()))
#            self.request.form['groupname'] = addname
#            self.request.form['title'] = self.context.Title()
        result = super(AddGroupForm, self).__call__()
        submitted = self.request.form.get('form.submitted', False)
        if submitted and self.group and not self.groupname:
            target_url = self.context.absolute_url() + "/@@sharing"
            self.request.response.redirect(target_url)
            groupname = self.group.getId()
            addGroup(groupname, self.context)

            roles = self.request.form.get('localroles', [])
            if roles:
                self.context.manage_setLocalRoles(groupname, roles)
                self.context.reindexObjectSecurity()

        return result

    def roles(self):
        vocabulary = getUtility(IVocabularyFactory, 'LocalRoles')
        return vocabulary(self.context)
