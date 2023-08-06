#coding:utf-8

from setuptools import setup, find_packages 

setup(
    name='lerrylib',
    version="0.1", 
    description="一些自己写的函数", 
    author="Lerry",
    author_email="lvdachao@gmail.com",
    packages = ['lerrylib'],
    zip_safe=False,
    include_package_data=True,
    install_requires = [
    ],
    url = "https://bitbucket.org/lerry/lerrylib",
)

