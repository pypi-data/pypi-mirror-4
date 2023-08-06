#!/usr/bin/env python

from setuptools import setup, find_packages
 
setup(
    name = 'django-online-status',
    version = '0.1.0',
    packages = find_packages(),    
    author = 'Jakub Zalewski',
    author_email = 'zalew7@gmail.com',    
    description = 'Online status for authenticated users (online, idle, offline) and list of current users online, all to display with templatetags. No database models, everything cached. Read more: http://bitbucket.org/zalew/django-online-status/wiki/Home',
    url='http://bitbucket.org/zalew/django-online-status',    
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)

