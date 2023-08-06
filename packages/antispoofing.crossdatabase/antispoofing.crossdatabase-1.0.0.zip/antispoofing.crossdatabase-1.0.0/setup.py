#!/usr/bin/env python
#Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
#Sat Jul  9 20:21:55 CEST 2012

from setuptools import setup, find_packages

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='antispoofing.crossdatabase',
    version='1.0.0',
    description='Antispoofing cross database testing',
    url='http://pypi.python.org/pypi/antispoofing.crossdatabase',
    license='GPLv3',
    author='Tiago de Freitas Pereira',
    author_email='tiagofrepereira@gmail.com',
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data = True,

    install_requires=[
        "bob >= 1.1.0",         # base signal proc./machine learning library
        "gridtk",
        "xbob.db.replay",     #Replay database
        "xbob.db.casia_fasd", #CASIA database
        "antispoofing.lbptop",  #LBP-TOP Package
        "antispoofing.utils",  #Utils Package
        "antispoofing.fusion",  #Fusion Package
    ],

    namespace_packages = [
      'antispoofing',
      ],

    entry_points={
      'console_scripts': [
         'crossdb_result_analysis.py= antispoofing.crossdatabase.script.crossdb_result_analysis:main',
         'crossdb_fusion_framework.py = antispoofing.crossdatabase.script.crossdb_fusion_framework:main',
         'crossdb_computeQStatistic.py = antispoofing.crossdatabase.script.crossdb_computeQStatistic:main',
         'check_common_errors.py = antispoofing.crossdatabase.script.check_common_errors:main',
         'fusion_faceverif.py = antispoofing.crossdatabase.script.fusion_faceverif:main',
        ],
      },

)
