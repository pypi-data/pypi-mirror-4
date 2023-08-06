from zope.component import getUtilitiesFor
from zope.event import notify
from zope.formlib import form
from zope.i18nmessageid import MessageFactory
from zope.i18n import translate

from Products.statusmessages.interfaces import IStatusMessage
from plone.app.users.browser.register import RegistrationForm
from plone.app.layout.viewlets.common import ViewletBase

from collective.local.adduser.interfaces import IAddUserSchemaExtender
from collective.local.adduser.event import UserLocallyAdded

PMF = MessageFactory('plone')


def getSchemaExtenders():
    return sorted(getUtilitiesFor(IAddUserSchemaExtender),
        key=lambda x: getattr(x[1], 'order', 999))


class AddUserInSharing(ViewletBase):

    def update(self):
        pass

    def render(self):
        return u"""
<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery('#new-user-link').prepOverlay({
            subtype: 'ajax',
            filter: common_content_filter});
    });
</script>
<p><a href="%s" id="new-user-link">%s</a></p>""" % (
                '%s/@@add-new-user' % self.context.absolute_url(),
                translate(PMF(u"heading_add_user_form", default=u"Add New User"),
                    context=self.request))


class AddUserForm(RegistrationForm):

    @property
    def form_fields(self):
        defaultFields = super(AddUserForm, self).form_fields
        if not defaultFields:
            return []

        allFields = defaultFields
        for name, extender in getSchemaExtenders():
            allFields = extender.add_fields(allFields)

        return allFields


    @form.action(PMF(u'label_register', default=u'Register'),
                             validator='validate_registration', name=u'register')
    def action_join(self, action, data):
        super(AddUserForm, self).handle_join_success(data)

        for name, extender in getSchemaExtenders():
            extender.handle_data(data, self.context, self.request)

        user_id = data['username']
        notify(UserLocallyAdded(self.context, user_id, data))

        IStatusMessage(self.request).addStatusMessage(
            PMF(u"User added."), type='info')
        self.request.response.redirect(
                self.context.absolute_url() + "/@@sharing")
