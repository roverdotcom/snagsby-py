#!/usr/bin/env python

import re
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.md') as f:
    readme = f.read()

# Load the version in a safe way
with open('./snagsby/version.py') as f:
    version_raw = f.read()
    regex = re.compile(r'__version__\s*=\s*\'([^\']+)\'')
    match = regex.match(version_raw)
    version = match.group(1)

requirements = [
    'boto3>=1.7',
]

test_requirements = [
    'mock>=1.0.1',
    'httpretty==0.8.14',
    'testfixtures',
    'pytest',
]

setup(
    name='snagsby',
    version=version,
    description='Snagsby for python',
    long_description=readme,
    author='Bryan Shelton',
    author_email='bryan@rover.com',
    url='https://github.com/roverdotcom/snagsby-py',
    packages=[
        'snagsby',
    ],
    package_dir={'snagsby': 'snagsby'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    zip_safe=True,
    keywords='snagsby',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
    ],
    entry_points={
        'console_scripts': [
            'snagsby=snagsby.cli:main'
        ]
    },
    test_suite='tests',
    tests_require=test_requirements,
)
