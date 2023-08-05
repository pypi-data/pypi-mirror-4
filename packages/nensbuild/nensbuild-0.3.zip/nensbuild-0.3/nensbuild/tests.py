from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

import unittest
import mock

from nensbuild import build


class TestBuild(unittest.TestCase):

    def setUp(self):
        self.patcher1 = mock.patch('subprocess.call')
        self.patcher2 = mock.patch('os.path.exists')

        self.call = self.patcher1.start()
        self.exists = self.patcher2.start()

    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()

    def test_find_bash(self):
        with mock.patch('subprocess.check_output',
                        return_value='/bin/bash\n') as check_output:
            bash = build.get_bash_path()

        self.assertEqual('/bin/bash', bash)
        check_output.assert_called_with(
            ['which', 'bash'])

    @mock.patch('sys.stderr')
    @mock.patch('sys.exit')
    def test_find_bash_while_not_installed(self, sys_exit, sys_stderr):
        from subprocess import CalledProcessError
        exception = CalledProcessError(1, ['which', 'bash'])

        with mock.patch('subprocess.check_output',
                        side_effect=exception):
            build.get_bash_path()
        sys_exit.assert_called_with(1)
        sys_stderr.write.assert_called_with(
            'Bash not found, please install bash')

    def test_create_link(self):
        self.exists.return_value = False
        build.link()
        self.call.assert_called_with(
            ['ln', '-sf', 'development.cfg', 'buildout.cfg'])

    def test_not_create_link(self):
        self.exists.return_value = True
        build.link()
        self.assertFalse(self.call.called)

    def test_run_boostrap(self):
        self.exists.return_value = False
        build.bootstrap()
        self.call.assert_called_with(
            ['python', 'bootstrap.py'])

    def test_not_run_bootstrap(self):
        self.exists.return_value = True
        build.bootstrap()
        self.assertFalse(self.call.called)

    def test_run_buildout(self):

        with mock.patch('nensbuild.build.get_bash_path',
                        return_value='/bin/bash'):
            build.buildout()
        self.call.assert_called_with(['/bin/bash', '-c', 'bin/buildout'])

    def test_run_all(self):
        self.exists.return_value = False
        build.main()
        self.assertEqual(self.call.call_count, 3)
