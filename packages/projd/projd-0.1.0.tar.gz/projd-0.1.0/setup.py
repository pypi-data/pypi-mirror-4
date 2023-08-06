
import os
from setuptools import setup, find_packages

setup(
    name = 'projd',
    version = '0.1.0',
    license = 'MIT',
    description = 'Utilities for working with projects and applications '
                  'organized within a root directory.',
    long_description = open(os.path.join(os.path.dirname(__file__),
                                         'README.md')).read(),
    keywords = 'python project directory application',
    url = 'https://github.com/todddeluca/projd',
    author = 'Todd Francis DeLuca',
    author_email = 'todddeluca@yahoo.com',
    classifiers = ['License :: OSI Approved :: MIT License',
                   'Development Status :: 3 - Alpha',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.7',
                  ],
    py_modules = ['projd'],
)

