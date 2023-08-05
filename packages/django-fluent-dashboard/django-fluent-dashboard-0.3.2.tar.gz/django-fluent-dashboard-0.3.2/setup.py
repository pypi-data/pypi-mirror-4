#!/usr/bin/env python
from setuptools import setup, find_packages
from os.path import dirname, join
import sys, os

# When creating the sdist, make sure the django.mo file also exists:
if 'sdist' in sys.argv:
    try:
        os.chdir('fluent_dashboard')
        from django.core.management.commands.compilemessages import compile_messages
        compile_messages(sys.stderr)
    finally:
        os.chdir('..')


setup(
    name='django-fluent-dashboard',
    version='0.3.2',
    license='Apache License, Version 2.0',

    install_requires=[
        'django-admin-tools>=0.4.1',  # 0.4.1 is the first release with Django 1.3 support.
    ],
    extras_require = {
        'cachestatus': ['dashboardmods>=0.2.2'],
    },

    description='An improved django-admin-tools dashboard for Django projects',
    long_description=open(join(dirname(__file__), 'README.rst')).read(),

    author='Diederik van der Boor',
    author_email='opensource@edoburu.nl',

    url='https://github.com/edoburu/django-fluent-dashboard',
    download_url='https://github.com/edoburu/django-fluent-dashboard/zipball/master',

    packages=find_packages(),
    include_package_data=True,

    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
