from setuptools import setup, find_packages
import os, sys, re

# Load the version by reading noeq.py, so we don't run into
# dependency loops by importing it into setup.py
version = None
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "noeq.py")) as file:
    for line in file:
        m = re.search(r'__version__\s*=\s*(.+?\n)', line)
        if m:
            version = eval(m.group(1))
            break

setup_args = dict(
    name             = 'noeq',
    version          = version,
    author           = 'Chris Petersen',
    author_email     = 'geek@ex-nerd.com',
    url              = 'https://github.com/noeq/python-noeq',
    license          = 'MIT',
    description      = 'Noeq client',
    long_description = open('README.md').read(),
    install_requires = [],
    py_modules       = ['noeq'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Utilities",
    ],
)

if __name__ == '__main__':
    setup(**setup_args)

