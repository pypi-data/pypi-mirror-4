from distutils.cmd import Command
from setuptools import setup
import os
import re
import sys
import shutil

VERSION = '1.0'

THIS_PATH = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))

def pkg_by_version(name=""):
    return name + ("" if sys.version_info[0] < 3 else "3")

def read(fname):
    path = os.path.join(THIS_PATH, fname)
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return None

class CleanCommand(Command):
    user_options = []

    def initialize_options(self):
        self.paths = []
        
        for f in os.listdir(THIS_PATH):
            if re.search("(^(build|dist|__pycache__)$|\.egg-info|\.egg)", f):
                self.paths.append(f)
            
        for root, dirs, files in os.walk(THIS_PATH):
            for f in files:
                if f.endswith(".pyc") or f.endswith(".pyc") or f.endswith(".pyo"):
                    self.paths.append(os.path.join(root, f))
                    
            for f in dirs:
                if re.search("^(__pycache__)$", f):
                    self.paths.append(os.path.join(root, f))

    def finalize_options(self):
        pass
    
    def run(self):
        for p in self.paths:
            if os.path.exists(p):
                if os.path.isdir(p):
                    print("Remove directory: " + p)
                    shutil.rmtree(p)
                else:
                    print("Remove file     : " + p)
                    os.unlink(p)

setup(
    name="py_interception",
    version=VERSION,
    author="Moises P. Sena",
    author_email="moisespsena@gmail.com",
    description="Method Interception with Dependency Injection implementation.",
    license="BSD",
    keywords="utils utilities di dependecy injection intercept interception",
    url="https://github.com/moisespsena/py_interception",
    packages=["interception"],
    test_suite='tests.' + pkg_by_version("p") + ".test_all",
    long_description="\n\n".join((read("README.rst"), read('AUTHORS.rst'), read('ChangeLog.rst'),)),
    classifiers=(
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ),
    cmdclass={'clean': CleanCommand},
    zip_safe=False,
    install_requires=(
        'py_di>=1.0',
        'py_sdag2>=1.0',
    ),
    setup_requires=(
        'setuptools',
	'setuptools-git',
    ),
)
