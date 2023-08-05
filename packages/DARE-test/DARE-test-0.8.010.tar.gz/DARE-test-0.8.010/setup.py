#!/usr/bin/env python

from setuptools import setup, find_packages
import distribute_setup
distribute_setup.use_setuptools()
import dare


setup(name='DARE-test',
    version=dare.__version__,
    description='Dynamic Application Runtime Environment',
    author='Sharath Maddineni',
    author_email='smaddineni@cct.lsu.edu',
    maintainer="Sharath Maddineni",
    maintainer_email="smaddineni@cct.lsu.edu",
    url='https://github.com/saga-project/DARE',
    license="MIT",
    packages=find_packages(),
    package_data={'dare': ['daredb/*'], '': ['*.conf']},
    install_requires=['bigjob'],
    entry_points={'console_scripts': ['dare-run = dare.bin.darerun:main']})
