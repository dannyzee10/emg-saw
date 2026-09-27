"""Focused cases for an informational, export-precision copper inventory."""
import unittest

from astra_trace_shape_inventory import inventory


def track(net='SIG', layer='Top Layer', endpoints=(0, 0, 1, 0), width=.18):
    return dict(kind='TRACK', net=net, layer=layer, values=(*endpoints, width),
                source=f'{net}|{layer}|{endpoints}|{width}')


class TrackShapeInventoryTests(unittest.TestCase):
    def test_reverse_is_duplicate_but_different_width_layer_and_net_are_not(self):
        result = inventory([track(), track(endpoints=(1, 0, 0, 0)),
                            track(net='OTHER'), track(width=.2), track(layer='Bottom Layer')])
        self.assertEqual(5, result['free_copper_track_count'])
        self.assertEqual(1, result['exact_duplicate_group_count'])
        self.assertEqual(1, result['exact_duplicate_extra_count'])
        self.assertEqual([0, 1], [r['export_index'] for r in result['exact_duplicate_groups'][0]])

    def test_only_exact_export_zero_is_zero_length(self):
        result = inventory([track(endpoints=(1, 2, 1, 2)), track(endpoints=(1, 2, 1.0001, 2))])
        self.assertEqual(1, result['zero_length_count'])
        self.assertEqual(0, result['exact_duplicate_group_count'])

    def test_netless_copper_is_included_and_mechanical_overlay_are_excluded(self):
        result = inventory([track(net='-', layer='Mid Layer 4', endpoints=(1, 1, 1, 1)),
                            track(net='-', layer='Mechanical Layer 4'), track(layer='Top Overlay')])
        self.assertEqual(1, result['free_copper_track_count'])
        self.assertEqual(1, result['nonnet_copper_track_count'])
        self.assertEqual(1, result['zero_length_count'])
        self.assertEqual(2, result['excluded_non_copper_track_count'])

    def test_partial_overlap_is_not_exact_duplicate(self):
        result = inventory([track(), track(endpoints=(.5, 0, 1.5, 0))])
        self.assertEqual(0, result['exact_duplicate_group_count'])


if __name__ == '__main__':
    unittest.main()
