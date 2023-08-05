#! /usr/bin/env python

from setuptools import setup

setup(
    name='mdx_smartypants',
    version='1.2',
    author='Jonathan Eunice',
    author_email='jonathan.eunice@gmail.com',
    description='Python-Markdown extension using smartypants to emit typographically nicer ("curly") quotes, proper ("em" and "en") dashes, etc.',
    long_description=open('README.rst').read(),
    url='http://bitbucket.org/jeunice/mdx_smartypants',
    py_modules=['mdx_smartypants', 'spants'],
    install_requires=['Markdown>=2.0','namedentities>=1.2'],
    tests_require = ['tox', 'pytest'],
    zip_safe = True,
    keywords='markdown smartypants extension curly quotes typographic',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Markup',
        'Topic :: Text Processing :: Markup :: HTML'
    ]
)
