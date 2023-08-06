from distutils.core import setup

setup(
    name = 'noolite',
    py_modules = ['noolite'],
    version = '0.1.0',
    description = 'Class for NooLite USB stick',
    author = 'Anton Balashov',
    author_email = 'sicness@darklogic.ru',
    url = 'https://github.com/Sicness/pyNooLite',
    keywords = ["noolite", "smarthome"],
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
