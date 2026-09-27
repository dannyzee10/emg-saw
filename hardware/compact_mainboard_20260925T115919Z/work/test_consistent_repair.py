"""Lightweight regression checks; all build_ops subprocesses are mocked."""
import contextlib
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import consistent_repair as repair


def row(group, conn=''):
    return {'kind': 'TRACK', 'group': group, 'net': 'N', 'layer': 'Top Layer',
            'x1': '1', 'y1': '2', 'x2': '3', 'y2': '4', 'w': '0.2', 'conn': conn}


def checker(stdout, code=0, stderr=''):
    return subprocess.CompletedProcess(['build_ops.py'], code, stdout, stderr)


CLEAN = checker('PROBLEMS 0\nDROPPED_GROUPS 0 kept rows 1 of 1\n')
DROP = checker('PROBLEMS 1\nDROPPED_GROUPS 1 kept rows 1 of 2\n  DROP P1:target\n')


class ConsistentRepairTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='astra-consistent-')
        self.addCleanup(self.temporary.cleanup)
        directory = Path(self.temporary.name)
        self.paths = [directory / name for name in ('adds.csv', 'dels.csv', 'adds_OK.csv', 'dels_OK.csv')]
        repair.write_rows(self.paths[0], [row('P1:target')])
        repair.write_rows(self.paths[1], [row('original-victim')])

    def run_with(self, results):
        with patch.object(repair.subprocess, 'run', side_effect=results) as run:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as error:
                code = repair.main([str(path) for path in self.paths])
        return code, error.getvalue(), run.call_count

    def assert_no_final_outputs(self):
        self.assertFalse(self.paths[2].exists())
        self.assertFalse(self.paths[3].exists())

    def test_failed_checker_does_not_publish(self):
        code, error, calls = self.run_with([checker('', 1, 'geometry import failed')])
        self.assertEqual((code, calls), (1, 1))
        self.assertIn('geometry import failed', error)
        self.assert_no_final_outputs()

    def test_delete_mismatch_with_success_exit_does_not_publish(self):
        result = checker('PROBLEMS 1\n  via delete match 0 for fixture\nDROPPED_GROUPS 0 kept rows 1 of 1\n')
        code, error, calls = self.run_with([result])
        self.assertEqual((code, calls), (1, 1))
        self.assertIn('deletion mismatch', error)
        self.assert_no_final_outputs()

    def test_missing_summary_does_not_publish(self):
        code, error, calls = self.run_with([checker('unexpected empty check\n')])
        self.assertEqual((code, calls), (1, 1))
        self.assertIn('complete check summary', error)
        self.assert_no_final_outputs()

    def test_unresolved_problems_without_drops_do_not_publish(self):
        code, error, calls = self.run_with([checker('PROBLEMS 1\nDROPPED_GROUPS 0 kept rows 1 of 1\n')])
        self.assertEqual((code, calls), (1, 1))
        self.assertIn('without removable groups', error)
        self.assert_no_final_outputs()

    def test_legitimate_drop_restores_victim_and_requires_clean_recheck(self):
        repair.write_rows(self.paths[0], [row('P1:target'), row('P1v:reroute', 'repair|old.csv|original-victim'), row('P2:keep')])
        code, error, calls = self.run_with([DROP, CLEAN])
        self.assertEqual((code, calls, error), (0, 2, ''))
        self.assertEqual([r['group'] for r in repair.read_rows(self.paths[2])], ['P2:keep'])
        self.assertEqual(repair.read_rows(self.paths[3]), [])

    def test_no_clean_iteration_does_not_publish(self):
        code, error, calls = self.run_with([DROP] * repair.MAX_CHECKS)
        self.assertEqual((code, calls), (1, repair.MAX_CHECKS))
        self.assertIn('No clean check', error)
        self.assert_no_final_outputs()

    def test_failure_preserves_previous_output_files(self):
        self.paths[2].write_text('previous adds\n')
        self.paths[3].write_text('previous dels\n')
        code, _, _ = self.run_with([checker('', 1, 'failed')])
        self.assertEqual(code, 1)
        self.assertEqual(self.paths[2].read_text(), 'previous adds\n')
        self.assertEqual(self.paths[3].read_text(), 'previous dels\n')

    def test_extra_plan_staging_does_not_publish_extensionless_output_on_failure(self):
        self.paths[2] = self.paths[2].with_suffix('')
        extra = self.paths[0].parent / 'extra.csv'
        repair.write_rows(extra, [row('S1:stitch')])
        with patch.object(repair.subprocess, 'run', side_effect=[DROP, checker('', 1, 'recheck failed')]):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                code = repair.main([str(path) for path in self.paths] + [str(extra)])
        self.assertEqual(code, 1)
        self.assert_no_final_outputs()
        self.assertTrue(Path(str(self.paths[2]) + '.extra0.csv').exists())


if __name__ == '__main__':
    unittest.main()
