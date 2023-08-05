from setuptools import setup, find_packages
import sys, os

version = '0.1'

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'docutils',        # only needed for wiki
    'feedparser',      # only needed for rssviewer
    'pyramid-beaker',  # session management
    'pyramid-layout',  # handle layouts
    'Mako',            # we have mako templates for forms
    'FormEncode',      # we use parts of formencode
    'WTForms',         # we use WTForms for forms
    'python-dateutil', # to use dateutil extension in WTForms
    'pyramid-deform',  # we will start using deform/colander/peppercorn
    'pastescript',     # we use this for development (maybe deploy)
    'psycopg2',        # dbapi for postgresql
    'deform_bootstrap', # testing 
    ]

setup(name='trumpet',
      version=version,
      setup_requires=['github-distutils >= 0.1.0'],
      description="build a website with pyramid",
      long_description="""\
Start a website with pyramid""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='pyramid, sqlalchemy, scss',
      author='Joseph Rawson',
      author_email='joseph.rawson.works@gmail.com',
      url='https://github.com/umeboshi2/trumpet',
      license='Public Domain',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=requires,
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
