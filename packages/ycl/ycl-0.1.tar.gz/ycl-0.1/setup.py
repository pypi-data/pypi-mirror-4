#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2013 by Łukasz Mierzwa
    :contact: l.mierzwa@gmail.com
"""


from setuptools import setup, find_packages


setup(
    name='ycl',
    version='0.1',
    license='GPLv3',
    description='YAML config loader',
    author='Łukasz Mierzwa',
    author_email='l.mierzwa@gmail.com',
    url='https://github.com/prymitive/yaml_config_loader',
    packages=find_packages(),
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    platforms=['any'],
)
