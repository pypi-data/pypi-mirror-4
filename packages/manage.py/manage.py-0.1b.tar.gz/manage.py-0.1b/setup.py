# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from manage import __version__


setup(
    name='manage.py',
    version=__version__,
    description='Human friendly CLI builder',
    long_description='',
    author='jean-philippe serafin',
    author_email='jps@birdback.com',
    url='https://github.com/Birdback/manage.py',
    packages=find_packages(),
    install_requires=['clint'],
    entry_points={
        'console_scripts': [
            'manage = manage.main:main',
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
