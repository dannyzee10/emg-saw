"""Seed wrapper tests with a mocked subprocess; no router or board geometry load."""
import contextlib
import csv
import io
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).with_name('astra_route_seed.py')
EXTRA = 'ASTRA_MCU_RX_REINFORCED_ADDS,ASTRA_UART_READY_ADDS'


class SeedPlansTests(unittest.TestCase):
    def run_seed(self, extra, inherited=''):
        with tempfile.TemporaryDirectory(prefix='seed_plans_') as temp:
            folder = Path(temp)
            work, evidence = folder / 'work', folder / 'evidence'
            work.mkdir()
            evidence.mkdir()
            (work / 'run_repair.py').write_text("PLANS = ['BASE']\nENV = {}\n")
            (evidence / 'GEOMETRY_C2_6L_BF.txt').write_text('synthetic fixture\n')
            (evidence / 'DRC_C2_6L_BF.json').write_text('{}')
            fields = ['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h']
            seed = evidence / 'seed.csv'
            with seed.open('w', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerow(dict(kind='TRACK', group='seed', net='TARGET', layer='Top Layer',
                                     x1=0, y1=0, x2=1, y2=0, w=0.2))

            def fake_router(cmd, env):
                Path(cmd[4]).write_text(seed.read_text())
                return subprocess.CompletedProcess(cmd, 0)

            argv = [str(SCRIPT), 'BF', 'FIXTURE', str(seed)]
            if extra is not None:
                argv.append('EXTRA_PLANS=' + extra)
            with (contextlib.chdir(work), patch.object(sys, 'argv', argv),
                  patch.dict('os.environ', {'EXTRA_PLANS': inherited}),
                  patch('subprocess.run', side_effect=fake_router) as run,
                  contextlib.redirect_stdout(io.StringIO())):
                try:
                    runpy.run_path(str(SCRIPT), run_name='__main__')
                except SystemExit as exc:
                    return str(exc), run.call_count, None, None
                manifest = json.loads((evidence / 'FIXTURE_PLANNING_ONLY' / 'MANIFEST.json').read_text())
                return None, run.call_count, run.call_args.args[0], manifest

    def test_requested_extra_plans_are_passed_and_recorded_in_order(self):
        error, calls, cmd, manifest = self.run_seed(EXTRA, inherited='IGNORED')
        self.assertIsNone(error)
        self.assertEqual(1, calls)
        expected = ['BASE', *EXTRA.split(',')]
        self.assertEqual(expected, manifest['routed_plans'])
        self.assertEqual([name + '.csv' for name in expected], [Path(p).name for p in cmd[6:]])

    def test_inherited_extra_plans_ignore_empty_csv_entries(self):
        error, calls, _, manifest = self.run_seed(None, inherited=',INHERITED,,')
        self.assertIsNone(error)
        self.assertEqual(1, calls)
        self.assertEqual(['BASE', 'INHERITED'], manifest['routed_plans'])

    def test_path_entries_are_rejected_before_subprocess(self):
        for bad in ('../escape', '..\\escape', 'C:escape', '/absolute', '..'):
            with self.subTest(bad=bad):
                error, calls, _, _ = self.run_seed(bad)
                self.assertIn('simple basenames', error)
                self.assertEqual(0, calls)


if __name__ == '__main__':
    unittest.main(verbosity=2)
