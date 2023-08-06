#!/usr/bin/env python
# -*- coding:utf-8 -*-
# This Python file uses the following encoding: utf-8


from setuptools import setup, find_packages
from glob import glob
import os

# strings
lib_path = '/usr/share/raid_guard'

# Get description from Readme file
readme_file = os.path.join(os.path.dirname(__file__), 'README.rst')
long_description = open(readme_file).read()

setup(  
    name='raid-guard',
    version='0.1.3',
    description='raid hard disc monitoring daemon for linux servers',
    long_description=long_description,
    author='Andreas Fritz',
    author_email='raid_guard@bitzeit.eu',
    url='http://www.sources.e-blue.eu/',
    download_url='https://pypi.python.org/pypi',
    packages = find_packages(),
    entry_points={'console_scripts':['raid_guard=raid_guard:main'],},
    include_package_data=True,
    data_files=[
                (lib_path, glob('raid_guard.ini')),
                (lib_path, glob('README.rst')),
                (lib_path, glob('LICENSE')),
                ],
    keywords="raid hard-disk server monitoring daemon",
    classifiers=[
                'Development Status :: 3 - Alpha',
                'License :: OSI Approved :: MIT License',
                'Operating System :: Unix',
                'Programming Language :: Python :: 2.7',
                'Environment :: Console',
                'Natural Language :: English',
                'Intended Audience :: System Administrators',
                'Topic :: System :: Networking :: Monitoring',
                'Topic :: System :: Networking :: Monitoring :: Hardware Watchdog',
                'Topic :: System :: Systems Administration',
                ],
    install_requires = ['deiman','iniparse'],
    )
