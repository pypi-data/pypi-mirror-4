#!/usr/bin/env python

import bluevia

from setuptools import setup, find_packages


setup(
    name=bluevia.__title__,
    version=bluevia.__version__,
    description='A Python wrapper around the BlueVia API.',
    long_description=open('README.rst').read(),  # + '\n\n' + open('HISTORY.rst').read(),
    author=bluevia.__author__,
    author_email=bluevia.__email__,
    url='https://pybluevia.readthedocs.org/',
    keywords='bluevia api sms mms',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['requests>=1.0.0'],
    license=open('LICENSE').read(),
    zip_safe=False,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries'
    ),
)
