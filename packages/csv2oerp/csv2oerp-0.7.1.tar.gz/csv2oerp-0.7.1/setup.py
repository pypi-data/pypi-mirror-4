#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from sphinx.setup_command import BuildDoc
from distutils.core import setup

name = 'csv2oerp'
version = '0.7.1'
setup(name=name,
      version=version,
      description='Python CSV to OpenERP importation library',
      long_description=open('README').read(),
      author='Stéphane Mangin',
      author_email='stephane.mangin@freesbee.fr',
      url='https://bitbucket.org/StefMangin/python-csv2oerp-0.7',
      download_url='',
      keywords='openerp import csv xls xlsx data importation migration xml xml-rpc xmlrpc rpc json',
      packages=['csv2oerp', 'csv2oerp.models'],
      license='LGPLv3+',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2.7',
          'Topic :: Database',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
      data_files = [
        ('/usr/bin/',[
            'bin/csv2oerp-gc',
        ]),
    ],
      # 'build_sphinx' option
      command_options={
            'build_sphinx': {
                #'project': ('setup.py', name),
                'version': ('setup.py', version),
                'release': ('setup.py', version),
                'source_dir': ('setup.py', 'doc/source'),
                'build_dir': ('setup.py', 'doc/build'),
            }
      },
      cmdclass={
          "build_sphinx": BuildDoc
      }
)

