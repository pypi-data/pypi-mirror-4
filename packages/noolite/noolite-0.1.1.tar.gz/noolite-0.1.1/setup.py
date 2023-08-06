from distutils.core import setup
import os

def read(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'noolite',
    py_modules = ['noolite'],
    version = '0.1.1',
    description = 'Class for NooLite USB stick',
    author = 'Anton Balashov',
    author_email = 'sicness@darklogic.ru',
    license = "GPLv3",
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
