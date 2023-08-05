#!/usr/bin/env python

# $Id: setup.py,v 24a10b7e2518 2012/06/29 20:59:56 jon $

from distutils.core import setup

setup(name="jonpy",
      version="0.11",
      description="Jon's Python modules",
      author="Jon Ribbens",
      author_email="jon+jonpy@unequivocal.co.uk",
      url="http://jonpy.sourceforge.net/",
      packages=['jon', 'jon.wt']
)
