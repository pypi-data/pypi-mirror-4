#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The Screen class lets you to do positioned writes to the dos terminal.
The Screen class also allows you to specify the colors for foreground and
background, to the extent the dos terminal allows.
"""

classifiers = """\
Development Status :: 3 - Alpha
Environment :: Win32 (MS Windows)
Intended Audience :: Developers
License :: OSI Approved :: BSD License
Operating System :: Microsoft :: MS-DOS
Programming Language :: Python
Topic :: Software Development :: Libraries
Topic :: System :: Shells
Topic :: Terminals
"""

from distutils.core import setup

doclines = __doc__.split('\n')

setup(
    name='dosbox-screen',
    version='0.0.2',
    requires=['ctypes', 'colorama'],
    install_requires=['ctypes', 'colorama'],
    description=doclines[0],
    classifiers=[line for line in classifiers.split('\n') if line],
    long_description=' '.join(doclines),
    license="BSD",
    #platform='win32',
    author='Bjorn Pettersen',
    author_email='bjorn@tkbe.org',
    url='https://github.com/thebjorn/doscmd-screen',
    download_url='https://github.com/thebjorn/doscmd-screen',
    py_modules=['screen']
)
