## -*- coding: utf-8 -*-
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'pyramid_handlers',
    'pyramid_simpleform',
    'pyramid_beaker',
    'zope.sqlalchemy',
    'waitress',
    'formencode',
    'python-magic',
    'FormAlchemy',
    'hgtools'
    ]

setup(name='ringo',
      version='0.1',
      description='Ringo is a framework to build pyramid applications.',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        ],
      author='Torsten Irländer',
      author_email='torsten@irlaender.de',
      url='https://bitbucket.org/ti/ringo',
      keywords='web wsgi bfg pylons pyramid framework',
      packages=find_packages(),
      include_package_data=True,
      #use_hg_version=True,
      zip_safe=False,
      test_suite='ringo',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = ringo:main
      [console_scripts]
      initialize_ringo_db = ringo.scripts.initializedb:main
      """,
      )
