# coding: utf-8
import os

from setuptools import setup


README_FILE = os.path.join(os.path.dirname(__file__), 'README.rst')


setup(
    name="mako-pipeline",
    description="Manage assets on mako templates",
    long_description=open(README_FILE, 'r').read(),
    version="0.0.1",
    packages=["mako_pipeline"],
    author="Rodrigo Machado",
    author_email="rcmachado@gmail.com",
    url="https://github.com/rcmachado/mako-pipeline",
    license="MIT",
    install_requires=["mako"],
    test_suite="nose.collector",
    test_requires=["nose==1.2.1", "mock==1.0.1", "coverage==3.5.3"]
)
