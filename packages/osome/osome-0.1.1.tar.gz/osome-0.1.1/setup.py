# -*- coding: utf-8 -*-
import sys
reload(sys).setdefaultencoding("UTF-8")

from setuptools import setup, find_packages
from osome import path

description = "The bucket of python shell helpers, no dependencies, simple API."

project = path(__file__).dir()

long_description = (project / 'README.rst').content
version = (project / 'VERSION').content
license = (project / 'LICENSE').content

setup(name='osome',
      version=version,
      packages=find_packages(),
      author='Sebastian Pawluś',
      author_email='sebastian.pawlus@gmail.com',
      url='https://github.com/xando/osome',
      description=description,
      keywords="shell tools shell path ",
      license=license,
      long_description=long_description,
      include_package_data=True,
      platforms=['any'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: Implementation :: PyPy'
      ],
)