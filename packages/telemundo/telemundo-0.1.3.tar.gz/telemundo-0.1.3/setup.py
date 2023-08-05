#!/usr/bin/env python

from setuptools import setup, find_packages

version = __import__('telemundo').get_version()

setup(
    name='telemundo',
    version=version,
    url='https://github.com/telemundo/telemundo-py',
    author='Rodolfo Puig',
    author_email='rodolfo.puig@nbcuni.com',
    description='Telemundo Py',
    keywords='Telemundo',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
