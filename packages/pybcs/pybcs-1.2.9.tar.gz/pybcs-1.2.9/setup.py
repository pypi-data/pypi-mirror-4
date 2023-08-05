#!/usr/bin/env python
from setuptools import setup
import sys
import platform

__VERSION__ = "1.2.9" 

requires = ['simplejson']
if sys.version_info < (2,7):
    requires.append('argparse')

scripts = ['tools/bcsh.py', ]

#if sys.platform.startswith('win'):
#    scripts += [
#        'bin/bcsh.bat'
#    ]

setup(
    name = "pybcs",
    version = __VERSION__,
    url = 'http://yun.baidu.com/',
    author = 'ning',
    author_email = 'idning@gmail.com',
    description = "bcs python sdk",
    #long_description=open('README.md').read(),
    packages = ['pybcs'],
    include_package_data = True,
    install_requires = requires,
    scripts = scripts,
    classifiers = ['Development Status :: 5 - Production/Stable',
                   'Environment :: Console',
                   'License :: OSI Approved :: GNU Affero General Public License v3',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   ],
)

