# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

pkg_name = 'radpress'
version = __import__(pkg_name).__version__

# get requires from requirements/global.txt file.
requires_file_name = os.path.join(
    os.path.dirname(__file__), 'requirements', 'global.txt')
with file(requires_file_name) as install_requires:
    install_requires = map(lambda x: x.strip(), install_requires.readlines())

setup(
    name=pkg_name,
    version=version,
    description='Simple reusable blog application',
    author=u'Gökmen Görgen',
    author_email='gokmen@radity.com',
    license='GPLv3',
    url='https://github.com/gkmngrgn/radpress',
    packages=find_packages(exclude=['venv', 'demo', 'docs']),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
        "Environment :: Web Environment"
    ]
)
