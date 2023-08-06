#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 16 Apr 08:18:08 2012 CEST

from setuptools import setup, find_packages

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='antispoofing.optflow',
    version='1.0.0',
    description='Optical Flow counter-measures for the REPLAY-ATTACK database',
    url='http://pypi.python.org/pypi/antispoofing.optflow',
    license='GPLv3',
    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,

    namespace_packages=[
      "antispoofing",
      ],

    install_requires=[
      "setuptools",
      "bob >= 1.1.0",
      "xbob.db.replay",
      "xbob.optflow.liu >= 1.1.0",
      "antispoofing.utils",
      "antispoofing.motion >= 1.1.0a0",
    ],

    entry_points={

      'console_scripts': [
        'optflow_estimate.py = antispoofing.optflow.script.liu:main',
        'optflow_histocomp.py = antispoofing.optflow.script.histocomp:main',
        'optflow_kollreider.py = antispoofing.optflow.script.kollreider:main',
        'optflow_bao.py = antispoofing.optflow.script.bao:main',
        'score_analysis.py = antispoofing.optflow.script.score_analysis:main',
        'optflow_kollreider_annotate.py = antispoofing.optflow.script.kollreider_annotate:main',
        ],

      },

)
