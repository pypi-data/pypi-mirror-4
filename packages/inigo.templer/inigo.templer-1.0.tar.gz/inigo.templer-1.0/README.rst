.. contents::

Introduction
============

This package contains templer templates used by Inigo Consulting as our
standard package structure.

Installation
=============

Method 1: Buildout
-------------------

Create a buildout using this configuration::

  [buildout]
  parts = scripts

  [scripts]
  recipe = zc.recipe.egg
  eggs = 
     templer.core
     inigo.templer

Method 2: Install into system python
------------------------------------

::

  easy_install inigo.templer


Usage
=====

Instantiating template
----------------------

::

  templer inigo_plone

This will create a folder with your development package.

Using localcommands
--------------------

Enter your development package, and you will find a bootstrap.py and
buildout.cfg in it. This is a pre-configured buildout which will help you in
setting up a development environment for your package. To use localcommand, you
will need the paster provided by this buildout. Follow these steps to build the
buildout::

  python bootstrap.py
  ./bin/buildout -vvvv

Once buildout is successful, you can use paster to add localcommand templates::

  ./bin/paster add <localcommand-template-name>

Templates
==========

inigo_plone
------------

This template contains our standardized package structure and several local
commands to aid in common tasks related to Plone add-on development for
our clients. 

The local commands are:

 * *content_type* - This adds a skeleton Dexterity Content Type similar to
   templer.dexterity, however with a different layout.

 * *behavior* - This adds a skeleton for Dexterity Content Type similar to
   templer.dexterity.

 * *basic_portlet* - This adds a skeleton for a configurable portlet.

 * *nonconfigurable_portlet* - This adds a skeleton for a nonconfigurable
   portlet. This skeleton can also add assignment profile to specific content
   types.

 * *schemaextender* - This adds a skeleton for an archetypes.schemaextender
   browserlayer aware extender.

 * *skin_layer* - This adds a single FileSystemDirectoryView skin layer into 
   the product

 * *upgrade_profile* - This adds a skeleton for a GenericSetup upgrade profile
   and handler for the product.

Todo/Wishlist:

  * custom indexer, vocabularyfactory, z3cform widget
