#!/usr/bin/env python

from distutils.core import setup

import specbar


setup(
    name='python-specbar',
    version=specbar.__version__,
    description='Simple module to build a statusbar for spectrwm.',
    long_description=open('README.rst').read(),
    author=specbar.__author__,
    author_email='weimann@ymail.com',
    url='https://bitbucket.org/whitie/python-specbar',
    py_modules=['specbar'],
    scripts=['specbar.py'],
    license=specbar.__license__,
    platforms='posix',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: X11 Applications',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Topic :: Desktop Environment :: Window Managers',
        'Topic :: Utilities',
    ],
)
