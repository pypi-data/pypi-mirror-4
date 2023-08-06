#!/usr/bin/env python
"""
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from distutils.core import setup

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: Python Software Foundation License',
    'Operating System :: MacOS',
    'Operating System :: Microsoft',
    'Operating System :: POSIX',
    'Programming Language :: Python',
    'Topic :: Communications',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

setup(
    author='Andrey Kaygorodov',
    author_email='info@kaygorodov.com',
    name='JRPC-utils',
    version='0.2.1',
    url='http://github.com/kaygorodov/jrpc-utils',
    description='A set of useful classes and functions for working with JSON-RPC v.2.0',
    py_modules=['jrpcutils'],
    license='http://www.apache.org/licenses/LICENSE-2.0',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
)
