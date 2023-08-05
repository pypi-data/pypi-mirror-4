# -*- coding:utf-8 -*-
'''
Created on 22/03/2010

@author: Flavio Codeco Coelho<fccoelho@gmail.com>
'''

#from ez_setup import use_setuptools
#use_setuptools()

from setuptools import setup, find_packages


setup(name='hidx', 
        version  = '0.5',
        author = 'Flavio Codeco Coelho', 
        author_email = 'fccoelho@gmail.com', 
        url = 'http://code.google.com/p/hidx/',
        description = 'High Dimensional Data Explorer',
        zip_safe = True,
        packages = find_packages(),
        entry_points = {'gui_scripts': ['hidx = hidx:main']}, 
        install_requires = ["numpy", "matplotlib", "SQLAlchemy", "MySQLDb",
                            "GeoAlchemy", "psycopg2", "pandas>=0.8", "dbf>=0.94"],
        test_suite = 'nose.collector', 
        license = 'GPL', 
        include_package_data = True,
        package_data = {'': ['INSTALL', 'README', 'COPYING', 'hidx.desktop',
                             '*.qrc', '*.qm', '*.png', '*.ui']},
      )
