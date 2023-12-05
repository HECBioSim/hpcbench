#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


extra_files = package_files('chromatin')
extra_files = list(filter(lambda x: ".py" not in x, extra_files))

setup(
    name='hpcbench',
    description='System preparation, logging and analysis tools for hpc '
    'benchmarking',
    author='Rob Welch',
    author_email='robert.welch@stfc.ac.uk',
    license='AGPLv3',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    package_data={'extra': extra_files},
    zip_safe=False,
    entry_points={
        'console_scripts': ['hpcbench=hpcbench.hpcbench:entry_point'],
    }
)
