"""Candidate C2 placement planner (offline aid; the native Altium write, save/reopen readback and DRC are the evidence).

Floorplan (x-ray, viewed from Top), board (10,10)-(10+L,10+H):
  ANALOG half along the BK13 edge (both faces):
    Top    : five BK13 sockets at PITCH, each channel's INA/RDD/INA-feedback input stage (B template, unchanged
             internally), J_REF, the five 68R VREF branch resistors beside socket pin 8.
    Bottom : U1/U2/U3 as package-aware groups directly under their own channels (servo and post-amp networks at the
             op-amp pins that serve them; only the low-impedance INA_OUT and Vservo nodes cross the board), U1's reference
             divider/filter beside its VREF-buffer pins, R_ref by J_REF, DNP DRL provisions under the sockets.
  DIGITAL/POWER half (both faces):
    Top    : USB-C + button (left edge), service column (Tag-Connect TC2030-NL, battery header, remote-NTC terminals,
             charge LED), ST67 module (antenna edge), STM32 + ADC/VCAP/bypass + ADC RC (B local layouts, rigid).
    Bottom : charger (UP1 under the USB-C shell), converter cell (B hot loop, flipped whole), supervisor, gauge, LDO at
             the power/analog boundary, pushbutton controller under the MCU, flat test pads, solder jumper, UART links.
usage: python plan_C2.py [L H PITCH]
"""
import csv, json, math, os, sys
from collections import defaultdict
from c2lib import load_b, place, group_transform, bbox_of, render, EV, HERE
from c2fit import conflicts, find_spot

L, H, PITCH = (float(a) for a in sys.argv[1:4]) if len(sys.argv) > 3 else (59.1, 36.0, 10.8)
X0, Y0 = 10.0, 10.0
X1, Y1 = X0 + L, Y0 + H
OUTLINE = (X0, Y0, X1, Y1)
B = load_b()
out = {}
log = []
EDGE_EXEMPT = {'J_USB_C', 'U_WIFI1'}


def put(recs):
    for d, r in recs.items():
        assert d not in out, 'placed twice: ' + d
        r['proxy'] = B[d]['proxy'] if d in B else False
        out[d] = r


def rec_at(d, x, y, rot, side, src=None):
    """record for part d with its PAD-CENTROID at (x, y)"""
    p = (src or B)[d]
    probe = place(p, 0.0, 0.0, rot, side)
    cx = sum(q['x'] for q in probe['pads']) / len(probe['pads'])
    cy = sum(q['y'] for q in probe['pads']) / len(probe['pads'])
    r = place(p, x - cx, y - cy, rot, side)
    r['proxy'] = p.get('proxy', False)
    return r


def at(d, x, y, rot, side, src=None):
    put({d: rec_at(d, x, y, rot, side, src)})


def rot_for(d, horizontal, side, pad1_dir, src=None):
    p = (src or B)[d]
    for rot in ((0, 180) if horizontal else (90, 270)):
        probe = place(p, 0.0, 0.0, rot, side)
        pads = {q['num']: q for q in probe['pads']}
        a = pads.get('1') or list(pads.values())[0]
        other = [q for q in probe['pads'] if q is not a][0]
        vx, vy = a['x'] - other['x'], a['y'] - other['y']
        if {'L': vx < 0, 'R': vx > 0, 'U': vy > 0, 'D': vy < 0}[pad1_dir]:
            return rot
    raise ValueError(d)


def at2(d, x, y, horizontal, side, pad1_dir):
    at(d, x, y, rot_for(d, horizontal, side, pad1_dir), side)


# ------------------------------------------------------------------ synthetic footprints for the approved service change
def synth(name, pads, bodies, hmax=0.0):
    """pads: list of (num, net, x, y, w, h, layer, hole); local coords, origin (0,0), Top"""
    P = []
    for num, net, x, y, w, h, layer, hole in pads:
        P.append({'num': num, 'net': net, 'layer': layer, 'x': x, 'y': y, 'bx0': x - w / 2, 'by0': y - h / 2, 'bx1': x + w / 2,
                  'by1': y + h / 2, 'hole': hole})
    xs = [q['bx0'] for q in P] + [b[0] for b in bodies]; xe = [q['bx1'] for q in P] + [b[2] for b in bodies]
    ys = [q['by0'] for q in P] + [b[1] for b in bodies]; ye = [q['by1'] for q in P] + [b[3] for b in bodies]
    return {'designator': name, 'x': 0.0, 'y': 0.0, 'rot': 0.0, 'side': 'Top', 'pads': P, 'bodies': bodies, 'proxy': False,
            'bx0': min(xs), 'by0': min(ys), 'bx1': max(xe), 'by1': max(ye), 'hmax': hmax}


