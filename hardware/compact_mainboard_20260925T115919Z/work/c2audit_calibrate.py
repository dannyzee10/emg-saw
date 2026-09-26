"""Calibrate the offline audit on candidate B (native DRC: 0 clearance / 0 component-clearance)."""
from c2lib import load_b, place
from c2audit import audit, summarize
B = load_b()
out = {d: place(p, p['x'], p['y'], p['rot'], p['side']) for d, p in B.items()}
for d, n in out.items():
    n['proxy'] = B[d]['proxy']
probs = audit(out, (10, 10, 85, 50), edge_exempt={'J_USB_C', 'U_WIFI1', 'J_SWD', 'JP_WIFI_BOOT'})
print('--- without reference (raw screening of B)')
print(summarize(probs, limit=3))
print('--- with B as its own reference (must be all zero)')
print(summarize(audit(out, (10, 10, 85, 50), edge_exempt={'J_USB_C', 'U_WIFI1', 'J_SWD', 'JP_WIFI_BOOT'}, ref=out), limit=5))
