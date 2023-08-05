#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages
    
import os

setup(
    name = "django-piston_0_2_3_patch_init",
    version = "0.2.3",
    url = '',
	download_url = '',
    license = 'BSD',
    description = "Piston omits __init__.py in its pkg, so pip installs dont work unless you add a patch like this.",
    author = 'Vijay Ragavan',
    author_email = 'vijay@moneychakra.com',
    packages = find_packages(),
    include_package_data = True,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
