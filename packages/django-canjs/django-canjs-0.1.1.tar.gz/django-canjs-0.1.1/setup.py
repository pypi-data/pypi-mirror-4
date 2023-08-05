#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = "django-canjs",
    version = "0.1.1",
    packages = find_packages(),
    include_package_data = True,
    author = "Aljosa Mohorovic",
    author_email = "aljosa.mohorovic@gmail.com",
    description = "CanJS integration library for Django",
    long_description = \
"""
RUN!!!
===

**This project is alpha quality software and should be considered as placeholder for something that could eventually be usable.
Therefor it has no documentation or any kind of support and shouldn't be used.**

django-canjs
===

CanJS integration library for Django
""",
    license = "MIT License",
    keywords = "django canjs",
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    platforms = ['any'],
    url = "https://github.com/aljosa/django-canjs",
)
