#coding:utf-8

from setuptools import setup, find_packages 

setup(
    name='lerrylib',
    version="0.1.1", 
    description="Some common use functions", 
    author="Lerry",
    author_email="lvdachao@gmail.com",
    packages = ['lerrylib'],
    zip_safe=False,
    include_package_data=True,
    install_requires = [
    ],
    url = "https://bitbucket.org/lerry/lerrylib",
)

