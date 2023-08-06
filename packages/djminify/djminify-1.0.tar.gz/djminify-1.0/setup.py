#from setuptools import setup
from distutils.core import setup

description = """
Powerfull and dead simple usage, django css/js minifier (compressor).
"""

setup(
    name = "djminify",
    url = "https://github.com/niwibe/django-minify",
    author = "Andrey Antukh",
    author_email = "niwi@niwi.be",
    version='1.0',
    packages = [
        "djminify",
        "djminify.compilers",
        "djminify.templatetags",
        "djminify.parser",
    ],
    description = description.strip(),
    include_package_data = True,
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
        "Environment :: Web Environment",
        "Framework :: Django",
        "License :: OSI Approved :: BSD License",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
)
