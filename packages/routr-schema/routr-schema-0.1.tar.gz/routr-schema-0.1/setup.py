from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
    name='routr-schema',
    version=version,
    description='Common guards for routr to validate request',
    author='Andrey Popp',
    author_email='8mayday@gmail.com',
    url='http://routr.readthedocs.org/',
    license='BSD',
    py_modules=['routrschema'],
    install_requires=[
        'routr >= 0.6',
        'schemify >= 0.1',
    ],
    include_package_data=True,
    zip_safe=False)
