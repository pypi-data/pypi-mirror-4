from setuptools import setup

from ecglist import __version__

setup(
    name             = "email-ecglist",
    version          = __version__,
    author           = "Martin J. Laubach",
    author_email     = "pypi+ecglist@laubach.at",
    description      = ("Check email addresses against the austrian do-not-email list (ECG-Liste)"),
    license          = "BSD",
    keywords         = "email validation ecglist",
    url              = "http://github.com/mjl/email-ecglist",
    py_modules       = ['ecglist'],
    long_description = open('README.rst').read(),
    test_suite       = "tests",
    classifiers      = [
        "Development Status :: 5 - Production/Stable",
        "Topic :: Communications :: Email",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3"
    ],
)
