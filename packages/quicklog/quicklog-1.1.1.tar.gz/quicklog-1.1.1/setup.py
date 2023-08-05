#!/usr/bin/env python

from setuptools import setup

setup(
    name='quicklog',
    version='1.1.1',
    description='Small logging utility',
    author='Chris Anoikesis',
    author_email='tutow@hotmail.com',
    url='http://packages.python.org/QuickLog',
    packages=["quicklog"],
      long_description="""\
      QuickLog is a small logging utility.
      """,
      classifiers=[
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 2 :: Only",
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "Topic :: Utilities",
      ],
      keywords='logging',
      license='MIT',
      install_requires=[],
    )

