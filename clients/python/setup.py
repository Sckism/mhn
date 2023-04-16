from setuptools import setup, find_packages

setup(
    name="sckism-mhn",
    version="0.0.5",
    description="Minimalist Hierarchical Notation (MHN) library",
    long_description="Minimalist Hierarchical Notation (MHN) library provides a cross between CSV and JSON allowing for hierarchal data structures and arrays in a flat text based format.",
    author="Peter Wicks",
    author_email="peter@wicks.ninja",
    url="https://github.com/Sckism/mhn",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
