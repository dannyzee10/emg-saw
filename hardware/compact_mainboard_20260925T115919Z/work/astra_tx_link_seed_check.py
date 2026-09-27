"""Nine local fixed-copper MCU TX link-pad escape points, no router."""
import csv
import hashlib
import json
import os
from pathlib import Path
EV = Path(__file__).resolve().parent.parent / 'evidence'
GEOM = EV / 'GEOMETRY_C2_6L_BF.txt'
os.environ['GEOM_FILE'] = str(GEOM)
os.environ['BOARD_BOX'] = '12,12,67.1,44'
import geom as G
from shapely.geometry import Point


def main():
    objects, _, _ = G.load()
    index = G.Index(objects)
    net, start = 'MCU_WIFI_UART_TX', (44.026,40.805)
    sites = [start] + [(start[0]+x,start[1]+y) for x in (-.15,0,.15) for y in (-.15,0,.15) if x or y]
    checked, chosen = [], None
    for p in sites:
        via = G.via(net,*p,.45,.20)
        hole = Point(*p).buffer(.1)
        copper = [{'net': q.net,'ref':q.comp,'pin':q.name,'kind':q.kind,'gap':gap,'required':need,'native_record':q.src}
                  for q,gap,need in index.violations(via)]
        drill = [q.src for q in index.holes if q.geom.distance(hole)<G.hole_gap(q)-1e-6]
        stub = None if p == start else G.track(net,'Bottom Layer',[start,p],.20)
        stub_ok = stub is None or (G.edge_ok(stub.geom) and not index.violations(stub))
        row = {'point':p,'via_copper_blockers':copper,'hole_blockers':drill,
               'edge_clear':G.edge_ok(via.geom),'bottom_020_stub_clear':bool(stub_ok)}
        row['passed'] = not copper and not drill and row['edge_clear'] and stub_ok
        checked.append(row)
        if row['passed']:
            chosen = row
            break
    report = {'geometry':str(GEOM),'sha256':hashlib.sha256(GEOM.read_bytes()).hexdigest(),
              'checked':checked,'chosen':chosen,'limits':['Local via/stub only; no complete route or CAD operation.',
              'Native repour/DRC and filled/capped VIP tagging still required.']}
    (EV/'ASTRA_BF_TX_LINK_SEED_CHECK.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    if chosen:
        x,y = chosen['point']
        group = 'ASTRA_BF_TX_LINK_ESCAPE VIP'
        rows = [dict(kind='VIA',group=group,net=net,layer='Multi Layer',x1=x,y1=y,d=.45,h=.20,conn='R_WIFI_UART_TX_LINK.2 escape seed',relax=0)]
        if tuple(chosen['point']) != start:
            rows.append(dict(kind='TRACK',group=group,net=net,layer='Bottom Layer',x1=start[0],y1=start[1],x2=x,y2=y,w=.20,conn='R_WIFI_UART_TX_LINK.2 escape seed',relax=0))
        with (EV/'ASTRA_BF_TX_LINK_ESCAPE_SEED_ADDS.csv').open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=['kind','group','net','layer','x1','y1','x2','y2','w','d','h','conn','relax'])
            writer.writeheader();writer.writerows(rows)
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