SYN = {}
# Tag-Connect TC2030-IDC-NL-FP rev B (official drawing): pads 0.787 on 1.27 grid, 1-3-5 lower row, 2-4-6 upper row;
# NPTH alignment holes 0.991 at (-2.54,0) and (+2.54,+-1.016).  Pad numbers carry the J_SWD schematic pins at the
# ARM-Cortex TC2030-CTX positions: TC1 VTref=pin1, TC2 SWDIO=pin2, TC3 nRESET=pin5, TC4 SWCLK=pin4, TC5 GND=pin3, TC6 SWO=nc.
tc = [('1', '3V3_DIG', -1.27, -0.635), ('2', 'MCU_SWDIO', -1.27, 0.635), ('5', 'MCU_NRST', 0.0, -0.635),
      ('4', 'MCU_SWCLK', 0.0, 0.635), ('3', 'GND', 1.27, -0.635), ('', '-', 1.27, 0.635)]
SYN['J_SWD'] = synth('J_SWD', [(n, net, x, y, 0.787, 0.787, 'Top Layer', 0.0) for n, net, x, y in tc] +
                     [('H1', '-', -2.54, 0.0, 0.991, 0.991, 'Multi Layer', 0.991), ('H2', '-', 2.54, 1.016, 0.991, 0.991, 'Multi Layer', 0.991),
                      ('H3', '-', 2.54, -1.016, 0.991, 0.991, 'Multi Layer', 0.991)], [[-4.953, -3.048, 4.953, 3.048]])
TC_FACE = (9.906, 6.096)      # plug face on the mating side: no other bodies under it (also its body/courtyard, Mech15)
for tpn, net in (('TP_WIFI_UART_RX', 'WIFI_UART_RX'), ('TP_WIFI_UART_TX', 'WIFI_UART_TX'), ('TP_GND', 'GND'), ('TP_WIFI_BOOT', 'WIFI_BOOT'),
                 ('TP_MCU_BOOT0', 'MCU_BOOT0'), ('TP_WIFI_CHIP_EN', 'WIFI_CHIP_EN')):
    SYN[tpn] = synth(tpn, [('TP', net, 0.0, 0.0, 1.2, 1.2, 'Top Layer', 0.0)], [[-0.8, -0.8, 0.8, 0.8]])   # flat probe pad; courtyard = extent
SYN['JP_WIFI_BOOT'] = synth('JP_WIFI_BOOT', [('1', 'NetJP_WIFI_BOOT_1', -0.6, 0.0, 0.9, 1.2, 'Top Layer', 0.0),
                                             ('2', 'WIFI_BOOT', 0.6, 0.0, 0.9, 1.2, 'Top Layer', 0.0)], [[-1.2, -0.8, 1.2, 0.8]])  # solder jumper
for k, v in SYN.items():
    v['group'] = 'SERVICE'; v['sheet'] = B[k]['sheet']; v['src_uid'] = B[k]['src_uid']; v['footprint'] = 'NEW'


def put_syn(d, x, y, rot, side):
    r = place(SYN[d], x, y, rot, side)
    r['proxy'] = False; r['group'] = 'SERVICE'
    out[d] = r
    return r


# ------------------------------------------------------------------ zones (functional separation in 3D)
ANALOG_GROUPS = {'AFE'}
def is_analog(r):
    return B.get(r['designator'], r).get('group') in ANALOG_GROUPS or r['designator'].startswith(('FP:TP_GND_ANA', 'FP:TP_VREF'))


ZONE_ANALOG_Y = Y0 + 13.6        # analog band top (Top side); Bottom analog zone limit is set per module below
ZONES = []

