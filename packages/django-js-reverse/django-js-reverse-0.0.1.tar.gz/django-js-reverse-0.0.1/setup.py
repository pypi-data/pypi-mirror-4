#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup


version_tuple = __import__('js_reverse').VERSION
version = '.'.join([str(v) for v in version_tuple])

setup(
    name='django-js-reverse',
    version=version,
    license='MIT',
    description='Javascript url handling for Django that doesn\'t hurt.',
    author='Bernhard Janetzki',
    author_email='boerni@gmail.com',
    url='https://github.com/version2/django-js-reverse',
    download_url='http://pypi.python.org/pypi/django-js-reverse/',
    packages=['js_reverse'],
)