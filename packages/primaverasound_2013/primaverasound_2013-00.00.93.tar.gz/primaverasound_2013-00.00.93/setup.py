# coding=UTF-8
'''
Created on 22/03/2013

Setuptools setup file

@author: Ricardo García Fernández
@mail: ricardogarfe@gmail.com
'''
 
from setuptools import setup, find_packages

setup (name="primaverasound_2013",
        version="00.00.93",
        packages=find_packages(exclude=["test", "test.*"]),
        scripts=['retrieve_schedule.py'],
        install_requires=['requests', 'lxml==2.3.2'],
        package_data={'primaverasound_schedule':[''], },
        author='Ricardo García Fernández',
        author_email='ricardogarfe@gmail.com',
        description='Primavera Sound 2013 Schedule scraper per day and Concert for http://primaverasound.com',
        license = 'Apache v2.0',
        keywords='primaverasound',
        url='http://ricardogarfe.github.com/primaverasound/',
        long_description='Primavera Sound 2013 Schedule scraper per day and Concert for http://primaverasound.com. You can see results in ScraperWiki https://scraperwiki.com/scrapers/primavera_sound_2013/',
        download_url='https://github.com/ricardogarfe/primaverasound/archive/master.zip',
        )
