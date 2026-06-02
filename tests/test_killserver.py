"""Unit tests for killserver() logic ported from PR #107.

The killserver() function is duplicated in each of the three distance scripts:
- jaccard_similarity.py
- cosine_similarity.py
- edit-value-similarity.py

These tests use mocks so that no real tika-server processes are ever killed,
and the tests are hermetic and cross-platform safe (the popen/grep is Unixy
but we mock it).

Tests cover:
- Normal case: no tika-server running -> still prints "success" (current behavior)
- Kill case: processes found -> kills them with SIGKILL and prints success
- Failure case: exception during popen/kill -> prints "Failed to kill"
"""

import unittest
from unittest.mock import patch, MagicMock, call
import signal
import sys
import os
import re


def _extract_killserver_function(script_path):
    """Extract ONLY the killserver() def source from a script and return a
    callable. This avoids parsing the entire file (some scripts contain
    Python 2 'print' statements that are SyntaxError under Python 3).

    We exec the isolated function definition in a controlled namespace.
    """
    with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
        src = f.read()

    # Find the killserver def block (from 'def killserver():' up to next top-level def or EOF)
    match = re.search(
        r'(?ms)^def killserver\(\):.*?(?=^def |^if __name__|\Z)',
        src
    )
    if not match:
        raise RuntimeError(f"Could not locate killserver() in {script_path}")

    func_src = match.group(0).rstrip()

    # Provide the globals the function expects
    ns = {
        '__name__': '__killserver_test__',
        'os': os,
        'signal': signal,
    }

    exec(func_src, ns)
    return ns['killserver']


class TestKillserverJaccard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.killserver = _extract_killserver_function("tikasimilarity/distance/jaccard_similarity.py")

    def test_killserver_no_process_prints_success(self):
        with patch('os.popen') as mock_popen, \
             patch('builtins.print') as mock_print:
            mock_popen.return_value = iter([])  # no matching lines
            TestKillserverJaccard.killserver()
            mock_popen.assert_called_once_with("ps ax | grep tika-server | grep -v grep")
            # Current impl prints success even when nothing was killed
            mock_print.assert_called_with("Tika process successfully terminated")

    def test_killserver_kills_processes(self):
        fake_line = "  12345 ?        S      0:00 java -jar tika-server.jar"
        with patch('os.popen') as mock_popen, \
             patch('os.kill') as mock_kill, \
             patch('builtins.print') as mock_print:
            mock_popen.return_value = iter([fake_line])
            TestKillserverJaccard.killserver()
            mock_kill.assert_called_once_with(12345, signal.SIGKILL)
            # success printed after kills
            self.assertIn(
                call("Tika process successfully terminated"),
                mock_print.call_args_list
            )

    def test_killserver_handles_exception(self):
        with patch('os.popen') as mock_popen, \
             patch('builtins.print') as mock_print:
            mock_popen.side_effect = OSError("boom")
            TestKillserverJaccard.killserver()
            mock_print.assert_called_with("Failed to kill Tika process")


class TestKillserverCosine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.killserver = _extract_killserver_function("tikasimilarity/distance/cosine_similarity.py")

    def test_killserver_no_process_prints_success(self):
        with patch('os.popen') as mock_popen, \
             patch('builtins.print') as mock_print:
            mock_popen.return_value = iter([])
            TestKillserverCosine.killserver()
            mock_print.assert_called_with("Tika process successfully terminated")

    def test_killserver_kills_processes(self):
        fake_line = "9876  pts/0    Sl     0:01 /usr/bin/java -jar /tmp/tika-server-1.28.jar --port 9998"
        with patch('os.popen') as mock_popen, \
             patch('os.kill') as mock_kill, \
             patch('builtins.print') as mock_print:
            mock_popen.return_value = iter([fake_line])
            TestKillserverCosine.killserver()
            mock_kill.assert_called_once_with(9876, signal.SIGKILL)
            mock_print.assert_any_call("Tika process successfully terminated")

    def test_killserver_handles_exception(self):
        with patch('os.popen') as mock_popen, \
             patch('builtins.print') as mock_print:
            mock_popen.side_effect = Exception("pop fail")
            TestKillserverCosine.killserver()
            mock_print.assert_called_with("Failed to kill Tika process")


class TestKillserverEditValue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.killserver = _extract_killserver_function("tikasimilarity/distance/edit-value-similarity.py")

    def test_killserver_no_process_prints_success(self):
        with patch('os.popen') as mock_popen, \
             patch('builtins.print') as mock_print:
            mock_popen.return_value = iter([])
            TestKillserverEditValue.killserver()
            mock_print.assert_called_with("Tika process successfully terminated")

    def test_killserver_kills_processes(self):
        fake_lines = [
            "  42 S+     0:00 bash -c ps ax | grep tika-server | grep -v grep",
            " 7777 ?        Ssl    10:23 java -jar tika-server.jar",
        ]
        with patch('os.popen') as mock_popen, \
             patch('os.kill') as mock_kill, \
             patch('builtins.print') as mock_print:
            mock_popen.return_value = iter(fake_lines)
            TestKillserverEditValue.killserver()
            # Should have tried to kill the one that looks like it has pid 7777
            # (the first line is the grep itself, split()[0]=='42')
            self.assertEqual(mock_kill.call_count, 2)
            mock_kill.assert_any_call(42, signal.SIGKILL)
            mock_kill.assert_any_call(7777, signal.SIGKILL)
            mock_print.assert_any_call("Tika process successfully terminated")

    def test_killserver_handles_exception(self):
        with patch('os.popen') as mock_popen, \
             patch('builtins.print') as mock_print:
            mock_popen.side_effect = RuntimeError("no ps")
            TestKillserverEditValue.killserver()
            mock_print.assert_called_with("Failed to kill Tika process")


if __name__ == '__main__':
    unittest.main()
