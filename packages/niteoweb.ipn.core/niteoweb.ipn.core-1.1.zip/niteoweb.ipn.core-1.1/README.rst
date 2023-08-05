=================
niteoweb.ipn.core
=================

A Plone add-on package that acts as a base for supporting different Instant
Payment Notification providers (such as PayPal, JVZoo, Click2Sell, etc.)

* `Source code @ GitHub <https://github.com/niteoweb/niteoweb.ipn.core>`_
* `Releases @ PyPI <http://pypi.python.org/pypi/niteoweb.ipn.core>`_
* `Continuous Integration @ Travis-CI <http://travis-ci.org/niteoweb/niteoweb.ipn.core>`_

Subpackages
===========

You probably do not want to use this package on its own, but rather use one
of its sub-packages:

 * `niteoweb.ipn.jvzoo <http://pypi.python.org/pypi/niteoweb.ipn.jvzoo>`_
 * `niteoweb.ipn.c2s (WIP) <http://pypi.python.org/pypi/niteoweb.ipn.c2s>`_

How it works
============

This package acts as a base layer for ``niteoweb.ipn.*`` packages. It provides
the code that these sub-packages would have to otherwise duplicate:

 * Creating a new member.
 * Updating an existing member.
 * Disabling an existing member.
 * Firing off events that your project code can catch and perform custom tasks
   on.

The following information is stored as member properties for later use:

    ``product_id``
        IPN provider's `Product ID` of the purchased item.

    ``affiliate``
        Affiliate who referred the buyer.

    ``valid_to``
        Date until the member's subscription is valid.

    ``history``
        History of actions taken on the member. Useful for analyses later on.


Assumptions
===========

* Emails are used as usernames.
* "Disabling" a member means to revoke her Member role and put her in the
  `Disabled` group, while removing her from all other groups.
* "Enabling" a member means to create a new member (if she doesn't exist yet),
  grant her the Member role (if she doesn't have it yet) and add her to the
  Product Group.
* "Product Group" is a group that contains members that have purchased the same
  product. Product group IDs are equal to Product IDs -- this is how they are
  linked together.
* When niteoweb.ipn.core creates a new member object, the registration email is
  **not** sent. Your third-party code should take care of this (for example by
  subscribing to the IPrincipalCreatedEvent emitted by PAS).
* Whenever a member is enabled, a 'valid_to' property is set on the member
  object to represent until which day should this member be allowed to use the
  site. You then need to setup a cronjob that calls ``@@validity`` view every
  day to disable those members whose validity period has elapsed. In the
  plone.app.registry control panel you can set a secret that needs to be passed
  as a request parameter to the ``@@validity`` view.

Installation
============

You probably do not want to install `niteoweb.ipn.core` directly, but rather
use one of ``niteoweb.ipn.*`` sub-packages.

