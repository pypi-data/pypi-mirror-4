from __future__ import with_statement

import os.path
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from typequery import (__version__ as version, __license__ as license,
                       __author__ as author, __email__ as author_email)


def readme():
    try:
        with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
            return f.read()
    except (IOError, OSError):
        return ''


setup(
    name='TypeQuery',
    py_modules=['typequery', 'typequery_tests'],
    version=version,
    description='A simple and dirty way to define generic methods to existing '
                'types.',
    long_description=readme(),
    license=license,
    author=author,
    author_email=author_email,
    maintainer=author,
    maintainer_email=author_email,
    url='https://bitbucket.org/dahlia/typequery',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: Jython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: Stackless'
    ]
)
