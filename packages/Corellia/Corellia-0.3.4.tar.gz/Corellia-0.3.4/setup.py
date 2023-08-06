#!/usr/bin/env python

from setuptools import setup


requires = ["python-snappy>=0.3", "redis>=2.7.0"]

setup(name='Corellia',
      version='0.3.4',
      description='Helper classes to write distributed applications',
      author='Zhu Zhaomeng',
      author_email='zhaomeng.zhu@gmail.com',
      packages=['Corellia'],
      install_requires=requires,
      url="https://github.com/Tefx/Corellia",
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
          "Topic :: Utilities",
      ]
      )