#!/usr/bin/env python
from setuptools import setup, find_packages
from jenkins_log_parser import __version__


install_requires = [
    'jinja2',
]

setup(
    name='jenkins_log_parser',
    version=__version__,
    author='Tommaso Barbugli',
    author_email='tbarbugli@gmail.com',
    url='http://github.com/tbarbugli/jenkins_log_parser',
    license='BSD',
    packages=find_packages(exclude=("tests",)),
    zip_safe=False,
    install_requires=install_requires,
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'jenkins_log_parser = jenkins_log_parser.main:main',
        ]
    }
)
