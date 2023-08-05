#!/usr/bin/env python

from distutils.core import setup

setup(name='dse',
      version='4.0.0-beta',
      description='DSE - Simplified "bulk" insert/update/delete for Django.',
      author='Thomas Weholt',
      author_email='thomas@weholt.org',
      long_description=open('README.txt').read(),
      packages = ['dse',],
      #install_requires = ['django >= 1.5.0'],
      url = "https://bitbucket.org/weholt/dse4",
      classifiers=[
          'Development Status :: 4 - Beta',
          #'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Framework :: Django',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Database',
          ],
      )
