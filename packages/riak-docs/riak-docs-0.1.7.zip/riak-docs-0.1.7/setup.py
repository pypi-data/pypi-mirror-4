from setuptools import setup, find_packages

setup(
    name='riak-docs',
    version='0.1.7',
    description='Models to facilitate some common interactions with Riak documents.',
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