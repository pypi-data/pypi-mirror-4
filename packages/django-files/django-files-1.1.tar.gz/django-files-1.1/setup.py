#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name = "django-files",
    version = "1.1",
    description = "Django attachments ContentTypes micro framework.",
    long_description = "Attachments framework based on ContentTypes and the django.contrib.comments system.",
    keywords = "django file attachment upload storage",
    license = open("LICENSE.md").read(),
    author = "Rolf Håvard Blindheim",
    author_email = "rhblind@gmail.com",
    url = "https://github.com/rhblind/django-files",
    install_requires = [
        "django",
        "django-braces"
    ],
    packages = [
        "files",
        "files.management",
        "files.templatetags"
    ],
    package_data = {
        "files": [
            "static/css/*.css",
            "static/images/*.png",
            "static/javascripts/*.js",
            "templates/attachments/*.html",
        ]
    },
    classifiers = [
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
