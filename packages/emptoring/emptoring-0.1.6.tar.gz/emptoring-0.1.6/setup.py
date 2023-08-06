""" setup.py

    Basic setup file to enable pip install
    
    http://python-distribute.org/distribute_setup.py
    
    python setup.py register -r pypi sdist upload -r pypi
"""

#from distribute_setup import use_setuptools
#use_setuptools()

from setuptools import setup, find_packages

setup(
        name='emptoring',
        version='0.1.6',
        install_requires=['simplejson', 'requests', 'pystache', 'lxml'],
        extras_require = { 'python2.6' : ['ordereddict'], 'tests': ['gevent'],},
        packages=find_packages(),      
        package_data={'': ['*.txt',  '*.ico',  '*.json']},
        description='Generic backend http client library',
        author='Samuel M Smith',
        author_email='smith.samuel.m@gmail.com',
        license="MIT", 
        url='https://github.com/SmithSamuelM/emptor',
        keywords='http client requests'
    )
