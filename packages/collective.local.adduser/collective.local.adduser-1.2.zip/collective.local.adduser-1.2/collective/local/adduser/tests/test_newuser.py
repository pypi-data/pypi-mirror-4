from plone.testing.z2 import Browser
from plone.app.testing import login

from collective.local.adduser.tests.base import BaseTestCase


class CreateNewUserTests(BaseTestCase):

    # disabled for now
    def xtest_create_new_user(self):
        app = self.layer['app']
        portal = self.layer['portal']
        workspace = self.create_workspace()
        import transaction
        transaction.commit()
        browser = Browser(app)
        browser.handleErrors = False
        # login
        portalURL = portal.absolute_url()
        browser.open(portalURL + '/login_form')
        browser.getControl(name='__ac_name').value = 'incharge'
        browser.getControl(name='__ac_password').value = 'secret'
        browser.getControl(name='submit').click()

        browser.getLink(workspace.Title()).click()
#        browser.open(workspace.absolute_url())
#        open('/tmp/testbrowser.html', 'w').write(browser.contents)

        browser.getLink('Sharing').click()
#        browser.getLink('Add New User').click()
        # TODO finish the tests
