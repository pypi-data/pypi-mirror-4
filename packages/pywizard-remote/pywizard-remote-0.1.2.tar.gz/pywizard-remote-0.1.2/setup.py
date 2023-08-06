import os
from setuptools import setup

setup(
    name='pywizard-remote',
    version='0.1.2',
    packages=[
        'pywizard_remote',
    ],
    url='',
    license='MIT',
    author='Alex Rudakov',
    author_email='ribozz@gmail.com',
    description='Remote controll for pywizard.',
    long_description=open('README.md').read(),
    install_requires=[
        'pywizard',
    ]
)
