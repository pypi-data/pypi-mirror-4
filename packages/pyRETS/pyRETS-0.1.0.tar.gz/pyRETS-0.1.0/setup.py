#!/usr/bin/env python

from distutils.core import setup
from lib.pyRETS import *

setup(name="pyRETS",
    version="0.1.0",
    author="Paul Trippett",
    author_email="paul@stormrets.com",
    url="http://www.stormrets.com/plugins/pyrets/",
    license='LICENSE.txt',
    description="RETS Client Library in Pure Python",
    long_description=open('README.txt').read(),
    package_dir = {'': 'lib'}
)