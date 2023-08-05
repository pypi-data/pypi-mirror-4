#!/usr/bin/env python

from setuptools import setup


requires = ["gevent>=0.13.0", "python-snappy>=0.3", "Husky>=0.1.0", "redis>=2.7.0"]

setup(name='Corellia',
      version='0.2.4',
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