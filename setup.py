# -*- coding: utf-8 -*-
import os
import io
from setuptools import setup
from setuptools import find_packages

from EditOnline import __version__

here = os.path.abspath(os.path.dirname(__file__))

setup(name='EditOnline',
      version=__version__,
      description='A simple online file editor by Python base on Ace.js.',
      url='https://github.com/sintrb/EditOnline',
      classifiers=[
          'Intended Audience :: Developers',
          'License :: Apache License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords='EditOnline',
      author='sintrb',
      author_email='lxneng@gmail.com',
      license='Apache',
      # packages=find_packages('../'),
      py_modules = ['EditOnline'],
      # data_files = [('static', ['static']), ('editor.html',['editor.html'])],
      package_data = {'': ['*.html'], 'static': ['*.js']},
      # package_dir={'': '.'},
      include_package_data=True,
      zip_safe=False)