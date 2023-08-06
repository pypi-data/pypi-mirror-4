import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='python-barcode-spreadSheet',
    version='1.1.2',
    license='BSD',
    description='A simple Python tool to generate bar-codes and programmatically insert them into Google Spreadsheets for printing.',
    long_description=README,
    url='http://prasenjitsingh.com/opensource/python-barcode-spreadSheet/',
    author='Prasenjit Singh',
    author_email='prasenjit0625@gmail.com',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)