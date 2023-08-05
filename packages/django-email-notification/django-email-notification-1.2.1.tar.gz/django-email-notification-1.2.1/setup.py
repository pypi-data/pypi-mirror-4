#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from distutils.core import setup

root_dir = os.path.abspath(os.path.dirname(__file__))

def get_version():
    version_re = re.compile(r"^__version__ = '([\w_.]+)'$")
    with open(os.path.join(root_dir, 'notification', '__init__.py')) as f:
        for line in f:
            match = version_re.match(line[:-1])
            if match:
                return match.groups()[0]
    return '0.0.1'


setup(name = "django-email-notification",
    version = get_version(),
    description = "django-email-notification allows backoffice users to send short email notifications to django registered users or users you only know the email about what is new or changed from django's admin or a dedicated view. And then track their clicks.",
    author = "Richard Moch",
    author_email = "richard@rootsaka.com",
    url = "http://bitbucket.org/rmoch/django-email-notification",
    packages = ['notification'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Utilities'
      ])
