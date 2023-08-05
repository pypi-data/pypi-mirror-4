#!/usr/bin/env python
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


Name = 'ua2.celery'
ProjecUrl = "https://bitbucket.org/ua2web/ua2.celery"
Version = '0.0.1'
Author = 'Vic'
AuthorEmail = 'vic@ua2web.com'
Maintainer = 'Vic'
Summary = 'Extended handlers and helpers worh with celery'
License = 'BSD License'
ShortDescription = Summary
Description = Summary

needed = [
]

EagerResources = [
    'ua2',
]

ProjectScripts = [
]

PackageData = {
    '': ['*.*'],
}

# Make exe versions of the scripts:
EntryPoints = {
}

setup(
    url=ProjecUrl,
    name=Name,
    zip_safe=False,
    version=Version,
    author=Author,
    author_email=AuthorEmail,
    description=ShortDescription,
    long_description=Description,
    license=License,
    scripts=ProjectScripts,
    install_requires=needed,
    include_package_data=True,
    packages=find_packages('src'),
    package_data=PackageData,
    package_dir={'': 'src'},
    eager_resources=EagerResources,
    entry_points=EntryPoints,
    namespace_packages=['ua2'],
)
