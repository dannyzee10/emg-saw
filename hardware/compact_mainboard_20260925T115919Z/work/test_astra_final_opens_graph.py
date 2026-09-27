"""Tiny fixtures for detecting newly introduced thin power-feed dependencies."""
from types import SimpleNamespace
import unittest
from shapely.geometry import LineString, Point
from astra_check_final_opens_graph import preserved, power_thresholds


def copper(shape):
    return SimpleNamespace(geom=shape, layers={'Bottom Layer'})


class PowerConnectivityTests(unittest.TestCase):
    def setUp(self):
        self.source = (0, copper(Point(0, 0).buffer(.225)))
        self.sink = (1, copper(Point(2, 0).buffer(.30)))
        self.original = (2, copper(LineString([(0, 0), (2, 0)]).buffer(.20)))
        self.thin = ('new_thin', copper(LineString([(0, 0), (1, 0)]).buffer(.15)))
        self.wide = ('new_wide', copper(LineString([(1, 0), (2, 0)]).buffer(.20)))
        self.reinforcement = ('new_feed', copper(LineString([(0, 0), (1, 0)]).buffer(.20)))
        self.before = [self.source, self.sink, self.original]

    def test_normal_graph_passes_but_excluding_thin_feed_detects_regression(self):
        after = [self.source, self.sink, self.thin, self.wide]
        self.assertEqual(preserved(self.before, after, {2})[2], [])
        wide_after = [self.source, self.sink, self.wide]
        self.assertEqual(preserved(self.before, wide_after, {2})[2], [[0, 1]])

    def test_direct_wide_reinforcement_restores_preserved_power_path(self):
        wide_after = [self.source, self.sink, self.wide, self.reinforcement]
        self.assertEqual(preserved(self.before, wide_after, {2})[2], [])

    def test_existing_thin_dependency_does_not_create_false_wide_path_claim(self):
        wide_before = [self.source, self.sink]
        wide_after = [self.source, self.sink, self.wide]
        self.assertEqual(preserved(wide_before, wide_after, set())[2], [])

    def test_thresholds_include_original_feeds_wider_and_narrower_than_040(self):
        old = [(0, SimpleNamespace(kind='PAD')),
               (1, SimpleNamespace(kind='TRACK')), (2, SimpleNamespace(kind='TRACK'))]
        self.assertEqual(power_thresholds(old, {1:.3, 2:.9}), [.3,.4,.9])


if __name__ == '__main__':
    unittest.main()
