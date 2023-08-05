#!/usr/bin/env python
from setuptools import setup, find_packages

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules'
]

KEYWORDS = 'passwordly'


setup(name = 'passwordly',
    version = "0.5",
    description = """Simple library for generating passwordly passwords""",
    author = "Josh Yudaken",
    url = "https://github.com/passwordly/passwordly-python",
    packages = find_packages(),
    download_url = "http://pypi.python.org/pypi/passwordly/",
    install_requires=[
      "py-bcrypt>=0.2"
    ],
    classifiers = CLASSIFIERS,
    keywords = KEYWORDS,
    zip_safe = True,
)
