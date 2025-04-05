#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="internal-file-transfer",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple and efficient internal file transfer tool for local networks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/internal-file-transfer",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "flask==2.3.3",
        "flask-socketio==5.3.4",
        "pywebview==4.3",
        "simple-websocket==1.0.0",
        "Werkzeug==2.3.7",
    ],
    entry_points={
        "console_scripts": [
            "internal-file-transfer=main:main",
        ],
    },
) 