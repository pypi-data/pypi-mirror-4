#! /usr/bin/env python

import os
from setuptools import setup, find_packages
import dojo

def read(filename):
    f = open(os.path.join(os.path.dirname(__file__), filename))
    out = f.read()
    f.close()
    return out

setup(
    name="django-dojo",
    version=dojo.__version__,
    description="Add Dojo to your Django projects and run Dojo builds with manage.py commands",
    long_description=read("README"),
    author="Mike Kibbel",
    author_email="mkibbel@gmail.com",
    url="https://github.com/skibblenybbles/django-dojo",
    license="BSD License",
    platforms=["OS Independent"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: Utilities",
    ],
    install_requires=[
        "Django>=1.4"
    ],
    packages=find_packages(exclude=["example", "example.*"]),
    include_package_data=True,
    zip_safe=False,
)
