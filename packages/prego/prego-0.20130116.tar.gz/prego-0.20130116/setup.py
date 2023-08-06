#!/usr/bin/python
# -*- coding:utf-8; tab-width:4; mode:python -*-

import distutils.core
from setuptools import find_packages

distutils.core.setup(
    name             = 'prego',
    version          = '0.20130116',
    author           = 'David Villa Alises',
    author_email     = 'David.Villa@gmail.com',
    packages         = find_packages(),
    entry_points     = {
        'console_scripts': [
            'prego = prego.console:run',
            ]},
    data_files       = [('/usr/share/doc/prego', ['README.rst']),
                        ('/usr/lib/prego', ['config.spec', 'defaults.config'])],
    url              = 'https://bitbucket.org/arco_group/prego',
    license          = 'GPLv3',
    description      = 'System test framework over POSIX shells',
    long_description = open('README.rst').read(),
    requires         = ['hamcrest', 'commodity'],
    classifiers      = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        ],
)