# ------------------------------------------------------------------ ANALOG half: sockets + input stages (Top)
JY = Y0 + 2.2
JX = [X0 + 8.7 + i * PITCH for i in range(5)]
BJ = {n: (B['J_FPC%d' % n]['x'], B['J_FPC%d' % n]['y']) for n in range(1, 6)}
for n in range(1, 6):
    mem = ['J_FPC%d' % n, 'INA%d' % n, 'RDD%d' % (3 * n - 2), 'RDD%d' % (3 * n - 1), 'RDD%d' % (3 * n), 'CCU%d' % (2 * n - 1), 'CCU%d' % (2 * n),
           'RH_%d' % n, 'RL_%d' % n]
    put(group_transform(B, mem, 'T', JX[n - 1] - BJ[n][0], JY - BJ[n][1]))
for n in range(1, 6):
    at2('R_VREF%d' % n, JX[n - 1] + 3.9, JY + 0.2, False, 'Top', 'D')      # 68R branch right beside socket pin 8
at('J_REF', X0 + 3.2, JY, 0, 'Top')

# ------------------------------------------------------------------ ANALOG half: op-amp modules (Bottom)
# U (TSSOP14) on Bottom rot 0, viewed from Top: pins 1-7 LEFT (pin1 low), 8-14 RIGHT (pin8 high)
#   left : 1 VOUT_a, 2 NetCH_a, 3 VREF_A, 4 V+, 5 VREF_A, 6 NetCservo_a, 7 Vservo_a  -> channel a: post-amp low, servo high
#   right: 8 VOUT_b, 9 NetCH_b, 10 VREF_A, 11 GND, 12 VREF_A, 13 NetCservo_b, 14 Vservo_b -> channel b: post-amp high, servo low
# rot 180 puts pins 1-7 on the RIGHT (pin1 high): U1, so channel 1 is right of it and its VREF buffers face the edge.
UY = JY + 8.2


def chan_left(n, xr, uy):
    at2('Cservo_%d' % n, xr - 3.35, uy + 2.75, True, 'Bottom', 'R')
    at2('Rservo_%d' % n, xr - 3.35, uy + 4.85, True, 'Bottom', 'R')
    at2('RG_%d' % n, xr - 0.55, uy - 1.55, False, 'Bottom', 'U')
    at2('CH_%d' % n, xr - 1.75, uy - 1.55, False, 'Bottom', 'U')
    at2('RGN_%d' % n, xr - 3.55, uy - 1.55, False, 'Bottom', 'U')
    at2('CL_%d' % n, xr - 2.65, uy - 4.35, True, 'Bottom', 'R')


def chan_right(n, xl, uy, servo_high):
    s = 1 if servo_high else -1
    at2('Cservo_%d' % n, xl + 3.35, uy + s * 2.75, True, 'Bottom', 'L')
    at2('Rservo_%d' % n, xl + 3.35, uy + s * 4.85, True, 'Bottom', 'L')
    at2('RG_%d' % n, xl + 0.55, uy - s * 1.55, False, 'Bottom', 'U')
    at2('CH_%d' % n, xl + 1.75, uy - s * 1.55, False, 'Bottom', 'U')
    at2('RGN_%d' % n, xl + 3.55, uy - s * 1.55, False, 'Bottom', 'U')
    at2('CL_%d' % n, xl + 2.65, uy - s * 4.35, True, 'Bottom', 'L')


x_u1 = JX[0] - 4.1
at('U1', x_u1, UY, 180, 'Bottom')
chan_right(1, x_u1 + 3.75, UY, servo_high=False)
at2('CU_11', x_u1 + 3.75 + 0.95, UY - 0.55, True, 'Bottom', 'L')
at2('CU_21', x_u1 + 3.75 + 2.70, UY - 0.55, True, 'Bottom', 'L')
XU = {}
for a, b, u, k in ((2, 3, 'U2', '2'), (4, 5, 'U3', '4')):
    xu = (JX[a - 1] + JX[b - 1]) / 2 + 1.2
    XU[u] = xu
    at(u, xu, UY, 0, 'Bottom')
    chan_left(a, xu - 3.75, UY)
    chan_right(b, xu + 3.75, UY, servo_high=False)
    at2('CU_1' + k, xu - 3.75 - 0.95, UY + 0.55, True, 'Bottom', 'R')
    at2('CU_2' + k, xu - 3.75 - 2.70, UY + 0.55, True, 'Bottom', 'R')

