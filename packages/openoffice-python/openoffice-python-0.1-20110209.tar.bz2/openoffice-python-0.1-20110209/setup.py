#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

setup(
    name='openoffice-python',
    description='Enhanced Python interfaces to OpenOffice.org',
    long_description= open("README").read(),
    packages=['openoffice'],
    version='0.1',
    author='Hartmut Goebel',
    author_email='h.goebel@goebel-consult.de',
    url          = "http://openoffice-python.origo.ethz.ch/",
    download_url = "http://openoffice-python.origo.ethz.ch/download",
    platforms=['POSIX'],
    license='GPLv3',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
    requires=['python(>=2.3)'],
    )
