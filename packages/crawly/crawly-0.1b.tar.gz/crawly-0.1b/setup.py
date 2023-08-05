#!/usr/bin/env python
"setup installation script."
import os

from setuptools import setup

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='crawly',
    license='BSD',
    version="0.1b",
    author='Mouad Benchchaoui',
    url='https://bitbucket.org/mouad/crawly',
    author_email='moaudino@gmail.com',
    description='A micro python crawler/scraper library',
    long_description='\n' + read('README.rst') + '\n\n' + read('HISTORY.rst'),
    install_requires=[
        'gevent==0.13.7',
        'requests==0.14',
        'lxml==3.0.1'
    ],
    py_modules=['crawly'],
    zip_safe=True,
    package_data={'': ['*.rst']},
    platforms='any',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP','Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ]
)
