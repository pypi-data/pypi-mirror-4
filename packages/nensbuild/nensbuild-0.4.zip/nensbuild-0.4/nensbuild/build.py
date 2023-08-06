from __future__ import absolute_import, division
from __future__ import print_function, unicode_literals


import os.path
import subprocess
import sys


def get_bash_path():
    try:
        return subprocess.check_output(['which', 'bash']).strip()
    except subprocess.CalledProcessError:
        sys.stderr.write('Bash not found, please install bash')
        sys.exit(1)


def link():
    result_file = 'buildout.cfg'
    if not os.path.exists(result_file):
        subprocess.call(['ln', '-sf', 'development.cfg', result_file])


def bootstrap():
    result_file = 'bin/buildout'
    if not os.path.exists(result_file):
        subprocess.call(['python', 'bootstrap.py'])


def buildout():
    bash = get_bash_path()
    subprocess.call([bash, '-c', 'bin/buildout'])


def is_sysegg_in_buildout():
    return (
        'recipe= syseggrecipe' in
        subprocess.check_output(['bin/buildout', 'annotate']))


def check_sysegg():
    if is_sysegg_in_buildout():
        subprocess.call(['bin/buildout', 'sysegg:force-sysegg=false',
                         'install', 'sysegg'])


def main():
    """Run all commands."""

    link()
    bootstrap()
    buildout()
    check_sysegg()
