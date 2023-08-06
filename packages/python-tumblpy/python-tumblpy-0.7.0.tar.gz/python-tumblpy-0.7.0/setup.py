#!/usr/bin/env python

from setuptools import setup

setup(
    name='python-tumblpy',
    version='0.7.0',
    install_requires=['requests>=1.0.4,<1.1.0', 'simplejson', 'requests_oauthlib'],
    author='Mike Helmick',
    author_email='mikehelmick@me.com',
    license='MIT License',
    url='https://github.com/michaelhelmick/python-tumblpy/',
    keywords='python tumblpy tumblr oauth api',
    description='A Python Library to interface with Tumblr v2 REST API & OAuth',
    long_description=open('README.rst').read(),
    download_url="https://github.com/michaelhelmick/python-tumblpy/zipball/master",
    py_modules=["tumblpy"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',
        'Topic :: Internet'
    ],
    dependency_links=[
        'https://github.com/requests/requests-oauthlib/tarball/master#egg=requests_oauthlib-0.2.0'
    ],
)
