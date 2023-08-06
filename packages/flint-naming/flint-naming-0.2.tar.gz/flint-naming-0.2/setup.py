# -*- coding: utf-8 -*-
from __future__ import with_statement
from setuptools import setup


def get_long_description():
    descr = []
    for fname in ('README.rst',):
        with open(fname) as f:
            descr.append(f.read())
    return '\n\n'.join(descr)


setup(
    name='flint-naming',
    version='0.2',
    description="Check PEP-8 naming conventions, plugin for flint",
    long_description=get_long_description(),
    keywords='flint pep8',
    author='Florent Xicluna',
    author_email='florent.xicluna@gmail.com',
    url='https://github.com/flintwork/pep8-naming',
    license='Expat license',
    zip_safe=False,
    install_requires=[
        'setuptools',
        'pep8-naming',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
    ],
)
