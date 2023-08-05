# -*- coding: utf-8 -*-
"""
Created on 2012-10-18 17:49
:author: Andreas Kaiser (disko)
"""

import os
from setuptools import find_packages
from setuptools import setup

version = '0.1'


def read(*rnames):

    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.rst')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='deform_widget_jquery_option_tree',
    version=version,
    description="jQuery Option Tree widget for deform",
    long_description=long_description,
    classifiers=[
        "Environment :: Plugins",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
    ],
    keywords='deform widget',
    author='Andreas Kaiser',
    author_email='disko@binary-punks.com',
    url='https://github.com/disko/deform_widget_jquery_option_tree',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "deform",
    ],
    entry_points={},
)
