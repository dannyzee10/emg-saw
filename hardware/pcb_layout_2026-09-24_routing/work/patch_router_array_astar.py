import re
P = r'C:\Users\PMLS\Desktop\emg-saw\.claude\worktrees\pcb-routing-0925\hardware\pcb_layout_2026-09-24_routing\work\router4.py'
s = open(P, encoding='utf-8').read()

# ---- 1) array-based A*: flat numpy best/parent arrays, compact heap entries (f, g, idx, dir)
a0 = s.index('def astar(free, via_ok, starts, goals, lcost, allowed, max_expand=None):')
a1 = s.index('def to_segments(path, W):')
new_astar = '''def astar(free, via_ok, starts, goals, lcost, allowed, max_expand=None):
    """A* over (layer, x, y) cells of the window.  State lives in flat numpy arrays and the heap holds
    compact (f, g, idx, dir) tuples, so memory stays bounded by the window size and max_expand."""
    ny, nx = via_ok.shape
    plane = ny * nx
    if max_expand is None:
        max_expand = min(600000, 6 * plane)
    gx = sum(g[1] for g in goals) / len(goals); gy = sum(g[2] for g in goals) / len(goals)
    lc = [lcost[L] for L in LAYERS]
    minc = min(lc[i] for i, L in enumerate(LAYERS) if L in allowed)
    hk = RES * minc * 0.95
    frees = [free[L] for L in LAYERS]
    lays = [i for i, L in enumerate(LAYERS) if L in allowed]
    best = np.full(len(LAYERS) * plane, np.inf, np.float64)
    parent = np.full(len(LAYERS) * plane, -1, np.int64)
    closed = np.zeros(len(LAYERS) * plane, bool)
    goal = np.zeros(len(LAYERS) * plane, bool)
    for L, ix, iy in goals:
        goal[L * plane + iy * nx + ix] = True
    openq = []
    for L, ix, iy in starts:
        i = L * plane + iy * nx + ix
        best[i] = 0.0
        heapq.heappush(openq, (math.hypot(ix - gx, iy - gy) * hk, 0.0, i, -1))
    n = 0
    while openq:
        f, g, i, d_in = heapq.heappop(openq)
        if closed[i] or g > best[i]:
            continue
        closed[i] = True
        if goal[i]:
            path = []
            while i >= 0:
                L, r = divmod(int(i), plane); iy, ix = divmod(r, nx)
                path.append((L, ix, iy)); i = parent[i]
            return path[::-1]
        n += 1
        if n > max_expand:
            return None
        L, r = divmod(int(i), plane); iy, ix = divmod(r, nx)
        fr = frees[L]; mult = lc[L]; base = L * plane
        for k, (dx, dy, c) in enumerate(DIRS):
            jx, jy = ix + dx, iy + dy
            if 0 <= jx < nx and 0 <= jy < ny and fr[jy, jx]:
                if dx and dy and not (fr[iy, jx] and fr[jy, ix]):
                    continue
                j = base + jy * nx + jx
                if closed[j]:
                    continue
                ng = g + c * RES * mult + (TURN if (d_in >= 0 and k != d_in) else 0.0)
                if ng < best[j]:
                    best[j] = ng; parent[j] = i
                    heapq.heappush(openq, (ng + math.hypot(jx - gx, jy - gy) * hk, ng, j, k))
        if via_ok[iy, ix]:
            for L2 in lays:
                if L2 != L and frees[L2][iy, ix]:
                    j = L2 * plane + iy * nx + ix
                    ng = g + VIA_COST
                    if not closed[j] and ng < best[j]:
                        best[j] = ng; parent[j] = i
                        heapq.heappush(openq, (ng + math.hypot(ix - gx, iy - gy) * hk, ng, j, -1))
    return None


'''
s = s[:a0] + new_astar + s[a1:]