# ------------------------------------------------------------------ DIGITAL / POWER half, Top (B local layouts, rigid)
DY = Y1 - 50.0
DX = X1 - 0.35 - 79.67
BLOCK = [d for d in B if B[d]['group'] in ('WIFI', 'MCU', 'ADC_RC')] + ['FP:TP_VOUT_%d' % i for i in range(1, 6)]
put(group_transform(B, BLOCK, 'T', DX, DY))
put(group_transform(B, [d for d in B if B[d]['group'] == 'PB_CTRL'], 'T', DX, DY))      # stays under the MCU (Bottom)
put(group_transform(B, [d for d in B if B[d]['group'] == 'USB_IN'], 'T', 0.0, DY))
ub = bbox_of([out[d] for d in out if B[d]['group'] == 'USB_IN'])
at('PWR_BTN_N', X0 + 0.6 + 4.11, ub[1] - 0.35 - 2.83, 0, 'Top')
ANT = (41.19 + DX, 49.44 + DY, 53.47 + DX, 54.44 + DY)                                      # ST67 antenna keep-out (moved with WIFI)
ZONES.append(('ANTENNA', '*', ANT, lambda r: r['designator'] == 'U_WIFI1'))
COL = (ub[2], out['C_WIFI_VDDIO1']['bx0'])                                                  # service column between USB and ST67
log.append('service column x %.2f..%.2f' % COL)

VIAS = []      # through vias that travel with their part (x, y, dia, net, owner)
HOLES = []     # (rect, name) NPTH / alignment-pin holes: both sides clear
# ST67 module ground-pad thermal vias (native B geometry) travel with the WIFI block; parts on the other side must clear them
for l in open(os.path.join(EV, 'GEOMETRY_B_TRIAL.txt'), encoding='utf-8', errors='replace'):
    f = l.rstrip('\n').split('|')
    if f[0] == 'VIA':
        vx, vy = float(f[2]), float(f[3])
        if any(q['net'] == f[1] and q['bx0'] <= vx <= q['bx1'] and q['by0'] <= vy <= q['by1'] and (q['bx1'] - q['bx0']) * (q['by1'] - q['by0']) > 1
               for q in B['U_WIFI1']['pads']):
            VIAS.append((vx + DX, vy + DY, float(f[4]), f[1], 'U_WIFI1'))
log.append('ST67 thermal vias carried: %d' % len([v for v in VIAS if v[4] == 'U_WIFI1']))
BOT_ANALOG_TOP = max(r['by1'] for d, r in out.items() if r['side'] == 'Bottom' and B.get(d, {}).get('group') == 'AFE') + 0.25
log.append('bottom analog band up to y %.2f' % BOT_ANALOG_TOP)
ZONES.append(('ANALOG_TOP', 'Top', (X0, Y0, X1, ZONE_ANALOG_Y), is_analog))
ZONES.append(('ANALOG_BOTTOM', 'Bottom', (X0, Y0, X1, BOT_ANALOG_TOP), is_analog))
adc = bbox_of([out[d] for d in out if B.get(d, {}).get('group') == 'ADC_RC'])
ZONES.append(('ADC_CORNER_BOTTOM', 'Bottom', (adc[0] - 1, adc[1] - 1, adc[2] + 1, adc[3] + 1), is_analog))


def near(d, target, side, rots=(0, 90, 180, 270), rmax=7.0, step=0.2, src=None, extra_zones=()):
    def make(x, y, rot):
        if d in SYN:
            r = place(SYN[d], x, y, rot, side); r['proxy'] = False; r['group'] = 'SERVICE'
            return {d: r}
        return {d: rec_at(d, x, y, rot, side, src)}
    res = find_spot(make, out, OUTLINE, target, rmax=rmax, step=step, rots=rots, zones=ZONES + list(extra_zones), vias=VIAS,
                    holes=HOLES, edge_exempt=EDGE_EXEMPT)
    if res is None:
        log.append('NO SPOT for %s near %s' % (d, target))
        return None
    recs, x, y, rot = res
    for k, v in recs.items():
        out[k] = v
    return x, y, rot


