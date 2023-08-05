#!/usr/bin/env python
# vi:si:et:sw=4:sts=4:ts=4
# encoding: utf-8
try:
    from setuptools import setup
except:
    from distutils.core import setup

def get_version():
    import subprocess
    p = subprocess.Popen(['git', 'describe', '--tags'], stdout=subprocess.PIPE)
    r = p.communicate()
    return r[0].strip()

setup(
    name="basedata",
    version=get_version() ,
    description="support library for basedata.org",
    author="bd",
    author_email="code@basedata.org",
    url="https://basedata.org",
    download_url="https://basedata.org/code/python-basedata/",
    license="GPL 3",
    packages=['basedata'],
    install_requires=[],
    keywords = [
    ],
    classifiers = [
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

