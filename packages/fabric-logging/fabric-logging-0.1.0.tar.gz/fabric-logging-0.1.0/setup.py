#!/usr/bin/env python

import sys

from setuptools import setup, find_packages

from fabric.version import get_version


readme = open('README').read()

v = get_version('short')
long_description = """
To find out what's new in this version of Fabric, please see `the changelog
<http://docs.fabfile.org/en/%s/changelog.html>`_.

You can also install the `in-development version
<https://github.com/fabric/fabric/tarball/master#egg=fabric-dev>`_ using
pip, with `pip install fabric==dev`.

----

%s

----

For more information, please see the Fabric website or execute ``fab --help``.
""" % (v, readme)

setup(
    name='fabric-logging',
    #version=get_version('short'),
    version='0.1.0',
    description='Adds option to redirect all stdout/stderr through standard Python logging. Very much a work in progress',
    long_description=long_description,
    author='Matt Long',
    author_email='matt@mattlong.org',
    url="https://github.com/mattlong/fabric",
    packages=find_packages(),
    test_suite='nose.collector',
    tests_require=['nose', 'fudge<1.0'],
    install_requires=['ssh>=1.7.14'],
    entry_points={
        'console_scripts': [
            'fab = fabric.main:main',
        ]
    },
    classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: BSD License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Unix',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Topic :: Software Development',
          'Topic :: Software Development :: Build Tools',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Clustering',
          'Topic :: System :: Software Distribution',
          'Topic :: System :: Systems Administration',
    ],
)
