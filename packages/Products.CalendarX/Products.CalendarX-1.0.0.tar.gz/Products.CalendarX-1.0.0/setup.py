from setuptools import setup, find_packages
import os


def _textFromPath(*names):
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, *names)
    return open(path, 'r').read().strip()

version = '1.0.0'
long_description = '\n\n'.join(
    (_textFromPath('README.rst'),
     _textFromPath('docs', 'HISTORY.txt')
     ))

setup(name='Products.CalendarX',
      version=version,
      description=("CalendarX is a customizable, open source metacalendar "
                   "application written for the Plone content management "
                   "system on top of Zope and Python."),
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Framework :: Plone",
          "Framework :: Zope2",
          "Programming Language :: Python",
          "Operating System :: OS Independent",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Office/Business :: Scheduling",
          "Natural Language :: Catalan",
          "Natural Language :: Czech",
          "Natural Language :: Danish",
          "Natural Language :: English",
          "Natural Language :: German",
          "Natural Language :: French",
          "Natural Language :: Italian",
          "Natural Language :: Japanese",
          "Natural Language :: Dutch",
          "Natural Language :: Portuguese (Brazilian)",
          "Natural Language :: Swedish",
        ],
      keywords='plone calendar',
      author='Lupa Zurven',
      author_email='lupa at zurven dot com',
      maintainer='Alex Clark',
      maintainer_email='aclark@aclark.net',
      url='https://github.com/collective/Products.CalendarX',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.AdvancedQuery',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [distutils.setup_keywords]
      paster_plugins = setuptools.dist:assert_string_list

      [egg_info.writers]
      paster_plugins.txt = setuptools.command.egg_info:write_arg

      [z3c.autoinclude.plugin]
      target = plone
      """,
      paster_plugins=["ZopeSkel"],
      )
