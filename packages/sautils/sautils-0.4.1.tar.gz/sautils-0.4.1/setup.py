from setuptools import setup, find_packages
import sys, os

version = '0.4.1'

setup(
    name='sautils',
    version=version,
    description='Various SQLAlchemy utilities',
    author='Andrey Popp',
    author_email='8mayday@gmail.com',
    license='BSD',
    py_modules=['sautils'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'sqlalchemy',
    ],
    entry_points='''
    # -*- Entry points: -*-
    ''')
