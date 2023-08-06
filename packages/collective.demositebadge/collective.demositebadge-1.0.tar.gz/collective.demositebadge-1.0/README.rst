Introduction
============

This Plone add-on displays configurable badge that you can use on your
development, demo and preview instances. It'll help you and your customers not
to confuse your development Plone instances with production sites.


Compatibility
-------------

This add-on was tested for Plone 3 and Plone 4.


Installation
------------

* add the following to your buildout configuration file::

    [buildout]
    ...
    eggs = collective.demositebadge
    ...

* rerun buildout and restart your Zope instance.
* then install the ``collective.demositebadge`` package from within the
  ``portal_quickinstaller`` tool


Usage
-----

After add-on is install you'll get ``Demo site badge`` Plone Control Panel.
There simply enable badge and, if you need, customize default badge text.

That is it.

Usually you'll have custom theme in your Plone Site, thus you may need to add a
bit of css magic in order to make demo badge look better under your own
circumstances.


Plone 3 Notes
-------------

To install and use this add-on on Plone 3 you need to do some extra steps:

* use ``plone.app.registry`` fixed versions set; for this add the following to
  your buildout configuration file::

    [buildout]
    ...
    extends =
         http://good-py.appspot.com/release/plone.app.registry/1.0b1
    ...
    
    [versions]
    plone.z3cform = 0.6.0
    zope.i18n = 3.6.0
    
    [instance]
    ...
    zcml =
        ...
        plone.app.registry

* and before Activating demo badge addon, you have to make sure 'Configuration registry' is activated (installed) in your Add-ons Control Panel


Live Examples
=============

* http://theme.choosehelp.devel.martinschoel.com/www


Credits
=======


Companies
---------

|martinschoel|_

* `Martin Schoel Web Productions <http://www.martinschoel.com/>`_
* `Contact us <mailto:python@martinschoel.com>`_


Authors
-------

* Vitaliy Podoba <vitaliy@martinschoel.com>
* Victor Imenkov


Contributors
------------


.. |martinschoel| image:: http://cache.martinschoel.com/img/logos/MS-Logo-white-200x100.png
.. _martinschoel: http://www.martinschoel.com/
