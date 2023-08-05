#!/usr/bin/env python

from setuptools import setup, find_packages


with open('README.rst') as file:
    long_description = file.read()


setup(
    name='django-giza',
    version="0.1.5",
    author='Anentropic',
    author_email='ego@anentropic.com',
    license='LICENSE.txt',
    description="Autodoc all modules from a Django project's INSTALLED_APPS for Sphinx",
    long_description=long_description,
    url='https://github.com/anentropic/giza',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        "Framework :: Django",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
    ],
)
