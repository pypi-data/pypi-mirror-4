# coding=UTF-8
'''
Created on 27/09/2012

Setuptools setup file

@author: Ricardo García Fernández
@mail: ricardogarfe@gmail.com
'''
 
from setuptools import setup, find_packages

setup (name="ricardo_crawler",
        version="0.9.1",
        packages=find_packages(),
        scripts=['ricardo_crawler.py'],
        install_requires=['BeautifulSoup'],
        package_data={'pyricardo_crawler':[''], },
        author='Ricardo García Fernández',
        author_email='ricardogarfe@gmail.com',
        description='My first Web Scrapper in Python',
        license = 'GNU GPLv3',
        keywords='web-crawler',
        url='https://github.com/ricardogarfe/crawler-mswl',
        long_description='Web Scrapper in Python for Development Tools Subject from MSWL - URJC',
        download_url='',
        )
