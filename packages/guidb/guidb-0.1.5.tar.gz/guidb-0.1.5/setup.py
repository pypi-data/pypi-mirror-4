import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "guidb",
    version = "0.1.5",
    author = "Guillem Borrell",
    author_email = "guillemborrell@gmail.com",
    description = ("""Very simple parallel database based on leveldb and zeromq."""),
    license = "BSD",
    keywords = "parallel database",
    long_description=read('README'),
    url = "http://guillemborrell.es",
    packages=['guidb'],
    package_data={'': ['guidb/runservers.sh']},
    install_requires=[
        'pyzmq',
        'protobuf',
        'leveldb',
        ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "Programming Language :: Python :: 2.7",
        'Intended Audience :: Developers',
        "License :: OSI Approved :: BSD License",
    ],
)
