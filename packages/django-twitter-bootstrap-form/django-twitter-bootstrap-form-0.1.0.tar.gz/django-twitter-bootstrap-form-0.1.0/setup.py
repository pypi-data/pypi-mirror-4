#!/usr/bin/env python

from setuptools import setup

setup(
    name='django-twitter-bootstrap-form',
    version='0.1.0',
    description='Twitter Bootstrap Form',
    author='Pragmatic Mates',
    author_email='info@pragmaticmates.com',
    maintainer='Pragmatic Mates',
    maintainer_email='info@pragmaticmates.com',
    url='https://github.com/PragmaticMates/django-twitter-bootstrap-form',
    packages=[
        'twitter_bootstrap_form',
        'twitter_bootstrap_form.templatetags'
    ],
    include_package_data=True,
    install_requires=('django'),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Operating System :: OS Independent',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License'],
    license='BSD License')
