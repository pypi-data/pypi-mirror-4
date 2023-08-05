#!/usr/bin/env python

from setuptools import setup

setup(
    name='python-netflix',
    version='0.4.1',
    install_requires=['requests>=0.13.0', 'simplejson'],
    author='Mike Helmick',
    author_email='mikehelmick@me.com',
    license='MIT License',
    url='https://github.com/michaelhelmick/python-netflix/',
    keywords='python netflix oauth api',
    description='A Python Library to interface with Netflix REST API & OAuth',
    long_description=open('README.rst').read(),
    download_url="https://github.com/michaelhelmick/python-netflix/zipball/master",
    py_modules=["netflix"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',
        'Topic :: Internet'
    ]
)
