Introduction
============

Provides a "Members" tab on selected content types.
The view a the list of members having a role on the content,
sorted by role.

Content types have just to implement IUserListingAvailable.

Add to the configure.zcml on your policy product::

  <include package="collective.local.userlisting" />
  <class class="my.package.content.MyContent.MyContent">
     <implements interface="collective.local.userlisting.interfaces.IUserListingAvailable" />
  </class>
