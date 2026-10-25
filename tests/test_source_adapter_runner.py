"""Offline boundary tests for the synthetic-only source-adapter runner."""
import contextlib
import io
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import run_source_adapter_fixture as runner
import check_source_adapter as worker


class SourceAdapterRunnerTests(unittest.TestCase):
    def test_cli_has_no_source_path_or_live_acquisition_option(self):
        for option in ('--data', '--live', '--country', '--approve'):
            with mock.patch.object(runner, 'run_fixture') as run, \
                    contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                runner.main([option, 'abstract'])
            run.assert_not_called()

    def test_process_failure_never_emits_private_payload_or_captured_output(self):
        failure = subprocess.CalledProcessError(1, ['private-marker'],
                                               output='private-marker', stderr='private-marker')
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(runner, 'run_fixture', side_effect=failure), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(runner.main([]), 1)
        self.assertEqual(out.getvalue(), '')
        self.assertEqual(err.getvalue(), runner.FAILURE + '\n')

    def test_worker_rejects_unisolated_startup_before_creating_input(self):
        with mock.patch.object(worker.sys, 'flags', SimpleNamespace(isolated=0, no_user_site=0)), \
                mock.patch.object(worker, 'make_full_fixture') as fixture:
            with self.assertRaises(ValueError):
                worker.run_fixture_worker()
        fixture.assert_not_called()

    def test_private_input_stays_in_pipe_and_failed_child_output_is_sanitized(self):
        out, err = io.StringIO(), io.StringIO()
        failure = subprocess.CalledProcessError(1, ['Rscript'],
                                               output='private-marker', stderr='private-marker')
        with mock.patch.object(worker.sys, 'flags', SimpleNamespace(isolated=1, no_user_site=1)), \
                mock.patch.object(worker.sys, 'dont_write_bytecode', True), \
                mock.patch.object(worker.sys, 'version_info', (3, 12, 14)), \
                mock.patch.object(worker.sys, 'argv', ['fixture-worker']), \
                mock.patch.object(worker, 'make_full_fixture', return_value=(b'a', b'b', b'c', {})), \
                mock.patch.object(worker, 'parse_sources', return_value={'abstract': 'private-marker'}), \
                mock.patch.object(worker.subprocess, 'run', side_effect=failure) as child, \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(worker.main(), 1)
        self.assertNotIn('private-marker', str(child.call_args.args[0]))
        self.assertIn('private-marker', child.call_args.kwargs['input'])
        self.assertEqual(out.getvalue(), '')
        self.assertEqual(err.getvalue(), worker.FAILURE + '\n')


if __name__ == '__main__':
    unittest.main()
