#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'pyassert',
          version = '0.2.4',
          description = 'Rich assertions library for Python',
          long_description = '''
pyassert is an assertion library for the Python programming language.

Introduction
------------

Assertions are used in automated tests to verify that a given piece of code behaves as expected. pyassert aims to provide assertions with provide

* **rich functionality**: common assertions should be expressed easily
* **good readability**: assertions should be easy to read and easy to understand to enhance the overall understandability of the test
* **independent of the test framework**: pyassert assertions work with every Python test environment.

How to install it?
``````````````````

pyassert is available via the [Cheeseshop](http://pypi.python.org/pypi/pyassert/) so you can use easy_install or pip:

    $ pip install pyassert


Links
`````

* pyassert Github repository including documentation <https://github.com/pyclectic/pyassert>
''',
          author = "Alexander Metzner, Michael Gruber",
          author_email = "halimath.wilanthaou@gmail.com, aelgru@gmail.com",
          license = 'Apache Software License',
          url = 'https://github.com/pyclectic/pyassert',
          scripts = [],
          packages = ['pyassert'],
          classifiers = ['Development Status :: 4 - Beta', 'Environment :: Other Environment', 'Intended Audience :: Developers', 'License :: OSI Approved :: Apache Software License', 'Programming Language :: Python', 'Programming Language :: Python :: 2.6', 'Programming Language :: Python :: 2.7', 'Programming Language :: Python :: 3.2', 'Topic :: Software Development :: Quality Assurance', 'Topic :: Software Development :: Testing'],
          
          
          
          
          zip_safe=True
    )
