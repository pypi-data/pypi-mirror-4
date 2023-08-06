#!/usr/bin/env python
try:
    from setuptools import setup, find_packages
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name = 'beaker-mongo',
    version = '0.2.1',
    description = 'Beaker backend MongoDB',
    long_description = '\n' + open('README').read(),
    author='Vadim Statishin',
    author_email = 'statishin@gmail.com',
    keywords = 'mongo mongodb beaker cache session',
    license = 'New BSD License',
    url = 'http://bitbucket.org/cent/beaker-mongo/',
    #tests_require = ['nose', 'webtest'],
    #test_suite='nose.collector',
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
          mongodb = beaker.ext.mongodb:MongoDBNamespaceManager
    """,
    requires=['pymongo', 'beaker'],
    install_requires = [
        'pymongo>=2.5',
        'beaker>=1.5'
    ]

)
