#!/usr/bin/env python

__author__ = 'Jason Corbett'

import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name="slickqa-narc",
    description="A program responsible for responding to Slick events",
    version="1.0" + open("build.txt").read(),
    license="License :: OSI Approved :: Apache Software License",
    long_description=open('README.txt').read(),
    packages=find_packages(exclude=['distribute_setup']),
    package_data={'': ['*.txt', '*.rst', '*.html']},
    include_package_data=True,
    install_requires=['slickqa>=2.0.14', 'kombu>=2.5.4', 'Jinja2>=2.6', 'pygal>=0.13.0', 'CairoSVG>=0.5', 'tinycss>=0.3', 'cssselect>=0.7.1', 'amqp>=1.0.6', 'anyjson>=0.3.3'],
    author="Slick Developers",
    url="http://code.google.com/p/slickqa",
    entry_points={
        'console_scripts': ['narc = narc.main:main', 'narcctl = narc.main:ctlmain'],
        'narc.response' : ['emailresponder = narc.plugins.email:EmailResponder',
                           'shutdownrestart = narc.plugins.internal:ShutdownRestartPlugin']
    }
)
