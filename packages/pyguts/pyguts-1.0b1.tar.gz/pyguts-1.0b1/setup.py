#!/usr/bin/env python

from setuptools import setup

setup(name='pyguts',
      version='1.0b1',
      description='A pygame front-end for spine-python.',
      author='Terry Simons',
      author_email='terry.simons@gmail.com',
      url='https://github.com/terrysimons/spine-python/pyguts',
      package_dir={'pyguts': 'src'},
      packages=['pyguts'],
      install_requires=['spine_python']
     )
