import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pyexeccontrol",
    version = "0.0.2",
    author = "Francesco Bruschi",
    author_email = "fbrusch@gmail.com",
    description = "An interface to gdb to control program execution",
    license = "BSD",
    keywords = "gdb debug execution",
    url = "http://packages.python.org/pyexeccontrol",
    packages = ["execcontrol"],
    long_description = read('README'),
    classifiers = [
        "Development Status :: 2 - Pre-Alpha"],
    install_requires = read("requirements.txt")
)