def pin_xy(d, num):
    for q in out[d]['pads']:
        if q['num'] == num:
            return q['x'], q['y']
    raise KeyError((d, num))


def outward(d, num, dist):
    """point `dist` beyond pin `num` of placed part d, away from the part centre"""
    px, py = pin_xy(d, num)
    cx, cy = (out[d]['bx0'] + out[d]['bx1']) / 2, (out[d]['by0'] + out[d]['by1']) / 2
    vx, vy = px - cx, py - cy
    if abs(vx) >= abs(vy):
        return px + math.copysign(dist, vx), py
    return px, py + math.copysign(dist, vy)


def tc_zones(rec):
    """Tag-Connect: plug face keep-out on its own side, alignment-pin holes clear on both sides"""
    hs = [q for q in rec['pads'] if q['num'].startswith('H')]
    cx = sum(q['x'] for q in rec['pads'] if not q['num'].startswith('H')) / 6
    cy = sum(q['y'] for q in rec['pads'] if not q['num'].startswith('H')) / 6
    horiz = (max(q['x'] for q in hs) - min(q['x'] for q in hs)) > 3
    fw, fh = (TC_FACE[0], TC_FACE[1]) if horiz else (TC_FACE[1], TC_FACE[0])
    face = (cx - fw / 2, cy - fh / 2, cx + fw / 2, cy + fh / 2)
    holes = [((q['x'] - 0.8, q['y'] - 0.8, q['x'] + 0.8, q['y'] + 0.8), 'TC_' + q['num']) for q in hs]
    return face, holes


# ------------------------------------------------------------------ service column (Top): Tag-Connect, battery, NTC, LED
def tc_make(x, y, rot):
    r = place(SYN['J_SWD'], x, y, rot, 'Top'); r['proxy'] = False; r['group'] = 'SERVICE'
    return {'J_SWD': r}


best = None
for yy in [Y0 + 13.9 + 0.2 * k for k in range(60)]:
    for rot in (90, 270):
        cand = tc_make((COL[0] + COL[1]) / 2, yy + 5.0, rot)
        face, holes = tc_zones(cand['J_SWD'])
        if face[1] < ZONE_ANALOG_Y + 0.2:
            continue
        faceblock = [r for d, r in out.items() if r['side'] == 'Top' and any(
            not (b[2] <= face[0] or b[0] >= face[2] or b[3] <= face[1] or b[1] >= face[3]) for b in r['bodies'])]
        if faceblock:
            continue
        if conflicts(cand, out, OUTLINE, zones=ZONES, holes=[], edge_exempt=EDGE_EXEMPT, stop_at_first=True):
            continue
        hb = [h for h, n in holes]
        if any(any(not (b[2] + 0.25 <= h[0] or b[0] - 0.25 >= h[2] or b[3] + 0.25 <= h[1] or b[1] - 0.25 >= h[3]) for b in r['bodies'])
               for r in out.values() for h in hb):
            continue
        best = (cand, face, holes)
        break
    if best:
        break
assert best, 'no Tag-Connect spot'
out.update(best[0])
TC_FACE_RECT = best[1]
ZONES.append(('TC_PLUG_FACE', 'Top', TC_FACE_RECT, lambda r: r['designator'] == 'J_SWD'))
HOLES.extend(best[2])
log.append('Tag-Connect face %.2f,%.2f-%.2f,%.2f' % TC_FACE_RECT)
near('LED_CHG', ((COL[0] + COL[1]) / 2, Y1 - 2.4), 'Top', rots=(90, 270), rmax=4)
near('J_Li-Po', ((COL[0] + COL[1]) / 2 - 1.2, TC_FACE_RECT[3] + 4.0), 'Top', rots=(90, 270), rmax=6)
near('R_TH_BAT', (out['J_Li-Po']['bx1'] + 1.2, TC_FACE_RECT[3] + 4.0), 'Top', rots=(90, 270), rmax=6)

