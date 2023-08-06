#!/usr/bin/env python2
from setuptools import setup, find_packages
import os

try:
    from setuptest import test
except ImportError:
    from setuptools.command.test import test


version = __import__('djaboto').get_version()

def read(fname):
    # read the contents of a text file
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django-djaboto",
    version = version,
    url = 'https://bitbucket.org/oddotterco/django-djaboto',
    license = 'BSD',
    platforms=['OS Independent'],
    description = "A Django app and assorted tools to help create, deploy and manage Django projects on AWS servers",
    long_description = read('README.rst'),
    keywords='django, cms, amazon',
    author = "Odd Otter Co",
    author_email = 'djaboto@oddotter.com',
    packages = find_packages(),
    install_requires = (
            'setuptools',
            'Django>=1.4',
            'fabric',
            'boto',
            'GitPython',
    ),
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
