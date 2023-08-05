"""
Balanced ACH client library.
"""
import os
import re

try:
    import setuptools
except ImportError:
    import distutils.core
    setup = distutils.core.setup
else:
    setup = setuptools.setup

setup(
    name='balanced-ach',
    version=(
        re
        .compile(r".*__version__ = '(.*?)'", re.S)
        .match(open('balanced_ach.py').read())
        .group(1)
    ),
    url='https://github.com/balanced/balanced-ach-python',
    license='BSD',
    author='Balanced',
    author_email='dev@balancedpayments.com',
    description='Balanced ACH client library',
    long_description=(
        open('README.rst').read()
    ),
    py_modules=['balanced_ach'],
    tests_require=[
        'nose ==1.1.2',
        'mock ==0.8',
        'unittest2 >=0.5.1',
    ],
    install_requires=[
        'iso8601 >=0.1.4',
        'simplejson >=2.3.2',
        'wac >=0.11',
    ],
    test_suite='nose.collector',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
