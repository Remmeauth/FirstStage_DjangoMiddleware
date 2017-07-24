#!/usr/bin/env python

from distutils.core import setup

setup(name='remme-django',
      version='1.0.0',
      description='Remme authentication protocol implementation for Django',
      author='Yevhenii Babichenko',
      author_email='eugene.babichenko@gmail.com',
      packages=['remme_django'],
      install_requires=['Django', 'requests', 'cryptography']
)
