#!/usr/bin/env python
import os
from setuptools import setup, find_packages

def long_description():
    """
    Build the long description from a README file located in the same directory
    as this module.
    """
    base_path = os.path.dirname(os.path.realpath(__file__))
    readme = open(os.path.join(base_path, 'README.rst'))
    try:
        return readme.read()
    finally:
        readme.close()

setup(
    name='django-languages',
    version='0.1',
    description='Provides a language field for Django models.',
    long_description=long_description(),
    author='Ander Martinez',
    author_email='ander.basaundi@gmail.com',
    url='http://bitbucket.org/basaundi/django-languages/',
    packages=find_packages(),
    zip_safe=False,
    package_data={'django_languages': [
        'bin/*.py',
    ]},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)
