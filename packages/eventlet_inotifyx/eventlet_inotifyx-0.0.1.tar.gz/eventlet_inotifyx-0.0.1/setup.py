#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='eventlet_inotifyx',
    version='0.0.1',
    description='''Thin wrapper around inotifyx to use with eventlet''',
    long_description=open('README.rst').read(),
    author='Roma Sokolov',
    author_email='sokolov.r.v@gmail.com',
    url='https://github.com/little-arhat/eventlet_inotifyx',
    packages=[
        'eventlet_inotifyx'
    ],
    install_requires=['eventlet', 'inotifyx'],
    license='MIT',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ),
)
