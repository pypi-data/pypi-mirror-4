Introduction
============

collective.groupmail is a way to send an email to all users in the group. It
overrides the Member search (in the Users folder) to also return groups, and
adds the group details view so that it contains the same type of contact form
that the user overview does. This enables you to send an email to the whole
group.

If the group has a configured email-address, that adress will be used. If
not, each member will have their email address looked up, and the email sent
to that member. 

Separate emails are sent, so that the reply will go only to the sender and
not to everyone. If you want it to go to everyone, you need to set up a
mailing list, and add the address of that list to the group properties.


Installation
============

Add collective.groupmail to the eggs= list in your buildout. Re-run buildout,
restart the server. All sites in the server will get this functionality. In
the future it is planned to add a layer so that you need to install the
product, but because of lack of time this will wait to a future release.


License
=======

GPL, see docs/LICENSE.GPL
