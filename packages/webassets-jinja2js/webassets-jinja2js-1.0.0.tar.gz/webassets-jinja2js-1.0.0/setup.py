#!/usr/bin/env python
# coding: utf-8
from setuptools import setup, find_packages

setup(name="webassets-jinja2js",
    version="1.0.0",
    description="Integration of pwt.jinja2js compiler with the webassets package.",
    long_description=open("README.rst").read(),
    author="Michael Su",
    author_email="mdasu1@gmail.com",
    url="https://pypi.python.org/pypi/webassets-jinja2js/",
    license="BSD",
    packages=find_packages(),
    install_requires=['webassets'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ]
)
