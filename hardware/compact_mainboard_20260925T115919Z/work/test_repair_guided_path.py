"""Exercise guided path handoff without importing or running router5/repair.

Only three function definitions are compiled from the selected source. Routing
responses and raster snapshots are tiny stand-ins; Shapely and split_group's
actual copper-distance selection are used. REPAIR_GUIDED_SOURCE can select a
different source basename for comparison without executing its top-level code.
"""
import ast
import os
from pathlib import Path
from types import SimpleNamespace
import unittest

from shapely.geometry import LineString, Point
from shapely.ops import unary_union


SOURCE = Path(__file__).with_name(os.environ.get('REPAIR_GUIDED_SOURCE', 'repair.py'))
VICTIM = 'old.csv|P1:blocker'
KEPT = 'old.csv|P2:other'


def track(net, layer, pts, width):
    return SimpleNamespace(geom=LineString(pts).buffer(width / 2), net=net, layers={layer})


def via(net, x, y, diameter, hole):
    return SimpleNamespace(geom=Point(x, y).buffer(diameter / 2), net=net, layers={'Top Layer', 'Bottom Layer'})


def result(points, vias=()):
    return ([('Top Layer', points)], list(vias), 0.2, 0.45, 0.2, False)


BROAD = result([(0, 0), (4, 0)])
VERIFIED = result([(0, 0), (0, 2), (4, 2), (4, 0)], [(2, 2)])


def fixture(responses, partial=0.35):
    names = {'fixed_path_victims', 'split_group', 'rows_for'}
    tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    if {node.name for node in functions} != names:
        raise AssertionError('Missing function in source under test')
    groups, entry_group, group_objs, original_entries = {}, {}, {}, []
    for group_name, ys in ((VICTIM, [0, 2, 5]), (KEPT, [7])):
        rows, entries, objects = [], [], []
        for y in ys:
            obj = track('BLOCKER', 'Top Layer', [(2, y - 0.05), (2, y + 0.05)], 0.1)
            entry = (obj.geom, obj.net, 'Top Layer')
            entries.append(entry)
            objects.append(obj)
            rows.append({'group': group_name, 'marker_y': y})
            entry_group[id(entry)] = group_name
        groups[group_name] = {'rows': rows, 'entries': entries, 'net': 'BLOCKER'}
        group_objs[group_name] = objects
        original_entries.extend(entries)
    router = SimpleNamespace(copper_objs=list(original_entries), VIP=False,
                             split_at_regions=lambda p, q: [(p, q)])
    responses = iter(responses)
    calls = []

    def route_conn(net, a, b):
        calls.append([id(entry) for entry in router.copper_objs])
        response = next(responses)
        if isinstance(response, Exception):
            raise response
        return response

    def restore(state):
        router.copper_objs[:] = state

    def rip_names(names):
        router.copper_objs[:] = [entry for entry in router.copper_objs if entry_group[id(entry)] not in names]

    namespace = dict(R=router, G=SimpleNamespace(track=track, via=via, required=lambda a, b: 0.2),
                     groups=groups, entry_group=entry_group, dead_groups=set(), LAST_PATH=[None], LAST_PLANE=[''],
                     PARTIAL=partial, _nsplit=[0], unary_union=unary_union, route_conn=route_conn,
                     objs_of_group=group_objs.__getitem__, snap=lambda: list(router.copper_objs),
                     restore=restore, rip_names=rip_names)
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(SOURCE), 'exec'), namespace)
    return namespace, calls, original_entries


class GuidedPathTests(unittest.TestCase):
    def diagnose(self, namespace):
        return namespace['fixed_path_victims']('TARGET', {}, {}, (-1, -1, 5, 8))

    def assert_restored(self, namespace, original):
        self.assertEqual([id(entry) for entry in original], [id(entry) for entry in namespace['R'].copper_objs])

    def test_partial_rip_uses_verified_corridor_at_both_requested_distances(self):
        for partial in (0.35, 0.5):
            with self.subTest(partial=partial):
                ns, calls, original = fixture([(BROAD, 'broad route'), (VERIFIED, 'verified route')], partial)
                hits, _, rows = self.diagnose(ns)
                self.assertEqual([VICTIM], hits)
                self.assertEqual([], calls[0])
                self.assertEqual([id(entry) for entry in ns['groups'][KEPT]['entries']], calls[1])
                self.assert_restored(ns, original)
                selected = ns['split_group'](VICTIM, ns['LAST_PATH'][0])
                self.assertEqual([2], [row['marker_y'] for row in ns['groups'][selected]['rows']])
                self.assertEqual([0, 5], [row['marker_y'] for row in ns['groups'][VICTIM]['rows']])
                self.assertEqual(4, len(rows))

    def test_returned_rows_and_path_include_verified_via_envelope(self):
        ns, _, _ = fixture([(BROAD, 'broad route'), (VERIFIED, 'verified route')])
        _, _, rows = self.diagnose(ns)
        self.assertEqual(1, sum(row['kind'] == 'VIA' for row in rows))
        self.assertTrue(ns['LAST_PATH'][0].covers(Point(2, 2.2)))
        self.assertFalse(ns['LAST_PATH'][0].covers(Point(2, 0)))

    def test_later_successful_verification_sets_path(self):
        ns, calls, original = fixture([(BROAD, 'broad route'), (None, 'no path'), (VERIFIED, 'verified route')])
        hits, why, _ = self.diagnose(ns)
        self.assertEqual([VICTIM], hits)
        self.assertIn('tol 0.25', why)
        self.assertEqual(3, len(calls))
        self.assertTrue(ns['LAST_PATH'][0].covers(Point(2, 2)))
        self.assert_restored(ns, original)

    def test_failed_verifications_leave_no_usable_partial_corridor(self):
        ns, calls, original = fixture([(BROAD, 'broad route')] + [(None, 'no path')] * 4)
        hits, why, _ = self.diagnose(ns)
        self.assertIsNone(hits)
        self.assertIsNone(ns['LAST_PATH'][0])
        self.assertIn('NOT reproducible', why)
        self.assertEqual(5, len(calls))
        self.assert_restored(ns, original)

    def test_verification_error_restores_state_and_leaves_no_corridor(self):
        ns, _, original = fixture([(BROAD, 'broad route'), RuntimeError('route failure')])
        with self.assertRaisesRegex(RuntimeError, 'route failure'):
            self.diagnose(ns)
        self.assertIsNone(ns['LAST_PATH'][0])
        self.assert_restored(ns, original)

    def test_already_connected_verification_has_no_stale_path(self):
        connected = ([], [], 0, 0, 0, False)
        ns, _, original = fixture([(BROAD, 'broad route'), (connected, 'already connected')])
        _, _, rows = self.diagnose(ns)
        self.assertEqual([], rows)
        self.assertIsNone(ns['LAST_PATH'][0])
        self.assert_restored(ns, original)


if __name__ == '__main__':
    unittest.main(verbosity=2)
