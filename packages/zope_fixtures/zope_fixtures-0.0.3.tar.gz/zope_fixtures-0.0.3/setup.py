#!/usr/bin/env python

from distutils.core import setup
import os.path

description = file(os.path.join(os.path.dirname(__file__), 'README'), 'rb').read()

setup(name="zope_fixtures",
      version="0.0.3",
      description="Zope fixtures, support for testing Zope environments.",
      long_description=description,
      maintainer="Robert Collins",
      maintainer_email="robertc@robertcollins.net",
      url="https://launchpad.net/python-zope-fixtures",
      packages=['zope_fixtures', 'zope_fixtures.tests'],
      package_dir = {'':'lib'},
      classifiers = [
          'Development Status :: 6 - Mature',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Quality Assurance',
          'Topic :: Software Development :: Testing',
          ],
      install_requires = [
          'fixtures',
          'testtools',
          'zope.component',
          'zope.interface',
          ],
      )
