import os
from distutils.core import setup
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "bbricks",
    packages = ["bbricks"],
    version = "1.0.11",
    description = "C/C++ builder on top of SCons, automatically enforcing quality, coding stanadards, etc",
    author = "alvaro ramirez",
    author_email = "alvaro@xenodium.com",
    keywords = ["scons", "cpp", "cpplint"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Quality Assurance"
        ],
    install_requires=['colorama', 'termcolor'],
    long_description=read('README') + read('bbricks/configs.py')
)
