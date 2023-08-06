Introduction
============

An event registration system for Plone. Provides ``Registrant`` and ``RegisterableEvent`` content types (using old-style content type framework: Archetypes) and corresponding workflows and associated ``portal_properties`` property sheet.

.. Note::

    This version of EventRegistration (1.0.x) may be incompatible with previous versions, which replaced the default ATEvent. In this version, a separate RegisterableEvent type is provided. Also, the custom workflows that ship with with this version of EventRegistration are disabled by default.

Installation
------------

Use Buildout::

    $ virtualenv .
    $ bin/pip install zc.buildout 
    $ bin/buildout init
    
With this ``buildout.cfg``:: 

    [buildout]
    allow-hosts = *.python.org
    extends = http://dist.plone.org/release/4.2.2/versions.cfg
    versions = versions
    parts = plone

    [plone]
    recipe = plone.recipe.zope2instance
    user = admin:admin
    eggs = 
        Pillow
        Plone
        Products.EventRegistration

And::

    $ bin/buildout
    $ bin/plone fg

Setup
-----

This add-on uses Plone's ``categories`` feature to define event types. As such, before adding a RegisterableEvent you must at least add one other content item first e.g. a Page, and define at least one category in it.
