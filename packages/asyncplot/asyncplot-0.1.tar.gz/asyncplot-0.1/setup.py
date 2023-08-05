import os
from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="asyncplot",
    version="0.1",
    author="Michael McNeil Forbes, Katheryn Buble",
    author_email="michael.forbes+python@gmail.com",
    description="Asynchronous client-server library for simple plotting.",
    license="BSD",
    keywords=["asynchronous", "plotting", "matplotlib"],
    url="https://bitbucket.org/mforbes/asyncplot",
    packages=['asyncplot'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