# ------------------------------------------------------------------ ANALOG half, Bottom extras
# U1 VREF-buffer side (pins 8-14) faces the left edge; its divider/filter sits right above U1, R_ref by J_REF
for d, tgt, rots in (('RV1', (X0 + 2.0, UY + 4.4), (0, 180)), ('RV2', (X0 + 4.1, UY + 4.4), (0, 180)),
                     ('Cdiv_1', (X0 + 6.1, UY + 4.4), (0, 180)), ('Cdiv_10uF', (X0 + 3.0, UY + 6.4), (0, 180)),
                     ('Cdiv', (X0 + 6.4, UY + 6.4), (0, 180)), ('R_ref', (X0 + 3.2, JY + 3.2), (0, 180))):
    near(d, tgt, 'Bottom', rots=rots, rmax=5)
# DNP DRL provisions: the 15 input resistors under their own sockets, the DRL amplifier chain by J_REF
for n in range(1, 6):
    for k, s in enumerate(('A', 'B', 'C')):
        # upright, pad 1 (electrode input) up and pad 2 (DRL_SUM) down: the 15 DRL_SUM pads form one row -> one straight bus
        d_ = 'R_DRL_V%s%d' % (s, n)
        near(d_, (JX[n - 1] - 1.75 + 1.75 * k, Y0 + 1.7), 'Bottom', rots=(rot_for(d_, False, 'Bottom', 'U'),), rmax=4, step=0.1)
for d in ('U_DRL1', 'C_DRL_DEC', 'R_DRL_FB', 'C_DRL_FB', 'R_DRL_OUT1', 'R_DRL_OUT2', 'R_DRL_SEL'):
    near(d, (X0 + 4.5, JY + 3.0), 'Bottom', rmax=12)

# ------------------------------------------------------------------ DIGITAL / POWER half, Bottom
# charger: UP1 under the USB-C shell interior (its exposed-pad GND vias land under the grounded shell)
usbc = [q for q in out['J_USB_C']['pads'] if q['hole'] > 0]
shell_mid_y = (min(q['y'] for q in usbc) + max(q['y'] for q in usbc)) / 2
at('UP1', X0 + 3.6, shell_mid_y, 0, 'Bottom')
log.append('UP1 at %.2f,%.2f (USB-C shell interior)' % (X0 + 3.6, shell_mid_y))
for (vx, vy) in ((0, 0), (0.5, 0.5), (-0.5, 0.5), (0.5, -0.5), (-0.5, -0.5)):
    c = pin_xy('UP1', '17')
    VIAS.append((c[0] + vx, c[1] + vy, 0.5, 'GND', 'UP1'))
for d, pin in (('C_IN_', '13'), ('C_OUT_', '10'), ('C_BAT', '2'), ('RISET', '16'), ('R_LIM', '12'), ('R_TMR', '14'),
               ('R_TS_SER', '1'), ('R_TS_TOP', '1'), ('R_TS_BOTTOM', '1'), ('R_EN1_BIAS', '6'), ('R_PGOOD', '7'), ('R_CHG_LED', '9')):
    near(d, outward('UP1', pin, 1.6), 'Bottom', rmax=8)


def group_near(members, kind, target, rmax=10.0, step=0.4, rots=(0,), extra_zones=()):
    """rigid group (B local layout) flipped ('F') or translated ('T'), optionally turned, centred near target"""
    def make(x, y, rot):
        if kind == 'F':
            return group_transform(B, members, 'FR', rot, x, y) if rot else group_transform(B, members, 'F', x, y)
        g = bbox_of([B[m] for m in members])
        gc = ((g[0] + g[2]) / 2, (g[1] + g[3]) / 2)
        return group_transform(B, members, 'R', rot, x, y) if rot else group_transform(B, members, 'T', x - gc[0], y - gc[1])
    res = find_spot(make, out, OUTLINE, target, rmax=rmax, step=step, rots=rots, zones=ZONES + list(extra_zones), vias=VIAS,
                    holes=HOLES, edge_exempt=EDGE_EXEMPT)
    if res is None:
        log.append('NO SPOT for group %s near %s' % (members[0], target))
        return None
    recs, x, y, rot = res
    for k, v in recs.items():
        v['proxy'] = B[k]['proxy']
        out[k] = v
    log.append('group %-6s -> centre %.2f,%.2f rot %d (%s)' % (members[0], x, y, rot, kind))
    return x, y, rot


def grp_members(g):
    return [d for d in B if B[d]['group'] == g]


