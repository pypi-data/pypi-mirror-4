#!/usr/bin/env python
"""
Installation script:

To release a new version to PyPi:
- Ensure the version is correctly set in oscar.__init__.py
- Run: python setup.py sdist upload
"""

from setuptools import setup, find_packages

setup(
    name = "django-url-fullpath-redirect",
    version = '0.1.2',
    url = "https://github.com/alifanov/django-url-fullpath-redirect",
    author = "Lifanov Alexander",
    author_email = "lifanov.a.v@gmail.com",
    description = ("Fork of django-url-tracker with query_string support"),
    long_description = open('README.rst').read(),
    license = "BSD",
    packages = find_packages(exclude=["docs*", "tests*"]),
    include_package_data = True,
    install_requires=[
        'django>=1.3.1',
        'South>=0.7.3',
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
    keywords = "seo, django, framework",
)


