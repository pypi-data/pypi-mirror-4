#!/usr/bin/env python

import os
from glob import glob
from distutils.util import convert_path

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup  # NOQA


def find_packages(where=".", exclude=()):
    """Borrowed directly from setuptools"""

    out = []
    stack = [(convert_path(where), "")]
    while stack:
        where, prefix = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if ("." not in name and os.path.isdir(fn) and
                    os.path.isfile(os.path.join(fn, "__init__.py"))):
                out.append(prefix + name)
                stack.append((fn, prefix + name + "."))

    from fnmatch import fnmatchcase
    for pat in list(exclude) + ["ez_setup"]:
        out = [item for item in out if not fnmatchcase(item, pat)]

    return out

path = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(path, "README.rst")).read()
    RELEASE = open(os.path.join(path, "RELEASE.rst")).read()
except IOError:
    README = RELEASE = ""

setup(
    name="circuits",
    version="2.1.0",
    description="Asynchronous Component based Event Application Framework",
    long_description="%s\n\n%s" % (README, RELEASE),
    author="James Mills",
    author_email="James Mills, prologic at shortcircuit dot net dot au",
    url="http://bitbucket.org/prologic/circuits/",
    download_url="http://bitbucket.org/prologic/circuits/downloads/",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: No Input/Output (Daemon)",
        "Environment :: Other Environment",
        "Environment :: Plugins",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Telecommunications Industry",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Adaptive Technologies",
        "Topic :: Communications :: Chat :: Internet Relay Chat",
        "Topic :: Communications :: Email :: Mail Transport Agents",
        "Topic :: Database",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Server",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Clustering",
        "Topic :: System :: Distributed Computing"],
    license="MIT",
    keywords="event framework distributed concurrent component asynchronous",
    platforms="POSIX",
    packages=find_packages("."),
    scripts=glob("scripts/*"),
    entry_points="""
    [console_scripts]
    circuits.web = circuits.web.main:main
    """,
    zip_safe=False,
    test_suite="tests.main.runtests",
)

# hghooks: no-pyflakes
