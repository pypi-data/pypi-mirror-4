# -*- coding: utf-8 -*-
"""django-c5filemanager setup file.

THIS SOFTWARE IS UNDER BSD LICENSE.
Copyright (c) 2010-2012 Daniele Tricoli <eriol@mornie.org>

Read LICENSE for more informations.
"""
import os

from setuptools import setup, find_packages

from c5filemanager import get_version

def read(filename):
    """Small tool function to read README."""
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

classifiers = '''
Development Status :: 4 - Beta
Environment :: Web Environment
Intended Audience :: Developers
License :: OSI Approved :: BSD License
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Framework :: Django
'''.strip().splitlines()

setup(
    name='django-c5filemanager',
    version=get_version(),
    license = 'BSD',
    description='Django connector for Core Five Filemanager.',
    long_description=read('README'),
    author='Daniele Tricoli',
    author_email='eriol@mornie.org',
    url='http://mornie.org/projects/django-c5filemanager/',
    packages=find_packages(),
    package_data = {
        'c5filemanager': [
            'locale/*/LC_MESSAGES/*',
        ],
    },
    install_requires = [
        'simplejson>=2.1.0',
        'PIL',
    ],
    classifiers = classifiers,
)
