from io import open
from setuptools import setup, find_packages

with open("README.md") as fh:
    long_description = fh.read()

setup(
    name="autoui",
    version="0.1.0",
    author="Alexandre Seris",
    author_email="alexandreseris@hotmail.fr",
    description="A python lib to help you generate UI for your functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["gui", "cli", "UI"],
    url="https://github.com/alexandreseris/autoui",
    project_urls={
        "Bug Tracker": "https://github.com/alexandreseris/autoui/issues"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    install_requires=[
        "bottle==0.12.19",
        "docstring_parser==0.13",
        "Eel==0.14.0"
    ],
    python_requires=">=3.6",
    setup_requires=['wheel'],
)
