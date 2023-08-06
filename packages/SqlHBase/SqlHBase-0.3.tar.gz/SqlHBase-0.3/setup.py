__author__ = 'zeph'

from distutils.core import setup
from setuptools import setup

setup(
    name='SqlHBase',
    version='0.3',
    author='Guido Serra aka Zeph',
    author_email='zeph@fsfe.org',
    url='http://www.rocket-internet.de',
    packages=['sqlhbase',],
    scripts=['bin/sqlhbase-mysqlimport','bin/sqlhbase-populate'],
    license='GPL 3',
    description='MySQLDump to HBase, ETL scripts',
    long_description=open('README.md').read(),
    install_requires=[
        "happybase >= 0.4",
        "hive-thrift-py == 0.0.1",
    ]
)
