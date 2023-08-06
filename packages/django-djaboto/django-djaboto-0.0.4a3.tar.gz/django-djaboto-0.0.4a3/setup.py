#!/usr/bin/env python2
from setuptools import setup, find_packages
import os

version = __import__('djaboto').get_version()

install_requires = [
    'setuptools',
    'Django>=1.4',
    'fabric',
    'boto',
    'GitPython',
]

dependency_links = [
    ]

setup(
    name = "django-djaboto",
    version = version,
    url = 'https://bitbucket.org/oddotterco/django-djaboto',
    license = 'BSD',
    platforms=['Linux'],
    description = "A Django app and assorted tools to help create, deploy and manage Django projects on AWS servers",
    keywords='django, cms, amazon',
    author = "Odd Otter Co",
    author_email = 'djaboto@oddotter.com',
    packages = find_packages(),
    install_requires = install_requires,
    dependency_links = dependency_links,
    include_package_data = True,
    zip_safe = False,
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    package_dir = {
        'djaboto': 'djaboto',
    },
    entry_points = {
        'console_scripts': [
            'soupstart = djaboto.management.commands.checkmix:execute',
            ],
        },
)
