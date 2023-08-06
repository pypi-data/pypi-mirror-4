#!/usr/bin/env python

from setuptools import setup

setup(
    name='bauhattan',
    version='0.1.0',
    packages=['bauhattan',],
    license='MIT License',
    long_description=open('README.md').read(),
    author='izrik',
    author_email='izrik@yahoo.com',
    url='https://github.com/izrik/bauhattan',
    description='Automated CI/CD Tool',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
    install_requires=[
        'requests',
    ],
)
