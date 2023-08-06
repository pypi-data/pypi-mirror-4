#!/usr/bin/env python
#
# Copyright (c) 2009-2011
#   Brendan W. McAdams <bwmcadams@evilmonkeylabs.com>
#   Ryan Bourgeois <bluedragonx@gmail.com>
#

try:
    from setuptools import setup, find_packages
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name = 'beaker_mongodb',
    version = '0.2',
    description = 'Beaker backend to write sessions and caches to a ' +\
    'MongoDB schemaless database.',
    long_description = '\n' + open('README.rst').read(),
    author='Ryan Bourgeois',
    author_email = 'bluedragonx@gmail.com',
    keywords = 'mongo mongodb beaker cache session',
    license = 'New BSD License',
    url = 'https://github.com/BlueDragonX/mongodb_beaker/',
    tests_require = ['nose', 'webtest'],
    test_suite='nose.collector',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages = find_packages(),
    include_package_data=True,
    zip_safe = True,
    entry_points="""
    [beaker.backends]
    mongodb = beaker_mongodb:MongoDBNamespaceManager    
    """,
    requires=['pymongo', 'beaker'],
    install_requires = [
        'pymongo>=1.9',
        'beaker>=1.5'
    ]

)
