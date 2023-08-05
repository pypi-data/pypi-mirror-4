#!/usr/bin/env python

from setuptools import setup

setup(name='bullfrog',
      version='0.0.1',
      description='It eats everything',
      author='Zach Smith',
      author_email='zachmsmith@gmail.com',
      install_requires=['flask'],
      py_modules=['bullfrog'],
      entry_points={
          'console_scripts': [
              'bullfrog = bullfrog:run',
          ]
      },
)
