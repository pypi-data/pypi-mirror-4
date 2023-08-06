Introduction
============

Allows to create a user and assign roles directly from the sharing tab for Plone >= 4.1.
This can work with Plone 4.0.9 with plone.app.users > 1.0.6, < 1.1.x.

Content types have just to implement IAddNewUser to have the functionnality.

If you want to enable it for Folder, you only have to add to your buildout.cfg::

  [instance]
  eggs =
      ...
      collective.local.adduser
  zcml =
      ...
      collective.local.adduser

If you don't want the functionnality for Folder, but on your own content type,
add to the configure.zcml of your policy module::

  <include package="collective.local.adduser" file="minimal.zcml" />
  <class class="my.package.content.MyContent.MyContent">
     <implements interface="collective.local.adduser.interfaces.IAddNewUser" />
  </class>

If you don't want the roles field, you can include minimal_wo_roles.zcml instead of minimal.zcml.