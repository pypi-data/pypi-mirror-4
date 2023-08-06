from setuptools import setup
#from distutils.core import setup
import os

def read(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'noolite',
    version = '0.2.0',
    author = 'Anton Balashov',
    author_email = 'sicness@darklogic.ru',
    maintainer = 'Anton Balashov',
    maintainer_email = 'sicness@darklogic.ru',
    description = 'Class for NooLite USB stick',
    py_modules = ['noolite'],
    install_requires = ['pyusb'],
    license = "GPLv3",
    platforms = 'any',
    url = 'https://github.com/Sicness/pyNooLite',
    keywords = ["noolite", "USB", "smarthome","PC118","PC116","PC1132"],
    long_description = read("README.txt"),
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Manufacturing",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Home Automation",
        "Topic :: System :: Hardware"
        ]
    )
