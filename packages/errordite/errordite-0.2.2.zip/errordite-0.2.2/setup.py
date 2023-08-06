"""
Setup file for python-errordite.
"""
import os
from os.path import join, dirname, normpath, abspath
from setuptools import setup
import errordite

# allow setup.py to be run from any path
os.chdir(normpath(join(abspath(__file__), os.pardir)))

setup(
    name=errordite.__title__,
    version=errordite.__version__,
    packages=['errordite'],
    include_package_data=True,
    install_requires=['requests'],
    license=open(join(dirname(__file__), 'LICENCE.md')).read(),
    description=errordite.__description__,
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    url='https://github.com/hugorodgerbrown/python-errordite',
    author=errordite.__author__,
    author_email='hugo@rodger-brown.com',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
)
