# -*- coding: utf-8 -*-
""" useragent setup.py script """

# system
from distutils.core import setup
from os.path import join, dirname


def get_contents(fname):
    return open(join(dirname(__file__), fname)).read()

setup(
    name='useragent',
    version='0.1.0',
    author='Don Spaulding',
    author_email='donspauldingii@gmail.com',
    packages=['useragent', 'useragent.test'],
    include_package_data=True,
    url='https://bitbucket.org/mirusresearch/useragent',
    license=get_contents('LICENSE.txt'),
    long_description=get_contents('README.txt'),
    test_suite='nose.collector',
    test_requires=["Nose", "coverage"],
)
