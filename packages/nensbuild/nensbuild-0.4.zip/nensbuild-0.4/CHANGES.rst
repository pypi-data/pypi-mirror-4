Changelog of nens-build
===================================================


0.4 (2013-02-05)
----------------

- Add sysegg check. This depends on the new syseggrecipe.
- Drop python2.6 support (again). subprocess.check_output is nw in python 2.7.


0.3 (2012-12-22)
----------------

- Add travis-ci support.
- Use bash as shell for running buildout. Fixes an issue with running nensbuild
  on a Vagrant virtual box. Fixes gh-1.


0.2 (2012-12-15)
----------------

- Fix classifiers for release on pypi.


0.1 (2012-12-15)
----------------

- Remove use of external python libraries.
- Add unittests.
- Initial project structure created with nensskel 1.29.
