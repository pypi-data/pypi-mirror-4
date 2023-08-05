import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Don't import fatzebra module here, since deps may not be installed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'fatzebra'))
from fatzebra import version

path, script = os.path.split(sys.argv[0])
os.chdir(os.path.abspath(path))

setup(name='fatzebra',
    version=version.VERSION,
    description='Fat Zebra Python Library',
    long_description=open("README.txt").read(),
    author='Fat Zebra',
    author_email='support@fatzebra.com.au',
    url='https://www.fatzebra.com.au/',
    packages=['fatzebra'],
    install_requires=['requests >= 0.14.2', 'simplejson'],
    test_suite='test',
)
