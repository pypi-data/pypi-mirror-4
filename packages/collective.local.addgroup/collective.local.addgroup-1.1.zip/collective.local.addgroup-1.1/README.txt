Introduction
============

Allows to create a group and assign roles directly from the sharing tab for Plone 4.
Tested on Plone 4.1.

Content types have just to implement IAddNewGroup to have the functionnality.
Also provides a dexterity behaviour.

If you want to enable it for Folder, you only have to add to your buildout.cfg::

  [instance]
  zcml =
      ...
      collective.local.addgroup


If you don't want the functionality for Folder, but on your own content type,
add to the configure.zcml of your policy module::

  <include package="collective.local.addgroup" file="minimal.zcml" />
  <class class="my.package.content.MyContent.MyContent">
     <implements interface="collective.local.addgroup.interfaces.IAddNewGroup" />
  </class>

If you just want this for a dexterity content type, you just have to activate the behaviour.

The user need to LOCALLY have the "Add Groups" permission to add a new group and
"Manage users" to add and remove users from the listed groups.

Add group to local list
-----------------------

The site manager can add groups from sharing table to locally managed groups list.
So then the user with local permissions can manage the group himself.
We don't give this feature to local managers to avoid privilege escalation.