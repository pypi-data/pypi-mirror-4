# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

# The version of the wrapped library is the starting point for the
# version number of the python package.
# In bugfix releases of the python package, add a '-' suffix and an
# incrementing integer.
# For example, a packaging bugfix release version 1.4.4 of the
# js.jquery package would be version 1.4.4-1 .

version = '0.5.1'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.rst')
    + '\n' +
    read('js', 'graphael', 'test_graphael.txt')
    + '\n' +
    read('CHANGES.rst'))

setup(
    name='js.graphael',
    version=version,
    description=u"Fanstatic packaging of gRaphaël",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='gocept Developers',
    author_email='mail@gocept.com',
    license='BSD',
    packages=find_packages(),namespace_packages=['js'],
    include_package_data=True,
    url='https://bitbucket.org/gocept/js.graphael',
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'js.raphael',
        'setuptools',
        ],
    entry_points={
        'fanstatic.libraries': [
            'graphael = js.graphael:library',
            ],
        },
    )
