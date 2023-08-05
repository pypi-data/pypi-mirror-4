#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys,os

if sys.version_info[0]==2:
	other_version = 3
else:
	other_version = 2


readme = changes = ''
if os.path.exists('README.rst'):
	readme = open('README.rst').read()
	changes = open('CHANGES.rst').read()

VERSION = '0.1.2'

SHORT_DESC = "Create simple yet powerful WSGI based sites, utilizing Jinja2 and Qt's TS-file format for localization"
PACKAGES = find_packages('src')

setup(
    name='pysite',
    packages=PACKAGES,
    package_dir={'':'src'},
    version=VERSION,
    description=SHORT_DESC,
    long_description='\n\n'.join([readme, changes]),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',       
    ],
    keywords= ['wsgi', 'website', 'www', 'website', 'framework'],
    author='Jakob Simon-Gaarde',
    author_email='jakob@simon-gaarde.dk',
    maintainer = 'Jakob Simon-Gaarde',
    maintainer_email = 'jakob@simon-gaarde.dk',
    install_requires=['jinja2'],
    requires=['jinja2'],
    provides=['pysite'],
    license='LGPL3',
    scripts=['scripts/pysite'],
    zip_safe=False
)
