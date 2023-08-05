from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

import unittest
import mock

from nensbuild import build


class TestBuild(unittest.TestCase):

    @mock.patch('subprocess.call')
    def test_create_link(self, call):
        with mock.patch('os.path.exists',
                        return_value=False):
            build.link()
        self.assertTrue(call.called)
        call.assert_called_with(
            ['ln', '-sf', 'development.cfg', 'buildout.cfg'])

    @mock.patch('subprocess.call')
    def test_not_create_link(self, call):
        with mock.patch('os.path.exists',
                        return_value=True):
            build.link()
        self.assertFalse(call.called)

    @mock.patch('subprocess.call')
    def test_run_boostrap(self, call):
        with mock.patch('os.path.exists',
                        return_value=False):
            build.bootstrap()
        self.assertTrue(call.called)
        call.assert_called_with(
            ['python', 'bootstrap.py'])

    @mock.patch('subprocess.call')
    def test_not_run_bootstrap(self, call):
        with mock.patch('os.path.exists',
                        return_value=True):
            build.bootstrap()
        self.assertFalse(call.called)

    @mock.patch('subprocess.call')
    def test_run_buildout(self, call):
        build.buildout()
        self.assertTrue(call.called)
        call.assert_called_with(['bin/buildout'])

    @mock.patch('os.path.exists', return_value=False)
    @mock.patch('subprocess.call')
    def run_all(self):
        build.main()
