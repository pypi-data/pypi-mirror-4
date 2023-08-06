# -*- coding: utf-8 -*-
import os.path
from setuptools import setup

setup(
    name='django-zms-news',
    version='0.1',
    packages = ['news'],
    include_package_data = True,
    license = 'Apache License, Version 2.0', 
    description='Django news with CKEditor integrated.',
    long_description=open('README.md', 'r').read() + open('AUTHORS.md', 'r').read() + open('CHANGELOG.md', 'r').read(),
    url='https://github.com/hisie/django_simple_news',
    author='hisie',
    author_email='dcebrian@serincas.com',
    install_requires=[
        'django-ckeditor', 'easy_thumbnails'
    ],
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
