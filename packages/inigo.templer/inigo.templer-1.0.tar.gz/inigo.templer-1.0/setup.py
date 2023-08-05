from setuptools import setup, find_packages
import os

version = '1.0'

long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='inigo.templer',
      version=version,
      description="Convenience templer templates for Inigo stuff",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Framework :: Plone",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Framework :: Buildout",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Code Generators",
        ],
      keywords='',
      author='Inigo Consulting',
      author_email='team@inigo-tech.com',
      url='http://github.com/inigoconsulting/inigo.templer',
      license='MIT',
      packages=find_packages(),
      namespace_packages=['inigo'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'templer.core',
          'templer.zope',
          'templer.localcommands',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.paster_create_template]
      inigo_plone = inigo.templer:InigoPlone

      [templer.templer_sub_template]
      content_type = inigo.templer.localcommands.dexterity:DexterityContent
      behavior = inigo.templer.localcommands.dexterity:DexterityBehavior
      upgrade_profile = inigo.templer.localcommands.genericsetup:UpgradeProfile
      skin_layer = inigo.templer.localcommands.genericsetup:SkinLayer
      schemaextender = inigo.templer.localcommands.archetypes:SchemaExtender
      basic_portlet = inigo.templer.localcommands.portlet:BasicPortlet
      nonconfigurable_portlet = inigo.templer.localcommands.portlet:NonConfigurablePortlet
      """,
      )
