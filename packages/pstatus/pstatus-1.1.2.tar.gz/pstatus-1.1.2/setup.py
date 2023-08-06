#!/usr/bin/env python
from setuptools import setup
from pstatus import __version__

setup(
    name='pstatus',
    version = __version__,
    description='Process Status Code Helper',
    long_description=open('README.rst').read(),
    author="Michael Komitee",
    author_email="mkomitee@gmail.com",
    url='https://github.com/mkomitee/pstatus',
    packages=['pstatus'],
    package_data={'': ['LICENSE', 'AUTHORS']},
    include_package_data=True,
    license=open('LICENSE').read(),
    classifiers = ('Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'Natural Language :: English',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: POSIX',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.1',
                   'Programming Language :: Python :: 3.2',
                   'Programming Language :: Python :: 3.3')
)
