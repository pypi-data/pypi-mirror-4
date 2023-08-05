from __future__ import absolute_import, division
from __future__ import print_function, unicode_literals


import os.path
import subprocess


def link():
    result_file = 'buildout.cfg'
    if not os.path.exists(result_file):
        subprocess.call(['ln', '-sf', 'development.cfg', result_file])


def bootstrap():
    result_file = 'bin/buildout'
    if not os.path.exists(result_file):
        subprocess.call(['python', 'bootstrap.py'])


def buildout():
    subprocess.call(['bin/buildout'])


def main():
    """Run all commands."""

    link()
    bootstrap()
    buildout()
