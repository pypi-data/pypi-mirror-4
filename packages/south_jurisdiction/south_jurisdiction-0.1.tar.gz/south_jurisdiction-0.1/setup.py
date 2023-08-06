#!/usr/bin/python

from os.path import abspath, dirname, join
from setuptools import setup
from south_jurisdiction import __version__

long_description = open(join(dirname(abspath(__file__)), 'README'))

setup(
    name='south_jurisdiction',
    version=__version__,
    description='South Jurisdiction: South Migrations contained for Django',
    long_description=long_description,
    author='Alex Couper',
    author_email='amcouper@gmail.com',
    url='https://github.com/alexcouper/django-south-jurisdiction/',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
    packages=[
        'south_jurisdiction',
        'south_jurisdiction.management',
        'south_jurisdiction.management.commands',
    ],
    install_requires=['south'],

)
