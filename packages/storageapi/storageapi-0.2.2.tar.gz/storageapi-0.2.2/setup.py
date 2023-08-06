#!/usr/bin/env python

# This file is part of StorageAPI, by Luke Granger-Brown
# and is licensed under the MIT license, under the terms listed within
# LICENSE which is included with the source of this package

from distutils.core import setup

setup(
    name='storageapi',
    version='0.2.2',
    description='http://getstorage.net for Python',
    author='Luke Granger-Brown',
    author_email='oss.getstorage.python@lukegb.com',
    url='http://getstorage.net',
    packages=['storage'],
    requires=[
        'requests',
    ],
    install_requires=[
        'requests',
    ],
    scripts=['scripts/storagecli'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Communications :: File Sharing'
    ]
)
