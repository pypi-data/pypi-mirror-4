#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is part of the charset python package
Copyrighted by Karel Vedecia Ortiz <kverdecia@uci.cu, kverdecia@gmail.com>
License: LGPLv3 (http://www.gnu.org/licenses/lgpl.html)
"""
__author__ = "Karel Antonio Verdecia Ortiz"
__contact__ = "kverdecia@uci.cu"


from setuptools import setup, find_packages
from distutils.extension import Extension

# setuptools DWIM monkey-patch madness
# http://mail.python.org/pipermail/distutils-sig/2007-September/thread.html#8204
import sys, os, glob
if 'setuptools.extension' in sys.modules:
    m = sys.modules['setuptools.extension']
    m.Extension.__dict__ = m._Extension.__dict__


detector_src = ['src/detector.pyx']
detector_src.extend(glob.glob('src/mozilladetector/*.cpp'))
    
    
version = '1.0'

setup(name='charset',
    version=version,
    description="Clases for charset detection. Uses chardet and mozilla universal charset detection.",
    long_description="""\
""",
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Karel Antonio Verdecia Ortiz',
    author_email='kverdecia@uci.cu, kverdecia@gmail.com',
    url='',
    license='LGPL3',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points = {
        'console_scripts': [
            'charset=charset.cmd:CmdCharset.run',
        ],
        'charset.detectors': [
            'chardet=charset.detector:Detector',
            'mozilla=charset.detector:MozDetector',
            'check=charset.detector:CheckDetector',
        ],
    },
    setup_requires=['setuptools_cython',],
    ext_modules=[
        Extension('charset.detector', detector_src, 
            include_dirs=['src/mozilladetector'], language='c++'),
    ],
    
)
