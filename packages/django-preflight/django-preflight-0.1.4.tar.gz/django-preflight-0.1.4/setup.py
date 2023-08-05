# -*- encoding: utf-8 -*-
# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).
try:
    from ast import PyCF_ONLY_AST
except ImportError:
    PyCF_ONLY_AST = 1024

from setuptools import setup


def get_version():
    return [compile(line, '', 'exec', PyCF_ONLY_AST).body[0].value.s
            for line in open('preflight/__init__.py')
            if line.startswith('__version__')][0]


setup(
    name='django-preflight',
    version=get_version(),
    author=u'Łukasz Czyżykowski',
    author_email='lukasz.czyzykowski@canonical.com',
    description="Create a page for making sure all settings are correct.",
    long_description=open('README').read(),
    url='https://launchpad.net/django-preflight',
    download_url='https://launchpad.net/django-preflight/+download',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Software Development :: Quality Assurance",
    ],
    license='AGPL-3',
    packages=(
        'preflight',
        'preflight.management',
        'preflight.management.commands',
    ),
    package_data={
        'preflight': ['templates/preflight/*.html'],
    },
    install_requires=[
        'django >= 1.0'
    ],
    tests_require=[
        'mock > 0.6'
    ],
    extras_require={
        'docs': ['Sphinx'],
    },
    test_suite='example_project.run.tests',
)
