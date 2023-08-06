#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Thu 20 Sep 2012 14:43:19 CEST 

"""Bindings for flandmark
"""

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires='xbob.extension'))
from xbob.extension import Extension, build_ext

setup(

    name="xbob.flandmark",
    version="1.0.8",
    description="Python bindings to the flandmark keypoint localization library",
    license="GPLv3",
    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',
    long_description=open('README.rst').read(),
    url='http://pypi.python.org/pypi/xbob.flandmark',

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    namespace_packages=[
      "xbob",
      ],

    setup_requires=[
      'xbob.extension',
      ],

    install_requires=[
      'setuptools',
      'bob',
      ],

    entry_points = {
      'console_scripts': [
        'annotate.py = xbob.flandmark.script.annotate:main',
        ],
      },

    cmdclass={
      'build_ext': build_ext,
      },

    ext_modules=[
      Extension("xbob.flandmark._flandmark",
        [
          "xbob/flandmark/ext/flandmark_detector.cpp",
          "xbob/flandmark/ext/liblbp.cpp",
          "xbob/flandmark/ext/ext.cpp",
        ],
        pkgconfig = [
          'opencv',
          ]
        )
      ],

    classifiers = [
      'Development Status :: 5 - Production/Stable',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
      ],
    
    )
