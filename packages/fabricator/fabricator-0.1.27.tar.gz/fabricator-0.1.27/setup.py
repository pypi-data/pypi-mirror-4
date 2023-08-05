# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

VERSION = (0, 1, 27)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))

setup(
    name='fabricator',
    version=__versionstr__,
    description="Multi user configuration and default fabric targets for you python project",
    author='SevenQuark',
    author_email='info@sevenquark.com',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    license='MIT license',
    url='https://github.com/SevenQuark/fabricator',
#    long_description = open('README.rst').read(),
    requires=['Fabric (>= 1.4)'],

    classifiers=(
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
)
