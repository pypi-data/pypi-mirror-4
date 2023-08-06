"""
Setup file for python-errordite.
"""
import os
from os.path import join, dirname, normpath, abspath
from setuptools import setup

# we can't import errordite as it hasn't been installed yet, so instead
# read information in as text. This will read in the __init__ file, and
# create a dict containing any lines beginning with '__' as keys, with
# whatever is after the '=' as the value,
# __desc__ = 'hello'
# would give {'desc': 'hello'}
meta = {}
for l in [line for line in tuple(open('errordite/__init__.py', 'r')) if line[:2] == '__']:
    t = l.split('=')
    meta[t[0].strip().strip('__')] = t[1].strip().strip('\'')

# allow setup.py to be run from any path
os.chdir(normpath(join(abspath(__file__), os.pardir)))

setup(
    name=meta['title'],
    version=meta['version'],
    packages=['errordite'],
    include_package_data=True,
    install_requires=['requests'],
    license=open(join(dirname(__file__), 'LICENCE.md')).read(),
    description=meta['description'],
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    url='https://github.com/hugorodgerbrown/python-errordite',
    author=meta['author'],
    author_email='hugo@rodger-brown.com',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
)
