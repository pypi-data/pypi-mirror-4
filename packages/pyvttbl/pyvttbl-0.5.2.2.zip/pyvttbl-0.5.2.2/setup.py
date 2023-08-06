# Copyright (c) 2011, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.

##from distutils.core import setup
from setuptools import setup

import glob
data_file_list = [f for f in glob.glob('pyvttbl/tests/data/*')]

setup(name='pyvttbl',
    version='0.5.2.2',
    description='Multidimensional pivot tables, data processing, statistical computation',
    author='Roger Lew',
    author_email='rogerlew@gmail.com',
    license = "BSD",
    classifiers=["Development Status :: 5 - Production/Stable",
                 "Intended Audience :: Developers",
                 "Intended Audience :: Information Technology",
                 "Intended Audience :: Science/Research",
                 "License :: OSI Approved :: BSD License",
                 "Natural Language :: English",
                 "Programming Language :: Python :: 2.7",
                 "Topic :: Database",
                 "Topic :: Database :: Database Engines/Servers",
                 "Topic :: Scientific/Engineering :: Information Analysis",
                 "Topic :: Scientific/Engineering :: Mathematics",
                 "Topic :: Software Development :: Libraries :: Python Modules"],
    url='http://code.google.com/p/pyvttbl/',
    packages=['pyvttbl',
              'pyvttbl.examples',
              'pyvttbl.misc',
              'pyvttbl.plotting',
              'pyvttbl.stats',
              'pyvttbl.tests',
              'pyvttbl.tools'],
    install_requires = ['dictset','pystaggrelite3'],
    zip_safe=False,
    data_files=[('pyvttbl/tests/data', data_file_list),
                ('pyvttbl/tests/output' ,['pyvttbl/tests/output/empty.txt'])])

"""C:\Python27\python.exe setup.py sdist upload --identity="Roger Lew" --sign"""
