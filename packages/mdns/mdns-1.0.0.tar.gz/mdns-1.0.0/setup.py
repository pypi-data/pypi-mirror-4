#!/usr/bin/env python

from distutils.core import setup

setup(name='mdns',
    version='1.0.0',
    description='mDNS library',
    author='Peter V. Saveliev',
    author_email='peet@redhat.com',
    url='https://github.com/svinota/mdns',
    license="GPLv3+",
    packages=[
        'mdns'
        ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Operating System :: POSIX',
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
        ],
    long_description='''
mDNS protocol implementation
============================

The library allows you to use mDNS/Zeroconf protocol in
your applications.

Also, it contains DNSSEC and Heartbeat extensions.

Links
=====

 * home: https://github.com/svinota/mdns
 * bugs: https://github.com/svinota/mdns/issues
 * pypi: http://pypi.python.org/pypi/mdns/

Changes
=======

1.0.0
-----

 * initial pypi release
'''
)
