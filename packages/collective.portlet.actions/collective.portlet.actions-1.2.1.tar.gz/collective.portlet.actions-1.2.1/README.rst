==========================
collective.portlet.actions
==========================

By `Alter Way Solutions <http://www.alterway.fr>`_.

.. image:: https://travis-ci.org/collective/collective.portlet.actions.png

Show in a portlet of a Plone site the links and (maybe translated) titles of the
actions of a selected category.

Compared with the static text portlet, action URLs are computed and links may be
protected by a TALES condition and permissions, such the same portlet may
provide different links to various users or in various contexts.

Requirements
============

collective.portlet.actions requires Plone 3.x or greater. It has been tested with Plone 3.2 and Plone 4.2. It should work with all versions in between and may or may not work with future Plone versions.

Install
=======

Usual install
-------------

collective.portlet.actions is a Python egg with a ZCML slug, such you just need
to add these lines in your zc.buildout config file: ::

  [instance]
  recipe = plone.recipe.zope2instance
  ...
  eggs =
    ...
    collective.portlet.actions
    ...
  zcml =
    ...
    collective.portlet.actions

As of Plone 3.2, you don't need to add ``collective.portlet.actions`` to the
``zcml`` option.

Then re-run your buildout config.

See ``docs/INSTALL.txt`` for other installation methods.

Development
-----------

Please read the comments on top of ``buildout.cfg`` that comes with the
subversion checkout.

Add a portlet
=============

Of course, if an existing actions category doesn't fit what you need, you may
add your own actions category in the ``portal_actions`` tool and add actions in
it. Action titles may be translated if you provide an i18n domain.

You may add an icon directly in the action definition, as a TAL expression that
provides the icon object. e.g. ``portal/book_icon.gif``.

You may associate an icon to each action using the ``portal_actionicons`` tool
too if you prefer the old way.

When done, add an 'Actions portlet' anywhere you want. Give a title and select
the appropriate actions category.

If you choose to show action icons, you may change the default icon for actions
that have no icon from their own or through the ``portal_actionicons``
tool. The value for the default icon is evaluated from the context when
publishing the portlet.

You're done.

License
=======

This component is protected by the terms of the GPL v2 license. Please read
the ``docs/LICENSE.\*`` files.

Further documentation
=====================

Please read the ``docs`` directory, as well as other specific ``README.txt`` in
other places of this component.

Home page
=========

You may find further informations, a tracker and support resources from the home
page at plone.org.

* At plone.org: http://plone.org/products/collective.portlet.actions

* At Pypi: http://pypi.python.org/pypi/collective.portlet.actions

Code repository
===============

https://github.com/collective/collective.portlet.actions

Credits
=======

Development
-----------

* Main developper: `Gilles Lenfant <mailto:gilles DOT lenfant AT alterway DOT
  fr>`_

* Sponsor: `EDF <http://www.edf.fr>`_

Translations
------------

See ``collective/portlet/actions/locales/README.txt`` if you need to translate
this component into another language.

* French (fr): `Gilles Lenfant <mailto:gilles DOT lenfant AT alterway DOT fr>`_
* Italian (it): `Davide Moro <mailto:davide DOT moro AT redomino DOT com>`_
