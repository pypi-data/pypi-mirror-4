from zope.formlib import form
from zope.i18nmessageid import MessageFactory
from zope.interface import implements, Interface
from zope import schema

from plone.app.controlpanel.widgets import MultiCheckBoxVocabularyWidget

from collective.local.adduser.interfaces import IAddUserSchemaExtender

_ = MessageFactory('adduser')


class IAddUserSchema(Interface):

    roles = schema.List(
        title=_(u'label_assign_permissions',
                default=u'Assign the following permissions:'),
        description=u'',
        required=False,
        default=['Reader'],
        value_type=schema.Choice(vocabulary='LocalRoles'))


class AddUserSchema(object):
    implements(IAddUserSchemaExtender)
    order = 10

    def add_fields(self, fields):
        fields += form.Fields(IAddUserSchema)
        fields['roles'].custom_widget = MultiCheckBoxVocabularyWidget
        return fields

    def handle_data(self, data, context, request):
        user_id = data['username']
        roles = data.get('roles', [])
        if roles:
            context.manage_addLocalRoles(user_id, roles)
            context.reindexObjectSecurity()
