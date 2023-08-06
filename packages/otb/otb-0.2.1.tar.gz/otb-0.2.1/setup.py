# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name='otb',
    version='0.2.1',
    author='François Orieux',
    author_email='orieux@iap.fr',
    packages=['otb'],
    scripts=[],
    url='http://bitbucket.org/forieux/otb/',
    license='LICENSE.txt',
    description='Orieux toolbox. Utility functions for scientific numerical computation.',
    long_description=open('README.rst').read(),
    install_requires=[
        "numpy >= 1.4",
        "matplotlib >= 1.1",
        "anfft",
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries',
    ],
)