XT = out['X_WIFI_32K']
XTAL_KEEP = (XT['bx0'] - 3, XT['by0'] - 3, XT['bx1'] + 3, XT['by1'] + 3)
CONV_AWAY = [('CONV_vs_ANALOG', 'Bottom', (X0, Y0, X1, BOT_ANALOG_TOP + 3.0), lambda r: B.get(r['designator'], {}).get('group') != 'CONVERTER'),
             ('CONV_vs_XTAL', 'Bottom', XTAL_KEEP, lambda r: B.get(r['designator'], {}).get('group') != 'CONVERTER'),
             ('CONV_vs_ANT', 'Bottom', (ANT[0] - 4, ANT[1] - 4, ANT[2] + 4, ANT[3]), lambda r: B.get(r['designator'], {}).get('group') != 'CONVERTER'),
             ('CONV_vs_ADC', 'Bottom', (adc[0] - 4, adc[1] - 4, adc[2] + 4, adc[3] + 4), lambda r: B.get(r['designator'], {}).get('group') != 'CONVERTER')]
# converter cell under the MCU's left-middle (Bottom): clear of the ST67 thermal-via field, crystal, antenna, ADC corner and the
# analog band; next to its main 3V3_DIG loads (MCU, ST67)
if group_near(grp_members('CONVERTER'), 'F', (48.5, 38.5), rmax=12, rots=(0, 90, 180, 270), extra_zones=CONV_AWAY) is None:
    raise SystemExit('converter cell has no legal spot: ' + '; '.join(log))
group_near(grp_members('SUPERVISOR'), 'T', (out['UP2']['x'] - 4.5, out['UP2']['y']), rmax=10, rots=(0, 90, 180, 270))
group_near(grp_members('LDO'), 'F', (35.0, BOT_ANALOG_TOP + 3.0), rmax=10, rots=(0, 180))
near('R_EN_PD', outward('UP3', '3', 1.5), 'Bottom', rmax=6)
group_near(grp_members('GAUGE'), 'T', (19.5, 32.5), rmax=10, rots=(0, 90, 180, 270))

# service (Bottom): flat probe pads + solder jumper + UART links beside the pins they serve
wb = pin_xy('U_WIFI1', '3'); wtx = pin_xy('U_WIFI1', '22'); wen = pin_xy('U_WIFI1', '17'); mb = pin_xy('U_MCU1', '94')
for d, tgt in (('JP_WIFI_BOOT', (wb[0] + 0.5, wb[1] - 2.0)), ('R_WIFI_BOOT_OVR', (wb[0] + 0.5, wb[1] - 4.0)),
               ('TP_WIFI_BOOT', (wb[0] + 2.5, wb[1] - 2.0)),
               ('R_WIFI_UART_TX_LINK', (wtx[0] + 1.5, wtx[1])), ('R_WIFI_UART_RX_LINK', (wtx[0] + 1.5, wtx[1] + 1.5)),
               ('TP_WIFI_UART_RX', (wtx[0] + 3.5, wtx[1] - 1.0)), ('TP_WIFI_UART_TX', (wtx[0] + 3.5, wtx[1] + 1.0)),
               ('TP_WIFI_CHIP_EN', (wen[0] + 2.8, wen[1] - 1.2)), ('TP_MCU_BOOT0', (mb[0], mb[1] - 2.0)), ('TP_GND', (wtx[0] + 3.5, wtx[1] + 3.0))):
    near(d, tgt, 'Bottom', rmax=8)

# native free test pads keep their Top layer: nearest legal Top spot to their own circuit
FP_TGT = {'FP:TP_GND_ANA': (X0 + 2.5, JY + 4.0), 'FP:TP_VREF_A': (X0 + 2.5, JY + 6.0), 'FP:TP_VREF_B_SRC': (X0 + 2.5, JY + 8.0),
          'FP:TP_3V0_ANA': pin_xy('UP3', '5'), 'FP:TP_3V3_DIG': pin_xy('UP2', '1'), 'FP:TP_VSYS': pin_xy('UP1', '10'),
          'FP:TP_VBUS': pin_xy('UP1', '13'), 'FP:TP_GND_PWR': pin_xy('J_Li-Po', '1'), 'FP:TP_VBAT_CELL': pin_xy('J_Li-Po', '3'),
          'FP:TP_GND_DIG': pin_xy('U_MCU1', '94')}
