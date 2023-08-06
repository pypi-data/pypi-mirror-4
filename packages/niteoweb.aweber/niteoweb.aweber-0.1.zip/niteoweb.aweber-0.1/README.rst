================================
AWeber.com integration for Plone
================================

A Plone add-on that integrates `AWeber <http://www.aweber.com>`_ email
autoresponder system with `Plone <http://plone.org>`_.

* `Source code @ GitHub <https://github.com/niteoweb/niteoweb.aweber>`_
* `Continuous Integration @ Travis-CI <http://travis-ci.org/niteoweb/niteoweb.aweber>`_


Installation
============

Within virtualenv from PyPI
---------------------------

.. sourcecode:: bash

    $ virtualenv --no-site-packages myproject
    $ cd myproject
    $ bin/pip install niteoweb.aweber


With buildout from PyPI
-----------------------

Add ``niteoweb.aweber`` to ``buildout.cfg`` under ``eggs`` section and then
run ``bin/buildout``.


Installation with mr.developer
------------------------------

Modify ``buildout.cfg`` to install this package with ``mr.developer``::

    [buildout]
    extensions = mr.developer
    auto-checkout = niteoweb.aweber

    [sources]
    niteoweb.aweber = git git://github.com/niteoweb/niteoweb.aweber.git


Configuration
=============

AWeber
------

Get a free account at `AWeber Labs <https://labs.aweber.com>`_ to create an
application. You are going to need an ``App ID``.

You will also need an `AWeber`_ account.


Plone
-----

#. Go to ``Site Setup`` -> ``Configure Aweber`` control panel form.
#. Enter ``App ID`` into the correct field.
#. Click ``Get auth code``.
#. A message will appear on top of the page. Visit the link in the message.
#. Fill out the form on the page with your `AWeber`_ account.
#. Click ``Allow Access``.
#. Copy authorization code to ``Authorization Code`` field in ``Plone`` control
   panel form.
#. Click ``Parse auth code and update lists`` to get fill in four necessary
   fields and to update `list names` field choices.
#. Choose desired ``List name``.
#. Click ``Save`` to save ``App ID`` and ``List Name`` choice.


Usage
=====

Subscribe a new user from Python code
-------------------------------------

After successful configuration in `Plone` control panel for `AWeber`
you can use the following snippet to subscribe a new user.

.. sourcecode:: python

    >>> from niteoweb.aweber.aweberapi import subscribe_to_aweber_mailinglist
    >>> email = "some.one@xyz.xyz"
    >>> fullname = "Some One"
    >>> subscribe_to_aweber_mailinglist(email, fullname)


Manually subscribe a new user
-----------------------------

After successful configuration in `Plone` control panel for `AWeber` you can
manually subscribe a new user to your mailing list.

#. Go to ``Site Setup`` -> ``Configure Aweber`` control panel form.
#. Make sure that value of ``List Name`` field is selected.
#. Fill out the ``Subscriber's full name`` and ``Subscriber's email``.
#. Click ``Subscribe new user``.
#. On success, subscriber's fields will be emptied.


Update lists
------------

After successful configuration in `Plone` control panel for `AWeber` you can
also update mailing lists only, without parsing of authorization code.

#. Go to ``Site Setup`` -> ``Configure Aweber`` control panel form.
#. Click ``Update lists only``.

