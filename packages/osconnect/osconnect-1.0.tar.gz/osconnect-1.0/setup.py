# setup.py
#try:
#    from setuptools import setup
#except:
#    from distutils.core import setup
    
from setuptools import setup, find_packages
from os.path import join, dirname

import osconnect

setup(
    name = 'osconnect',
    version = osconnect.__version__,
    packages = find_packages(),
    long_description = open(join(dirname(__file__), 'README.rst')).read(),
    install_requires=[
        'pexpect',#==0.8',
    ],
    test_suite='tests',
)