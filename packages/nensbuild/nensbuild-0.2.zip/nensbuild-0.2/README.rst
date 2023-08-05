NENS Build
============

At Nelen & Schuurmans we use a couple commands to get a development environment
up and running::

    git clone repo
    cd repo
    ln -s development.cfg buildout.cfg
    python bootstrap.py
    bin/buildout

There are more commands that could be eliminated::
    
    createdb
    bin/django syncdb
    bin/django migrate

This is a code smell according to book Clean Code. A build should 
have three steps at the most::

    git clone repo
    cd repo
    build


This python packages aims to solve this by going eliminating the symlink, bootstrap and buildout commands::

    git clone repo
    cd repo
    nens-build
