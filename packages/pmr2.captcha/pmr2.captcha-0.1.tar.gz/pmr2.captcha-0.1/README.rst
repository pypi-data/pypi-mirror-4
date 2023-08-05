Introduction
============

This package adds the support of captchas on spam-prone forms on a given
Plone instance.  Currently this package extends the user registration
form from the package plone.app.users with the support for captcha views
following the format found in `collective.captcha`_.  A compatible
package must be installed before the captcha will function.

.. _collective.captcha: http://pypi.python.org/pypi/collective.captcha

------------
Installation
------------

This package requires and is for Plone 4 or later.  Plone 3.x does not
depend on `plone.app.users`_ for the user registration form.  To add the
support for captchas on the form for those versions of Plone are done
using the ZMI using the TTW editor on the registration template and
script files.

.. _plone.app.users: http://pypi.python.org/pypi/plone.app.users

~~~~~~~~~~~~~~~~~~~~~~~~
Installing with buildout
~~~~~~~~~~~~~~~~~~~~~~~~

You can install pmr2.cpatcha using `buildout`_ by adding an entry for
this package in both eggs and zcml sections.

.. _buildout: http://pypi.python.org/pypi/zc.buildout

Example::

    [buildout]
    ...

    [instance]
    ...

    eggs =
        ...
        pmr2.captcha

    zcml =
        ...
        pmr2.captcha

Once the site is rebuilt, start the instance and install this product
using the Add-ons panel in Site Setup.
