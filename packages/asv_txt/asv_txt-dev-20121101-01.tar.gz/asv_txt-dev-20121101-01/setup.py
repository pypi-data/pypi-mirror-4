#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from asv_txt import __name__, __version__, __keywords__, __description__
##
## To deploy use
## $ python ./setup.py sdist upload
##
## Your need increase version before it !!!
##
                  

packages  = find_packages()
setup(
    name = __name__,
    version = __version__,
    packages = packages,
    include_package_data = True,

    install_requires = [
        'asv_utils>=dev-20121101-01',
        'asv_imgs>=dev-20121101-01',
        'creoleparser>=0.7.3',
    ],
    setup_requires = [
        'distribute>=0.6',
    ],

    author       = 'Sergey Vasilenko',
    author_email = 'sv@makeworld.ru',
    keywords  = __keywords__,
    description  = __description__,
    long_description = open('README.txt').read(),
    license   = 'GPL',
    platforms = 'All',
    url  = 'http://bitbucket.org/xenolog/{0}/wiki/Home'.format(__name__),

    classifiers = [
        'Environment :: Other Environment',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Natural Language :: Russian',
        'Development Status :: 4 - Beta',
        'Topic :: Software Development :: Libraries',
    ],
    zip_safe = False,
)


