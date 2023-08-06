===========
django-djaboto
===========

A django application with assorted tools to help create and manage Django CMS projects and to then deploy
them on AWS Ubuntu servers.  Additional OS targets may be added later.

Django-djaboto heavily relies upon the AWS Python module Boto, and really only wraps it in a django command set for consistency.

Dependencies
============

- boto>=2.4.1
- Fabric>=1.4.2
- Django>=1.4

Changelog
=========
0.0.6a2 - Sorted the output of the 'cmsplugins' command
          Added 'cmsplugins' command to list all installed django-cms plugins
0.0.5a1 - Added support for initial update to an existing instance with pre-existing sites.
