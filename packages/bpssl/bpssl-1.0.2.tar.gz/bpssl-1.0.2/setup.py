#!/usr/bin/env python
#:coding=utf-8:

from setuptools import setup, find_packages
 
setup (
    name='bpssl',
    version='1.0.2',
    description='SSL/HTTPS for Django',
    long_description=open('README.rst').read() + '\n' + open('CHANGES.rst').read(),
    author='Ian Lewis',
    author_email='ian@beproud.jp',
    url='http://bitbucket.org/beproud/bpssl/',
    classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Framework :: Django',
      'Environment :: Plugins',
      'Environment :: Web Environment',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(),
    namespace_packages=[
        'beproud',
        'beproud.django',
    ],
    install_requires=[
        'Django>=1.2',
    ],
    test_suite='tests.main',
)
