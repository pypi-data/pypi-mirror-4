#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Hack to prevent stupid "TypeError: 'NoneType' object is not callable" error
# in multiprocessing/util.py _exit_function when running `python
# setup.py test` (see
# http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html)
try:
    import multiprocessing
except ImportError:
    pass

from setuptools import setup, find_packages

setup(
    name='rtorrent-notify',
    version='1.0.0',
    description='Notify of rtorrent events, through RSS or IRC (using Irker)',
    long_description=open('README').read(),
    author='Laurent Bachelier',
    author_email='laurent@bachelier.name',
    url='http://git.p.engu.in/laurentb/rtorrent-notify/',
    packages=find_packages(),
    entry_points={'console_scripts': ['rtorrent-notify = rtorrentnotify.cli:main']},
    install_requires=['PyRSS2Gen'],
    test_suite='nose.collector',
    tests_require='nose>=1.0',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet',
    ],
)
