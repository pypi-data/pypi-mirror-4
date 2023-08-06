#!/usr/bin/env python

from distutils.core import setup

setup(
    name='django-vingd',
    version='0.1.1',
    description='Django App for Vingd integration',
    long_description=open('README.rst').read(),
    author='Marin Prcela',
    author_email='marin.prcela@vingd.com',
    url='https://github.com/vingd/django-vingd',
    packages=['django_vingd'],
    install_requires=[i.strip() for i in open('requirements.txt').readlines()],
    platforms=['OS Independent'],
    license='MIT',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
    )
)
