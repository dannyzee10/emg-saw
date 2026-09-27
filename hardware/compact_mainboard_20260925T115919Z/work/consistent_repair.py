"""Check repair.py output, dropping failed repairs together with victim reroutes.

usage: <build_ops env> python consistent_repair.py ADDS.csv DELS.csv OUT_ADDS.csv OUT_DELS.csv [EXTRA_PLAN.csv ...]
EXTRA_PLAN rows (e.g. plane stitches computed on the same geometry) are checked together.
Final output files are written only after a successful check reports PROBLEMS 0.
This helper understands repair.py P<k>/P<k>v ownership, not gloss.py deletion groups.
"""
import csv
from pathlib import Path
import re
import subprocess
import sys

FIELDS = ['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h', 'conn', 'relax']
MAX_CHECKS = 8


class RepairCheckError(RuntimeError):
    pass


def read_rows(path):
    with open(path, newline='') as source:
        return list(csv.DictReader(source))


def write_rows(path, rows):
    with open(path, 'w', newline='') as output:
        writer = csv.DictWriter(output, fieldnames=FIELDS, extrasaction='ignore', restval='')
        writer.writeheader()
        writer.writerows(rows)


def repair_id(group):
    return re.sub(r'v$', '', group.split(':')[0])


def checked_drops(result):
    """--drop-bad deliberately returns 0 for removable geometric problems."""
    if result.returncode != 0:
        diagnostic = '\n'.join(s.strip() for s in (result.stdout, result.stderr) if s.strip())
        raise RepairCheckError(f'build_ops failed (exit {result.returncode})\n{diagnostic}')
    if 'delete match' in result.stdout:
        raise RepairCheckError('build_ops reported a deletion mismatch\n' + result.stdout.strip())
    problems = re.findall(r'^PROBLEMS\s+(\d+)\s*$', result.stdout, re.M)
    totals = re.findall(r'^DROPPED_GROUPS\s+(\d+)\s+kept rows\b', result.stdout, re.M)
    drops = [line.strip()[5:].strip() for line in result.stdout.splitlines()
             if line.strip().startswith('DROP ')]
    if len(problems) != 1 or len(totals) != 1:
        raise RepairCheckError('build_ops did not return a complete check summary\n' + result.stdout.strip())
    problem_count, drop_count = int(problems[0]), int(totals[0])
    if drop_count != len(drops) or len(set(drops)) != len(drops) or any(not group for group in drops):
        raise RepairCheckError('build_ops returned an inconsistent dropped-group summary')
    if problem_count and not drops:
        raise RepairCheckError(f'build_ops reported {problem_count} problems without removable groups')
    if not problem_count and drops:
        raise RepairCheckError('build_ops reported dropped groups despite PROBLEMS 0')
    return drops


def make_consistent(adds_in, dels_in, out_a, out_d, extra):
    adds, dels = read_rows(adds_in), read_rows(dels_in)
    extra = list(extra)
    tmp_a, tmp_d = out_a + '.tmp.csv', out_d + '.tmp.csv'
    for iteration in range(MAX_CHECKS):
        write_rows(tmp_a, adds)
        write_rows(tmp_d, dels)
        result = subprocess.run(
            [sys.executable, 'build_ops.py', tmp_a] + extra
            + ['--del', tmp_d, '--drop-bad', out_a + '.chk.csv'],
            capture_output=True, text=True)
        drops = checked_drops(result)
        print(f'iteration {iteration}: dropped groups {len(drops)}')
        if not drops:  # checked_drops also requires PROBLEMS 0 here.
            break
        ids = {repair_id(group) for group in drops if group.startswith('P')}
        victims = {row['conn'].split('|', 2)[2] for row in adds
                   if repair_id(row['group']) in ids and row['conn'].startswith('repair|')}
        adds = [row for row in adds if repair_id(row['group']) not in ids and row['group'] not in drops]
        dels = [row for row in dels if row['group'] not in victims]
        # A dropped extra-plan group (stitch) is removed from its plan copy.
        for index, path in enumerate(extra):
            rows = [row for row in read_rows(path) if row['group'] not in drops]
            copied = str(Path(out_a).with_suffix('')) + f'.extra{index}.csv'
            write_rows(copied, rows)
            extra[index] = copied
        print(f'  removed repairs {sorted(ids)}; victims kept {len(victims)}')
    else:
        raise RepairCheckError(f'No clean check after {MAX_CHECKS} iterations; final outputs not written')

    # No final _OK output is created or overwritten until the checker succeeds.
    write_rows(out_a, adds)
    write_rows(out_d, dels)
    print(f'final: adds {len(adds)} rows, dels {len(dels)} rows; extra plans: {extra}')


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) < 4:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        make_consistent(*args[:4], args[4:])
    except (RepairCheckError, OSError, csv.Error, KeyError, IndexError) as exc:
        print(f'ABORTED: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
