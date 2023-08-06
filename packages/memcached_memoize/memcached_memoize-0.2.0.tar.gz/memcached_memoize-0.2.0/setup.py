#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from memcached_memoize import __version__

requirements = []
with file('requirements/dependencies.txt', 'r') as f:
    requirements = map(lambda r: r.strip(), f.readlines())

setup(
    name='memcached_memoize',
    version=__version__,
    description="memcached_memoize is decorator to make easy to use Django's cache backends to memoize python functions.",
    long_description="""
memcached_memoize is decorator to make easy to use Django's cache backends to memoize python functions.
""",
    keywords='memcached_memoize',
    author='Jornalismo, TimeHome',
    author_email='jornalismo@corp.globo.com, timehome@corp.globo.com',
    url='http://ngit.globoi.com/memcached_memoize/memcached_memoize',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    include_dirs=['requirements/'],

    packages=find_packages(exclude=['tests', 'requirements']),
    include_package_data=True,
    zip_safe=False,

    install_requires=requirements,
)
