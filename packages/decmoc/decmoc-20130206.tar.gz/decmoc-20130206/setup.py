#!/usr/bin/env python
from setuptools import find_packages, setup

setup(name='decmoc',
      version='20130206',
      description="Declarative mocking",
      url='https://github.com/lvh/decmoc',

      author='Laurens Van Houtven',
      author_email='_@lvh.cc',

      packages=find_packages(),

      install_requires=['mock'],

      license='ISC',
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Twisted",
        "License :: OSI Approved :: ISC License (ISCL)",
      ]
)
