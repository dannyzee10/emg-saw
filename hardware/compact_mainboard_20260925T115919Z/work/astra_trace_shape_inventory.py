"""Informational inventory of exported free copper tracks; never edits CAD.

Equality is at the native text export's precision. Findings are candidates for
native inspection, not authorization to delete copper or a connectivity check.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re

from astra_verify_routing_delta import geometry


def copper_layer(layer):
    return layer in ('Top Layer', 'Bottom Layer') or bool(re.fullmatch(r'Mid Layer [1-9]\d*', layer))


def inventory(items):
    tracks, excluded, zero_length, groups = [], [], [], defaultdict(list)
    for export_index, item in enumerate(items):
        if item['kind'] != 'TRACK':
            continue
        if not copper_layer(item['layer']):
            excluded.append(item['source'])
            continue
        x1, y1, x2, y2, width = item['values']
        record = dict(export_index=export_index, net=item['net'], layer=item['layer'],
                      width_mm=width, endpoints_mm=[[x1, y1], [x2, y2]], source=item['source'])
        tracks.append(record)
        if (x1, y1) == (x2, y2):
            zero_length.append(record)
        # Reverse direction is the same segment, but net, layer and width must
        # also agree. Partial collinear overlaps are outside this exact scan.
        endpoints = tuple(sorted(((x1, y1), (x2, y2))))
        groups[(item['net'], item['layer'], width, endpoints)].append(record)
    duplicates = [records for records in groups.values() if len(records) > 1]
    return dict(
        free_copper_track_count=len(tracks),
        nonnet_copper_track_count=sum(t['net'] in ('', '-') for t in tracks),
        excluded_non_copper_track_count=len(excluded),
        excluded_non_copper_tracks=excluded,
        zero_length_count=len(zero_length), zero_length_tracks=zero_length,
        exact_duplicate_group_count=len(duplicates),
        exact_duplicate_extra_count=sum(len(group) - 1 for group in duplicates),
        exact_duplicate_groups=duplicates)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--geometry', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    source, output = Path(args.geometry).resolve(), Path(args.output).resolve()
    if source == output:
        parser.error('Output must not overwrite the input geometry')
    result = inventory(geometry(source)['free'])
    result.update(
        geometry=str(source), geometry_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        status='informational',
        limitations=[
            'Exact equality is only at the text export precision, not native internal coordinates.',
            'Includes every free copper TRACK regardless of net, excluding polygon members, footprint tracks and keepouts.',
            'Does not detect partial overlaps, arcs, clearances or prove connectivity; no deletion is recommended by this scan.'])
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items()
                      if key.endswith('_count') or key in ('status', 'geometry_sha256')}, indent=2))


if __name__ == '__main__':
    main()
