# Copyright 2012 django-compresshtml authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from setuptools import setup, find_packages
from compresshtml import __version__

README = open('README.md').read()

setup(name='django-compresshtml',
      version=__version__,
      description='HTML compressor for django',
      long_description=README,
      author='kamagatos',
      author_email='kamagatos@gmail.com',
      packages=find_packages(),
      include_package_data=True,
      install_requires=['django',],
     )
