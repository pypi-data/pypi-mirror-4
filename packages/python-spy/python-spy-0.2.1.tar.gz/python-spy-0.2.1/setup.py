#!/usr/bin/env python

from distutils.core import setup

setup(
    name = 'python-spy',
    version = '0.2.1',
    author = 'Seimei',
    author_email = 'seimeininja@gmail.com',
    description = 'Another Python Spider framework',
    url = 'https://github.com/seimei/python-spy',
    packages = ['python-spy'],    
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],   
    install_requires = ['gevent', 'python-mysql'],
)
