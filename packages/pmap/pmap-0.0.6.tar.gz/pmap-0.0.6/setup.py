from setuptools import setup

setup(
    name = "pmap",
    version = "0.0.6",
    author = "Francesco Bruschi",
    py_modules = ["pmap"],
    description = "a multithreaded map operator",
    long_description = open("README.md").read(),
    author_email = "bruschi@elet.polimi.it",
    install_requires = open("requirements.txt").read().splitlines()
)
