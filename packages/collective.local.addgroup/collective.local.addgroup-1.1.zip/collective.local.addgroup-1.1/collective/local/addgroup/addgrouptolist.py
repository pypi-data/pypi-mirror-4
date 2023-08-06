from AccessControl import getSecurityManager

from zope.i18nmessageid import MessageFactory
from zope.i18n import translate

from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

from . import addGroup

_ = MessageFactory('addgroup')


class AddGroupToListJS(ViewletBase):

    def render(self):
        return u"""
<script type="text/javascript">
  jQuery(document).ready(function(){
    if (jQuery('#new-group-link')) {
        jQuery('#user-group-sharing-settings input[name=entries.type:records][value=group]').each(function() {
            value = jQuery(this).siblings('input[name=entries.id:records]').attr('value');
            if (value != 'AuthenticatedUsers') {
                if (jQuery("#groups-list a[href$='groupname="+value+"']").length == 0) {
                    html = '<a href="@@add-group-to-list?groupname='+value+'"><img src="'+portal_url+'/++resource++addgroup.gif" title="%s" /></a>'
                    img = jQuery(this).siblings('img');
                    jQuery(html).insertAfter(img);
                    img.remove();
                }
            }
        });
    }
  });
</script>
""" % translate(_(u"Add to managed groups"), context=self.request)


class AddGroupToList(BrowserView):
    def __call__(self):
        form = self.request.form
        if 'groupname' in form:
            groupname = form['groupname']
            gtool = getToolByName(self.context, 'portal_groups')
            g = gtool.getGroupById(groupname)
            if g is not None:
                addGroup(groupname, self.context)

        target_url = self.context.absolute_url() + "/@@sharing"
        self.request.response.redirect(target_url)
