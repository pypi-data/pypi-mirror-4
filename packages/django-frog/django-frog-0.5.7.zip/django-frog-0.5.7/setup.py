#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='django-frog',
    description='Media server built on django',
    long_description='A server and client solution to viewing and filtering large image and video collections',
    version='0.5.7',
    author='Brett Dixon',
    author_email='theiviaxx@gmail.com',
    license='MIT',
    url='https://github.com/theiviaxx/frog',
    platforms='any',
    packages=[
        'frog',
        'frog.management',
        'frog.management.commands',
        'frog.templatetags',
        ],
    package_data={
        'frog': [
        	'templates/frog/*',
        	'fixtures/*',
        	'video.json',
        	'README.md',
        	'static/j/*.js',
        	'static/j/libs/*.js',
        	'static/i/*.png',
        	'static/c/*.css'
        ],
    },
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
    ],
    zip_safe=False,
    include_package_data=True
)