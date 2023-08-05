Introduction
============

Dexterity is a content-type development tool for Plone. It supports
Through-The-Web and filesystem development of new content types for Plone.
Templer is a Python source package skeleton creator.

templer.dexterity provides a mechanism to quickly create Dexterity add-on
skeletons. It also makes it easy to add new content types to an existing
skeleton. New content types built with this tool are easy to integrate
with types you may have developed with Dexterity's TTW schema editor.

This is a development tool. You should be familiar with Plone and buildout to
use it. You should have already installed Dexterity in your Plone development
instance and be ready to start learning to use it.

Installation
============

Add these lines into buildout.cfg::

  [buildout]
  parts =
     templer

  [templer]
  recipe = zc.recipe.egg
  eggs =
     PasteScript
     templer.core
     templer.zope
     templer.plone
     templer.dexterity
     ${instance:eggs}

Where instance is the part name of a Zope instance or ZODB client.

Run buildout.

Usage
======

Creating a dexterity content package, typically done in your buildout's src
directory::

  ../bin/templer dexterity

Adding a content-type skeleton to an existing package::

  cd yourbuildout/src/your-product/src
  ../../../bin/paster add content_type

Adding a behavior skeleton::

  cd yourbuildout/src/your-product/src
  ../../../bin/paster add behavior

You **must** add your new project to your buildout and run buildout before
adding content types or behaviors to your new package.

Notes
=====

Egg Directories
---------------

In order to support local commands, templer will create Paste, PasteDeploy and
PasteScript eggs inside your product. These are only needed for development.
You can and should remove them from your add-on distribution.

Also remove::

  setup_requires=["PasteScript"],
  paster_plugins=["templer.localcommands"],

from the packages setup.py.

Errors
------

If you hit and error like this::

  pkg_resources.DistributionNotFound: plone.app.relationfield:
  Not Found for: my.product (did you run python setup.py develop?)

when attempting to run `paster add`, then you need to ensure that
Paster knows about all the relevant eggs from your buildout.

Add `${instance:eggs}` to your `paster` section in your buildout, thusly::

  [templer]
  recipe = zc.recipe.egg
  eggs =
     ...
     ${instance:eggs}
     entry-points = paster=paste.script.command:run

where `instance` is the name of your ``plone.recipe.zope2instance`` section.
Re-run the buildout and the issue should be resolved.
