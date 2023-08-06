# -*- coding: utf-8 -*-

"""
Created on 2013-03-05
:author: Andreas Kaiser (disko)
"""

import os

from setuptools import find_packages
from setuptools import setup


version = '0.2.1'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'bootstrap_timepicker', 'test_bootstrap_timepicker.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.bootstrap_timepicker',
    version=version,
    description="Fanstatic packaging of Bootstrap Timepicker",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Andreas Kaiser',
    author_email='disko@binary-punks.com',
    url='https://github.com/disko/js.bootstrap_timepicker',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    setup_requires=[],
    install_requires=[
        'fanstatic',
        'js.bootstrap',
        'js.jquery',
        'setuptools',
    ],
    entry_points={
        'fanstatic.libraries': [
            'bootstrap_timepicker = js.bootstrap_timepicker:library',
        ],
    },
)
