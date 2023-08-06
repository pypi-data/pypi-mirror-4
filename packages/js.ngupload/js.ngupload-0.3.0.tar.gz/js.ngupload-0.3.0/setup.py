# -*- coding: utf-8 -*-

import os

from setuptools import find_packages
from setuptools import setup

version = '0.3.0'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


long_description = read('README.rst') + '\n' + \
    read('js', 'ngupload', 'test_ngupload.txt') + '\n' + \
    read('CHANGES.txt')


setup(
    name='js.ngupload',
    version=version,
    description='Fanstatic packaging of ngUpload',
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
    ],
    keywords='Fanstatic ngUpload',
    author='Andreas Kaiser',
    author_email='disko@binary-punks.com',
    url='https://github.com/disko/js.ngupload',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'js.angular'
        'setuptools',
    ],
    entry_points={
        'fanstatic.libraries': [
            'ngupload = js.ngupload:library'
        ]
    },
)
