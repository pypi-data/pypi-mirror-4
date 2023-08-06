#!/usr/bin/env python
import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

requires = ['decorator']

setup(
    name='pto',
    version='0.0.4',
    description='Timeouts for arbitrary Python functions.',
    long_description=open('README.rst').read(),
    author='Hank Gay',
    author_email='hank.gay@gmail.com/',
    packages=['pto',],
    install_requires=requires,
    license=open('LICENSE.txt').read(),
    zip_safe=False,
    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: BSD',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries',
    ),
)
