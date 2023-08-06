#!/usr/bin/env python
from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup
import re
import platform
import os
import sys


def load_version(filename='yara/version.py'):
    """Parse a __version__ number from a source file"""
    with open(filename) as source:
        text = source.read()
        match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", text)
        if not match:
            msg = "Unable to find version number in {}".format(filename)
            raise RuntimeError(msg)
        version = match.group(1)
        return version


#build the yara package data (shipped yar files)
yara_package_data = []
for path, _, files in os.walk(os.path.join('yara', 'rules')):
    rootpath = path[len('yara') + 1:]
    for f in files:
        if f.endswith('.yar'):
            yara_package_data.append(os.path.join(rootpath, f))


#see if we have a pre-built libyara for this platform
arch, exetype = platform.architecture()
system = platform.system().lower()
machine = platform.machine().lower()

if system == 'windows':
    ext = '.dll'
else:
    ext = '.so'

libyara_path = os.path.join('.', 'libs', system, machine, "libyara" + ext)
data_files = []
if os.path.exists(libyara_path):
    if system == 'windows':
        install_libdir = os.path.join(sys.prefix, 'DLLs')
    else:
        install_libdir = os.path.join(sys.prefix, 'lib')
    data_files.append((install_libdir, [libyara_path]))
else:
    print("WARNING: Could not find %s" % libyara_path)
    print("You need to 'make install' libyara for this system/machine")
    print("See http://pythonhosted.org/yara/ for help")

setup(
    name="yara",
    version=load_version(),
    packages=['yara'],
    package_data=dict(yara=yara_package_data),
    data_files=data_files,
    zip_safe=False,
    author="Michael Dorman",
    author_email="mjdorma@gmail.com",
    url="http://code.google.com/p/yara-project/",
    description="Compile YARA rules to test against files or strings",
    long_description=open('README.rst').read(),
    license="Apache Software Licence",
    install_requires = [],
    platforms=['cygwin', 'win', 'linux'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Security',
        'Topic :: System :: Monitoring'
    ],
    test_suite="tests"
)
