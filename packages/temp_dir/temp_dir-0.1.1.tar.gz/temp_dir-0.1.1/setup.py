#!/usr/bin/env python
# coding: utf8

from setuptools import setup


setup(
    name='temp_dir',
    version='0.1.1',

    description='Execute block of code within a temporary directory',
    long_description=open('README.txt').read(),

    author='Krisztián Fekete',
    author_email='fkr972+temp_dir@gmail.com',
    url='https://github.com/krisztianfekete/temp_dir',

    py_modules=['temp_dir', 'test_temp_dir'],
    license='MIT License',

    classifiers=[
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Testing',
        ]
    )
