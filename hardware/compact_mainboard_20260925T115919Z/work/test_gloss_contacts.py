"""Small synthetic regressions; never load board geometry or launch native CAD."""
import contextlib
import csv
import io
import os
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch

from shapely.geometry import Point, box
import geom as G


NET, LAYER = 'GLOSS_TEST', 'Top Layer'
FIELDS = ['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w']


def track(a, b, layer=LAYER):
    obj = G.track(NET, layer, [a, b], 0.2)
    obj.src = ['TRACK', layer, NET, str(a[0]), str(a[1]), str(b[0]), str(b[1]), '0.2']
    return obj


def dogleg(dy=0):
    points = [(0, dy), (2, dy), (2, 2 + dy), (4, 2 + dy)]
    return [track(a, b) for a, b in zip(points, points[1:])]


def pad(x, y, layer=LAYER, radius=0.12):
    return G.Obj(Point(x, y).buffer(radius), NET, 'PAD', {layer})


class GlossContactTests(unittest.TestCase):
    def run_gloss(self, objects, routed):
        with tempfile.TemporaryDirectory(prefix='gloss_contacts_') as folder:
            plan, adds, dels = [Path(folder) / name for name in ('plan.csv', 'adds.csv', 'dels.csv')]
            with plan.open('w', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=FIELDS)
                writer.writeheader()
                for obj in routed:
                    s = obj.src
                    writer.writerow(dict(zip(FIELDS, ['TRACK', 'P1:test', NET, s[1], *s[3:8]])))
            output = io.StringIO()
            env = {key: value for key, value in os.environ.items()
                   if key not in ('BK13_ZONES', 'L5_RESERVED', 'WINDOW')}
            with (patch.object(G, 'load', return_value=(objects, {}, [])),
                  patch.object(G, 'BOARD', box(-10, -10, 30, 30)),
                  patch.object(G, 'ZONES', []), patch.object(G, 'FINE_REGIONS', {}),
                  patch.dict(os.environ, env, clear=True),
                  patch.object(sys, 'argv', ['gloss.py', str(adds), str(dels), str(plan)]),
                  contextlib.redirect_stdout(output)):
                runpy.run_path(str(Path(__file__).with_name('gloss.py')), run_name='__main__')
            with adds.open() as stream:
                added = list(csv.DictReader(stream))
            with dels.open() as stream:
                deleted = list(csv.DictReader(stream))
            return added, deleted, output.getvalue()

    def assert_contact_keeps_dogleg(self, contact, movable=False):
        chain = dogleg()
        added, deleted, output = self.run_gloss(chain + [contact], chain + ([contact] if movable else []))
        self.assertEqual([], added)
        self.assertEqual([], deleted)
        self.assertIn('skipped chains with unpreserved same-net contacts: 1', output)

    def test_interior_pad_is_preserved(self):
        self.assert_contact_keeps_dogleg(pad(2, 1))

    def test_interior_via_is_preserved(self):
        self.assert_contact_keeps_dogleg(G.via(NET, 2, 1, d=0.45))

    def test_fixed_interior_branch_is_preserved(self):
        self.assert_contact_keeps_dogleg(track((2, 1), (0.5, 1)))

    def test_movable_interior_branch_is_preserved(self):
        self.assert_contact_keeps_dogleg(track((2, 1), (0.5, 1)), movable=True)

    def test_pad_touching_copper_edge_without_centerline_contact_is_preserved(self):
        self.assert_contact_keeps_dogleg(pad(2.19, 1, radius=0.1))

    def test_near_endpoint_contact_without_guarantee_is_skipped(self):
        self.assert_contact_keeps_dogleg(pad(-0.18, 0, radius=0.1))

    def test_endpoint_pads_and_branch_still_allow_gloss(self):
        chain = dogleg()
        contacts = [pad(0, 0), pad(4, 2), track((0, 0), (-2, 0))]
        added, deleted, _ = self.run_gloss(chain + contacts, chain)
        self.assertEqual(2, len(added))
        self.assertEqual(3, len(deleted))
        self.assertEqual({'G1:GLOSS_TEST'}, {row['group'] for row in added + deleted})

    def test_other_layer_pad_does_not_block_gloss(self):
        chain = dogleg()
        added, deleted, _ = self.run_gloss(chain + [pad(2, 1, 'Bottom Layer')], chain)
        self.assertEqual(2, len(added))
        self.assertEqual(3, len(deleted))

    def test_via_at_existing_vertex_remains_an_anchor(self):
        chain = dogleg()
        added, deleted, _ = self.run_gloss(chain + [G.via(NET, 2, 0, d=0.45)], chain)
        self.assertEqual(1, len(added))
        self.assertEqual(2, len(deleted))
        self.assertEqual(('2.0', '0.0'), (added[0]['x1'], added[0]['y1']))
        self.assertEqual(('4.0', '2.0'), (added[0]['x2'], added[0]['y2']))

    def test_multiple_chains_keep_distinct_paired_add_delete_groups(self):
        chains = dogleg() + dogleg(10)
        added, deleted, _ = self.run_gloss(chains, chains)
        self.assertEqual({'G1:GLOSS_TEST', 'G2:GLOSS_TEST'}, {row['group'] for row in added})
        for group in {row['group'] for row in added}:
            self.assertEqual(2, sum(row['group'] == group for row in added))
            self.assertEqual(3, sum(row['group'] == group for row in deleted))

    def test_earlier_batch_additions_protect_later_chain_contacts(self):
        first = dogleg()
        points = [(2.5, 1), (3.5, 1), (3.5, -1), (5.5, -1)]
        second = [track(a, b) for a, b in zip(points, points[1:])]
        # The first replacement introduces a contact at (3, 1), inside the
        # second chain. Its later reroute must see the newly added copper.
        added, deleted, output = self.run_gloss(first + second, first + second)
        self.assertEqual(2, len(added))
        self.assertEqual(3, len(deleted))
        self.assertEqual({'G1:GLOSS_TEST'}, {row['group'] for row in added + deleted})
        self.assertIn('skipped chains with unpreserved same-net contacts: 1', output)


if __name__ == '__main__':
    unittest.main(verbosity=2)
