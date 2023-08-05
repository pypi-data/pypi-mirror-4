#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages
from pybb_extensions import VERSION, DEV_STATUS

setup(
    name='pybbm-extensions',
    version='.'.join(map(str, VERSION)),
    description='Extensions for PyBBm forum.',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    keywords='pybbm extensions',
    author='Jakub Zalewski',
    author_email='zalew7@gmail.com',
    url='https://bitbucket.org/zalew/pybbm-extensions',
    license='public domain',
    packages=find_packages(),
    zip_safe=False,
    package_data={
        'readonly': [],
    },
    classifiers=[
        'Development Status :: %s' % DEV_STATUS,
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    install_requires=[
        'django',
        'pybbm',
    ],
)