for d, tgt in FP_TGT.items():
    near(d, tgt, 'Top', rots=(0,), rmax=14, step=0.25)

if __name__ == '__main__':
    from c2audit import audit, summarize
    print('board %.1f x %.1f  pitch %.1f  JX %s' % (L, H, PITCH, ' '.join('%.1f' % v for v in JX)))
    print('\n'.join(log))
    missing = sorted(d for d in B if d not in out)
    print('placed %d / %d, missing: %s' % (len(out), len(B), ' '.join(missing)))
    REF = {d: place(p, p['x'], p['y'], p['rot'], p['side']) for d, p in B.items()}
    for d in REF:
        REF[d]['proxy'] = B[d]['proxy']
    probs = audit(out, OUTLINE, edge_exempt=EDGE_EXEMPT, ref=REF, holes=[h + (n,) for h, n in HOLES], zones=ZONES)
    probs = [p for p in probs if not (p[0] == 'HOLE' and p[2] == 'J_SWD')]
    print(summarize(probs, limit=30))
    json.dump({'L': L, 'H': H, 'PITCH': PITCH, 'outline': OUTLINE, 'log': log, 'problems': probs},
              open(os.path.join(EV, 'PLAN_C2_AUDIT.json'), 'w'), indent=1, default=str)
    zt = [z[2] + ('#aa33aa', z[0]) for z in ZONES if z[1] in ('Top', '*')]
    zb = [z[2] + ('#aa33aa', z[0]) for z in ZONES if z[1] in ('Bottom', '*')]
    render(out, os.path.join(EV, 'PLAN_C2_TOP.png'), window=(X0 - 2, Y0 - 2, X1 + 2, Y1 + 6), outline=OUTLINE,
           title='C2 plan TOP (%.1f x %.1f mm, BK13 pitch %.1f)' % (L, H, PITCH), scale=26, sides=('Top',), zones=zt)
    render(out, os.path.join(EV, 'PLAN_C2_BOTTOM_xray.png'), window=(X0 - 2, Y0 - 2, X1 + 2, Y1 + 6), outline=OUTLINE,
           title='C2 plan BOTTOM (x-ray, viewed from top)', scale=26, sides=('Bottom',), zones=zb)
    # plan table for the writer
    with open(os.path.join(EV, 'PLAN_C2_COMPONENTS.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['designator', 'src_uid', 'group', 'b_side', 'b_x', 'b_y', 'b_rot', 'c2_side', 'c2_x', 'c2_y', 'c2_rot', 'new_footprint'])
        for d in sorted(out):
            r, b = out[d], B[d]
            w.writerow([d, b['src_uid'], b['group'], b['side'], round(b['x'], 4), round(b['y'], 4), round(b['rot'], 3), r['side'],
                        round(r['x'], 4), round(r['y'], 4), round(r['rot'] % 360, 3), 'Y' if d in SYN else ''])
    import pickle
    pickle.dump({'out': out, 'VIAS': VIAS, 'HOLES': HOLES, 'OUTLINE': OUTLINE, 'ANT': ANT, 'JX': JX, 'JY': JY, 'PITCH': PITCH,
                 'ZONE_ANALOG_Y': ZONE_ANALOG_Y, 'BOT_ANALOG_TOP': BOT_ANALOG_TOP, 'TC_FACE': TC_FACE_RECT},
                open(os.path.join(HERE, 'work', 'plan_C2.pkl'), 'wb'))
    render(out, os.path.join(EV, 'PLAN_C2_WIP_TOP.png'), window=(X0 - 2, Y0 - 2, X1 + 2, Y1 + 6), outline=OUTLINE,
           title='C2 WIP TOP', scale=26, sides=('Top',), zones=[z[2] + ('#aa33aa', z[0]) for z in ZONES if z[1] in ('Top', '*')])
    render(out, os.path.join(EV, 'PLAN_C2_WIP_BOT.png'), window=(X0 - 2, Y0 - 2, X1 + 2, Y1 + 6), outline=OUTLINE,
           title='C2 WIP BOTTOM (x-ray from top)', scale=26, sides=('Bottom',), zones=[z[2] + ('#aa33aa', z[0]) for z in ZONES if z[1] in ('Bottom', '*')])
