#!/usr/bin/env python2
from setuptools import setup, find_packages

version = __import__('{{ app_name }}').get_version()

install_requires = [
    'Django>=1.4',
    'django-cms>=2.3.5',
    'django-less',
]

dependency_links = [
]

setup(
    name = "{{ app_name }}",
    version = version,
    url = 'http://github.com/growlf/django-chameleon',
    license = 'BSD',
    platforms=['Linux'],
    description = "A Django pluggable theme app.",
    keywords='django, cms, theme',
    author = "Odd Otter Co",
    author_email = 'chameleon@oddotter.com',
    packages = find_packages(),
    install_requires = install_requires,
    dependency_links = dependency_links,
    include_package_data = True,
    zip_safe = False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    package_dir = {
        '{{ app_name }}': '{{ app_name }}',
    },
)
