import os
from setuptools import setup, find_packages

def readfile(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()

setup(
    name='riak-docs',
    version='0.1.3',
    description='Models to facilitate some common interactions with Riak documents.',
    long_description=readfile('README.md'),
    author='Dan Ostrowski',
    author_email='dan.ostrowski@gmail.com',
    license='BSD',
    keywords='riak models object',
    install_requires=['riak', 'blinker'],
    packages=find_packages(),
    url='https://bitbucket.org/danostrowski/riakdocs',
    classifiers=[
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)