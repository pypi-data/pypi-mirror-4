import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
    

setup(
    name = "mathchem",
    version = "0.1.1",
    description = "",
    long_description = read('README.md'),
    url = 'https://github.com/hamster3d/mathchem-package',
    license = 'MIT',
    author = 'Alexander Vasilyev',
    author_email = 'hamster3d@gmail.com',
    packages = find_packages(exclude=['tests']),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ],
    install_requires = ['numpy'],

)