# ---- 2) incremental plan file + resume: every routed connection is appended (with its connection key)
#         to evidence/ROUTE_PARTIAL<tag>.csv as soon as it is routed; RESUME=<csv> pre-loads such a file.
FIELDS = "['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h', 'conn']"
old_rp = s[s.index('def run_pass(conns):'):s.index('def key(c):')]
new_rp = '''def stamp_rows(rows):
    for r in rows:
        if r['kind'] == 'TRACK':
            w = float(r['w'])
            g = LineString([(float(r['x1']), float(r['y1'])), (float(r['x2']), float(r['y2']))]).buffer(w / 2, 8)
            stamp(g, r['net'], [r['layer']]); copper_objs.append((g, r['net'], {r['layer']}))
        else:
            x, y, vd, vh = float(r['x1']), float(r['y1']), float(r['d']), float(r['h'])
            g = Point(x, y).buffer(vd / 2, 16)
            stamp(g, r['net'], LAYERS); copper_objs.append((g, r['net'], set(LAYERS)))
            win, m = patch(Point(x, y).buffer(vh / 2, 12))
            holes[win[0]:win[1], win[2]:win[3]] |= m


def run_pass(conns, partial_path, preload=()):
    reset_state()
    rows, failed = list(preload), []
    done = {r['conn'] for r in preload}
    stamp_rows(preload)
    t0 = time.time()
    pf = open(partial_path, 'w', newline='')
    pw = csv.DictWriter(pf, fieldnames=''' + FIELDS + ''')
    pw.writeheader(); pw.writerows(rows); pf.flush()
    for k, (net, a, b) in enumerate(conns):
        ck = '|'.join(key((net, a, b)))
        if ck in done:
            continue
        res, why = route_one(net, a, b)
        if not res:
            failed.append((net, a, b, why)); continue
        segs, vias, w, vd, vh = res
        new = []
        for L, pts in segs:
            for p, q in zip(pts, pts[1:]):
                for pp, qq in split_at_regions(p, q):
                    new.append({'kind': 'TRACK', 'group': f'R{k}:{net}', 'net': net, 'layer': L, 'x1': round(pp[0], 4), 'y1': round(pp[1], 4), 'x2': round(qq[0], 4), 'y2': round(qq[1], 4), 'w': w, 'd': '', 'h': '', 'conn': ck})
        for x, y in vias:
            new.append({'kind': 'VIA', 'group': f'R{k}:{net}', 'net': net, 'layer': 'Multi Layer', 'x1': round(x, 4), 'y1': round(y, 4), 'x2': '', 'y2': '', 'w': '', 'd': vd, 'h': vh, 'conn': ck})
        stamp_rows(new)
        rows += new
        pw.writerows(new); pf.flush()
        if k % 25 == 0:
            print(f'  {k + 1}/{len(conns)} failed {len(failed)} t={time.time() - t0:.0f}s', flush=True)
    pf.close()
    return rows, failed


'''
s = s.replace(old_rp, new_rp)

old_main_loop = s[s.index('    best = None\n    hard = []'):s.index('    rows, failed = best\n')]
new_main_loop = '''    best = None
    hard = []
    tag = os.environ.get('OUT_TAG', '')
    preload = []
    if os.environ.get('RESUME'):
        preload = [r for r in csv.DictReader(open(os.environ['RESUME'])) if r.get('conn')]
        print(f'resume: {len(preload)} rows / {len({r["conn"] for r in preload})} connections pre-loaded', flush=True)
    for p in range(passes):
        hk = {key(c) for c in hard}
        order = [c for c in conns if key(c) in hk] + [c for c in conns if key(c) not in hk]
        t0 = time.time()
        rows, failed = run_pass(order, G.HERE + f'evidence/ROUTE_PARTIAL{tag}_p{p + 1}.csv', preload if p == 0 else ())
        print(f'PASS {p + 1}: routed {len(conns) - len(failed)}/{len(conns)} failed {len(failed)} ({time.time() - t0:.0f}s)', flush=True)
        if best is None or len(failed) < len(best[1]):
            best = (rows, failed)
        if not failed:
            break
        newhard = [(n, a, b) for n, a, b, w in failed]
        hard = newhard + [c for c in hard if key(c) not in {key(x) for x in newhard}]
'''
s = s.replace(old_main_loop, new_main_loop)
s = s.replace("""    tag = os.environ.get('OUT_TAG', '')
    with open(G.HERE + f'evidence/ROUTE_PLAN{tag}.csv', 'w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=['kind', 'group', 'net', 'layer', 'x1', 'y1', 'x2', 'y2', 'w', 'd', 'h'])""",
"""    with open(G.HERE + f'evidence/ROUTE_PLAN{tag}.csv', 'w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=""" + FIELDS + """)""")
open(P, 'w', encoding='utf-8').write(s)
print('patched')
