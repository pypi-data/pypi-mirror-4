=====================
ztfy.security package
=====================

.. contents::

What is ztfy.security ?
=======================

ztfy.security is a thin wrapper around zope.security and zope.securitypolicy packages.

It provides an adapter to ISecurityManager interfaces, which allows you to get and set roles and
permissions applied to a given principal on a given adapted context.

This adapter also allows you to fire events when a role is granted or revoked to a given principal ; this
functionality can be useful, for example, when you want to forbid removal of a 'contributor' role to a principal
when he already owns a set of contents.

Finally, ztfy.security provides a small set of schema fields, which can be used when you want to define a
field as a principal id or as a list of principals ids.


How to use ztfy.security ?
==========================

ztfy.security package usage is described via doctests in ztfy/security/doctests/README.txt
