"""
Unit tests for swag/util.py.

Tests cover print_line(), run_cmd(), and get_env_var() without touching
the filesystem or spawning real subprocesses. subprocess.run and
os.path.exists are mocked throughout.

Run with:
    python -m pytest tests/test_util.py
"""
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
import subprocess as sp

sys.path.insert(0, str(Path(__file__).parent.parent))

from swag.util import get_env_var, print_line, run_cmd


# ---------------------------------------------------------------------------
# print_line

class TestPrintLine(unittest.TestCase):

    @patch('builtins.print')
    def test_default_width(self, mock_print):
        print_line()
        mock_print.assert_called_once_with('  ' + '-' * 80)

    @patch('builtins.print')
    def test_custom_width(self, mock_print):
        print_line(width=40)
        mock_print.assert_called_once_with('  ' + '-' * 40)


# ---------------------------------------------------------------------------
# run_cmd

class TestRunCmd(unittest.TestCase):

    @patch('swag.util.sp.run')
    def test_calls_subprocess_with_correct_args(self, mock_run):
        run_cmd('echo hello')
        mock_run.assert_called_once_with(
            'echo hello',
            shell=True,
            check=True,
            executable='/bin/bash',
        )

    @patch('swag.util.sp.run', side_effect=sp.CalledProcessError(1, 'bad_cmd'))
    def test_propagates_called_process_error(self, _mock_run):
        with self.assertRaises(sp.CalledProcessError):
            run_cmd('bad_cmd')


# ---------------------------------------------------------------------------
# get_env_var

class TestGetEnvVar(unittest.TestCase):

    @patch('swag.util.os.path.exists', return_value=False)
    def test_raises_file_not_found_when_config_missing(self, _mock_exists):
        with self.assertRaises(FileNotFoundError) as ctx:
            get_env_var('/nonexistent/config.sh', 'MY_VAR')
        self.assertIn('/nonexistent/config.sh', str(ctx.exception))

    @patch('swag.util.sp.run')
    @patch('swag.util.os.path.exists', return_value=True)
    def test_raises_value_error_when_stdout_empty(self, _mock_exists, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = '\n'
        mock_run.return_value = mock_result
        with self.assertRaises(ValueError) as ctx:
            get_env_var('/some/config.sh', 'EMPTY_VAR')
        self.assertIn('EMPTY_VAR', str(ctx.exception))

    @patch('swag.util.sp.run')
    @patch('swag.util.os.path.exists', return_value=True)
    def test_returns_value_when_stdout_nonempty(self, _mock_exists, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = '/some/path/value\n'
        mock_run.return_value = mock_result
        result = get_env_var('/some/config.sh', 'MY_VAR')
        self.assertEqual(result, '/some/path/value')


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
