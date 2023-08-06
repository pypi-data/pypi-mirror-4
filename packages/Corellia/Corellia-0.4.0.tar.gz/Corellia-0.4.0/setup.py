#!/usr/bin/env python
from setuptools import setup
from distutils.extension import Extension

requires = ["redis>=2.7.0"]
ext_modules=[
    Extension("Corellia.taskqueue", ["Corellia/taskqueue.c"]),
    Extension("Corellia.fastredis", ["Corellia/fastredis.c"]),
    Extension("Corellia.client", ["Corellia/client.c"]),
    Extension("Corellia.worker", ["Corellia/worker.c"]),
]


setup(
    name='Corellia',
    version='0.4.0',
    description='Fast Task Queue Using Redis',
    author='Zhu Zhaomeng',
    author_email='zhaomeng.zhu@gmail.com',
    packages=['Corellia', 'Corellia.utils'],
    install_requires=requires,
    url="https://github.com/Tefx/Corellia",
    ext_modules = ext_modules,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Topic :: Utilities",
    ]
)