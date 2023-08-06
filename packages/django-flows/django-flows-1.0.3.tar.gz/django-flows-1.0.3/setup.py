# -*- coding: UTF-8 -*-
from distutils.core import setup
from setuptools import find_packages
import time


_version = "1.0.3"
_packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests", "example"])
    
# common dependencies
_install_requires = [
            'django>=1.4,<1.6',
       ]

setup( name='django-flows',
       url='https://github.com/laterpay/django-flows',
       version=_version,
       packages=_packages,
       install_requires=_install_requires,
)
