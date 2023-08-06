import os
from setuptools import setup, Extension
from glob import glob

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "ucloudbiz",
    version = "0.1.0",
    author = "Choonho Son",
    author_email = "choonho.son@kt.com",
    description = ("ucloudbiz openapi python library."),
    license = "BSD",
    keywords = "ucloud ucloudbiz config library",
    url = "http://ucloud.googlecode.com",
    packages=['ucloudbiz', 'ucloudbiz.server', 'ucloudbiz.server.lib', 'ucloudbiz.server.vm', 'ucloudbiz.server.address', 'ucloudbiz.server.portforwarding'],
    long_description=read('README.txt'),
    zip_safe=True,
)
