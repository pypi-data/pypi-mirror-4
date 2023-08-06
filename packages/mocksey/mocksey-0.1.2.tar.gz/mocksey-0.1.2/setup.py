#!/usr/bin/env python

import mocksey

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

packages = [
    'mocksey',
]

requires = []

setup(
    name='mocksey',
    version=mocksey.__version__,
    description=mocksey.__description__,
    long_description=open('README.rst').read(),
    author='Chris McGraw',
    author_email='mitgr81+mocksey@mitgr81.com',
    url='https://github.com/mitgr81/mocksey',
    test_suite='mocksey.tests',
    packages=packages,
    package_dir={'mocksey': 'mocksey'},
    package_data={'': ['LICENSE']},
    include_package_data=True,
    install_requires=requires,
    license=open('LICENSE').read(),
    zip_safe=False,
    classifiers=(
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: Testing"
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ),
)
