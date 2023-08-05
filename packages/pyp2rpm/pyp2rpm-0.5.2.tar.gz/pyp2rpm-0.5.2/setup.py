#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyp2rpmlib.version import version

try:
    from setuptools import setup
except:
    from distutils.core import setup


description = """Convert Python packages to RPM SPECFILES. The packages can be downloaded from
PyPI and the produced SPEC is in line with Fedora Packaging Guidelines.

Users can provide their own templates for rendering the package metadata. Both the package
source and metadata can be extracted from PyPI or from local filesystem (local file doesn't
provide that much information though)."""

setup(
    name = 'pyp2rpm',
    version = version,
    description = "Convert Python packages to RPM SPECFILES",
    long_description = description,
    keywords = 'pypi, rpm, spec, specfile, convert',
    author = 'Bohuslav "Slavek" Kabrda',
    author_email = 'bkabrda@redhat.com',
    url = 'https://bitbucket.org/bkabrda/pyp2rpm/',
    license = 'MIT',
    packages = ['pyp2rpmlib', ],
    package_dir = {'pyp2rpmlib': 'pyp2rpmlib'},
    package_data = {'pyp2rpmlib': ['templates/*.spec']},
    scripts = ['pyp2rpm', ],
    install_requires=['Jinja2',
                      'distribute',
                     ],
    setup_requires = ['pytest',
                      'flexmock >= 0.9.3'
                     ],
    classifiers = ['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'Intended Audience :: System Administrators',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Build Tools',
                   'Topic :: System :: Software Distribution',
                  ]
)
