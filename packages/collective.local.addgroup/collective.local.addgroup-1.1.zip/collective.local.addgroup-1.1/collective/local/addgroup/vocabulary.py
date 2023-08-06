from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import normalizeString

from collective.local.addgroup import getGroupIds


class LocalGroupsVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        pgroups = getToolByName(context, 'portal_groups')
        terms = []

        for groupid in getGroupIds(context):
            group = pgroups.getGroupById(groupid)
            if group is not None:
                terms.append(SimpleTerm(groupid, unicode(groupid),
                    group.getProperty('title', groupid) or groupid))

        terms.sort(key=lambda x: normalizeString(x.title))
        return SimpleVocabulary(terms)
