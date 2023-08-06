#!/usr/bin/env python

from distutils.core import setup

setup(
    name='django-dispose',
    description='Disposes of media files that are no longer referenced in the database.',
    version='1.0',
    author='Daniel Hawkes',
    author_email='dan@danhawkes.co.uk',
    license='MIT',
    url='https://bitbucket.org/danhawkes/django-dispose',
    packages=[
        'django_dispose',
        'django_dispose.management',
        'django_dispose.management.commands'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: System :: Installation/Setup'
    ]
)
