from zope.component import getUtilitiesFor
from zope.i18n import translate
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import normalizeString
from plone.app.workflow.interfaces import ISharingPageRole


class LocalRolesVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        portal_membership = getToolByName(context, 'portal_membership')

        terms = []

        for name, utility in getUtilitiesFor(ISharingPageRole):
            permission = utility.required_permission
            if permission is None or portal_membership.checkPermission(permission, context):
                terms.append(SimpleTerm(name, name, utility.title))

        terms.sort(key=lambda x: normalizeString(
            translate(x.title, context=context.REQUEST)))
        return SimpleVocabulary(terms)


