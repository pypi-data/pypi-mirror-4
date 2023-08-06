#coding:utf-8

from setuptools import setup, find_packages 

setup(
    name='pytenpay',
    version="0.2.2", 
    description="财付通批量银行代付接口Python实现", 
    author="Zuroc, Lerry",
    author_email="zsp042@gmail.com",
    packages = ['pytenpay'],
    zip_safe=False,
    include_package_data=True,
    install_requires = [
        'requests>=1.2.0',
        'mako',
    ],
    url = "https://bitbucket.org/lerry/pytenpay",
)

