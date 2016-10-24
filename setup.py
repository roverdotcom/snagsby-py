#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.md') as f:
    readme = f.read()

# Load the version in a safe way
version_data = {}
execfile('./snagsby/version.py', version_data)

requirements = [
    'boto3>=1.0.0',
]

test_requirements = [
    'mock>=1.0.1',
    'httpretty==0.8.14',
]

setup(
    name='snagsby',
    version=version_data['__version__'],
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
    test_suite='tests',
    tests_require=test_requirements,
)
