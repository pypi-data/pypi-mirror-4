#!/usr/bin/env python

from distutils.core import setup


setup(name="django-bland",
    version="0.1.0",
    description="A terribly basic file based CMS for django",
    author="Adam Sven Johnson",
    author_email="adam@pkqk.net",
    url="https://github.com/pkqk/django-bland",
    license='MIT',
    packages=["bland"],
    package_data={
        "bland": ['templates/bland/*.html', 'static/bland/*.css']
    },
    requires=[
        'Django',
        'pyyaml',
        'markdown'
    ]
)
