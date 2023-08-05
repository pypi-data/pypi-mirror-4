#coding:utf-8
from setuptools import setup, find_packages


setup(
    name='zorm',
    version="0.132",
    description="A minimal ORM",
    author="zuroc 张沈鹏",
    author_email="zsp042@gmail.com",
    packages = ['zorm'],
    install_requires = [
        'msgpack-python',
        'MySQL-python',
        'hiredis',
        'redis',
        'DBUtils',
        'intstr',
        'pyrex',
        'decorator',
    ],

)

