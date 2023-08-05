# Asq's setup.py

from distutils.core import setup

version = "0.5"

with open('README.md', 'r') as readme:
    long_description = readme.read()

setup(
    name = "keeper",
    packages = ["keeper"],
    version = "{version}".format(version=version),
    description = "A file-based value store for bytes and strings.",
    author = "Robert Smallshire",
    author_email = "robert@smallshire.org.uk",
    url = "https://github.com/rob-smallshire/keeper/",
    download_url="https://github.com/rob-smallshire/keeper/archive/master.zip".format(version=version),
    keywords = ["Python"],
    license="MIT License",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        ],
    long_description = long_description
)
