"""
Setup file for python-errordite.
"""
import os
from os.path import join, dirname, normpath, abspath
from setuptools import setup

# allow setup.py to be run from any path
os.chdir(normpath(join(abspath(__file__), os.pardir)))

setup(
    name='errordite',
    version='0.1',
    packages=['errordite'],
    include_package_data=True,
    license=open(join(dirname(__file__), 'LICENCE.md')).read(),
    description='Errordite integration for python projects.',
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    url='https://github.com/hugorodgerbrown/python-errordite',
    author='Hugo Rodger-Brown',
    author_email='hugo@rodger-brown.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
