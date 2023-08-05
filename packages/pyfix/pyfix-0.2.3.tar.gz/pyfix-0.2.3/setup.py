#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'pyfix',
          version = '0.2.3',
          description = 'A framework for writing automated software tests (non xUnit based)',
          long_description = '''
pyfix
-----

pyfix is a framework for writing and executing automated tests including unittests, integration tests or acceptance
tests. pyfix provides capabilities similar to other tools (such as unittest) but does not follow the xUnit semantics
to write tests.

pyfix Principals
````````````````

pyfix aims to make tests easy to read and understand while it encourages the use of accepted software design principles
such as favor composition over inheritance. pyfix also tries to reduce the amount of syntactic "waste" that some other
frameworks suffer from (i.e. putting self in front of almost everything).

Links
`````
* pyfix Github repository <https://github.com/pyclectic/pyfix>
''',
          author = "Alexander Metzner",
          author_email = "halimath.wilanthaou@gmail.com",
          license = 'Apache Software License',
          url = 'https://github.com/pyclectic/pyfix',
          scripts = [],
          packages = ['pyfix', 'pyfix.fixtures'],
          classifiers = ['Development Status :: 4 - Beta', 'Environment :: Other Environment', 'Intended Audience :: Developers', 'License :: OSI Approved :: Apache Software License', 'Programming Language :: Python', 'Programming Language :: Python :: 2.6', 'Programming Language :: Python :: 2.7', 'Programming Language :: Python :: 3.2', 'Topic :: Software Development :: Quality Assurance', 'Topic :: Software Development :: Testing'],
          
          
          install_requires = [ "pyassert" ],
          
          zip_safe=True
    )
