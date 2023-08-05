#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages

setup(
    name="colly",
    version="0.2.1",
    author="Adam J. Gamble",
    author_email="mail@adamgamble.com",
    description=open('README').readline(),
    license='MIT',
    long_description='',
    packages=['colly', 'colly.commands'],
    url="http://repo.or.cz/w/colly.git",
    include_package_data=True,
    entry_points = { 
        'console_scripts': [
            'colly = colly:main'
        ]
    },
    install_requires = [
        'simplejson'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Filters'
    ],
)
