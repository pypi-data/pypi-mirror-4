#!/usr/bin/env python
#-*- mode: python; coding: utf-8 -*-

from setuptools import setup, find_packages

setup(name="sleipnir-restfulie",
      version="0.19",
      description="Write hypermedia aware resource based clients and servers",
      author="Carlos Martín",
      author_email="inean.es@gmail.com",
      url="http://restfulie.caelumobjects.com/",
      download_url="https://github.com/inean/restfulie-py",
      packages=find_packages(),
      license="Apache 2.0",
      keywords="rest, async, tornado, http, hypermedia",
      zip_safe=False,
      install_requires=[
          "oauth2    >= 1.5",
          "tornado   == 2.4.1",
          "hal-json  >= 0.1",
          "jsonpatch >= 0.12",
      ],
      long_description="""
      CRUD through HTTP is a good step forward to using resources
      and becoming RESTful, another step further is to make use of
      hypermedia aware resources and Restfulie allows you to do it in
      Python.
      """,
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Web Environment",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: Apache Software License",
          "Operating System :: MacOS :: MacOS X",
          "Operating System :: Microsoft :: Windows",
          "Operating System :: POSIX",
          "Programming Language :: Python",
      ],
      )
