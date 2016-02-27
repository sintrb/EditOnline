# -*- coding: utf-8 -*-
import os, io
from setuptools import setup

from EditOnline.EditOnline import __version__
here = os.path.abspath(os.path.dirname(__file__))
README = io.open(os.path.join(here, 'README.rst'), encoding='UTF-8').read()
CHANGES = io.open(os.path.join(here, 'CHANGES.rst'), encoding='UTF-8').read()
setup(name='EditOnline',
      version=__version__,
      description='A simple online file editor by Python base on Ace.js.',
      long_description=README + '\n\n\n' + CHANGES,
      url='https://github.com/sintrb/EditOnline',
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Topic :: Text Editors',
      ],
      keywords='EditOnline Ace.js',
      author='sintrb',
      author_email='sintrb@gmail.com',
      license='Apache',
      packages=['EditOnline'],
      scripts = ['EditOnline/EditOnline', 'EditOnline/EditOnline.bat'],
      include_package_data=True,
      zip_safe=False)
