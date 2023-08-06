#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django_multiuploader_file",
    version = "2.0",
    author = "Matheus Lima",
    author_email = "matheus.se@gmail.com",
    description = ("A fork of django-multiuploader that allow upload any file type."),
    license = "Apache License 2.0",
    keywords = "django ios notification push",
    url = "https://github.com/matheussl/django_multiuploader",
    packages = find_packages(),
    package_data = {
        'multiuploader': [
            'templates/multiuploader/*.html',
            'static/multiuploader/scripts/*.js',
            'static/multiuploader/site_graphics/*.gif',
            'static/multiuploader/styles/*.css',
        ],
    },
    long_description="N/A",

    install_requires = [
        'PIL>=1.1.7',
        'sorl-thumbnail>=11.12',
    ],
)
