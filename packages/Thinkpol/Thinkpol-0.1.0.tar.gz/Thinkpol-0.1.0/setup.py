#!/usr/bin/env python

from setuptools import setup


requires = ["gevent>=0.13.8", "python-snappy>=0.4", "yajl>=0.3.5"]

setup(name='Thinkpol',
      version='0.1.0',
      description='Helper classes to write monitoring part in distributed applications',
      author='Zhu Zhaomeng',
      author_email='zhaomeng.zhu@gmail.com',
      packages=['Thinkpol'],
      install_requires=requires,
      url="https://github.com/Tefx/Thinkpol",
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
          "Topic :: Utilities",
      ]
      )