#!/usr/bin/env python2
from setuptools import setup, find_packages
import os

version = __import__('chameleon').get_version()

install_requires = [
    'Django>=1.4',
    'django-cms>=2.3.5',
    'django-less',
]

dependency_links = [
    ]

setup(
    name = "django-chameleon",
    version = version,
    url = 'https://bitbucket.org/oddotterco/django-chameleon',
    license = 'BSD',
    platforms=['Linux'],
    description = "A Django app that will create a pluggable django-cms theme app within your project.",
    keywords='django, cms, theme',
    author = "Odd Otter Co",
    author_email = 'chameleon@oddotter.com',
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
        'chameleon': 'chameleon',
    },

    entry_points = {
        'console_scripts': [
            'purifyhtml = chameleon.management.commands.purifyhtml:execute',
        ],
    },
)
