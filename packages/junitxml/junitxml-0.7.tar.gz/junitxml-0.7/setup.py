#!/usr/bin/env python

from distutils.core import setup

setup(name="junitxml",
      version="0.7",
      description="PyJUnitXML, a pyunit extension to output JUnit compatible XML.",
      maintainer="Robert Collins",
      maintainer_email="robertc@robertcollins.net",
      url="https://launchpad.net/pyjunitxml",
      packages=['junitxml', 'junitxml.tests'],
      scripts=['pyjunitxml'],
      license="LGPL-3",
      )
