"""Small fixed-copper GND via scan around the proven CS seed; no router/CAD."""
import csv
import hashlib
import json
import math
import os
from pathlib import Path
EV = Path(__file__).resolve().parent.parent / 'evidence'
GEOM = EV/'GEOMETRY_C2_6L_BF.txt'
SEED = EV/'ASTRA_BF_CS_ESCAPE_SEED_ADDS.csv'
os.environ['GEOM_FILE'] = str(GEOM)
os.environ['BOARD_BOX'] = '12,12,67.1,44'
import geom as G
from shapely.geometry import Point


def main():
    objects,_,_ = G.load()
    for row in csv.DictReader(SEED.open()):
        x,y = float(row['x1']),float(row['y1'])
        if row['kind'] == 'TRACK':
            objects.append(G.track(row['net'],row['layer'],[(x,y),(float(row['x2']),float(row['y2']))],float(row['w'])))
        else:
            objects.append(G.via(row['net'],x,y,float(row['d']),float(row['h'])))
            objects.append(G.Obj(Point(x,y).buffer(float(row['h'])/2),row['net'],'HOLE',set()))
    index = G.Index(objects)
    center = (58.38,25.838)
    sites = [(round(center[0]+i*.1,4),round(center[1]+j*.1,4)) for i in range(-15,16) for j in range(-15,16)
             if .64 <= math.hypot(i*.1,j*.1) <= 1.50]
    sites.sort(key=lambda p: math.dist(p,center))
    selected, checked = [], []
    for diameter,hole_size in ((.60,.30),(.45,.20)):
        for p in sites:
            if any(math.dist(p,s['point']) < .70 for s in selected):
                continue
            via = G.via('GND',*p,diameter,hole_size)
            hole = Point(*p).buffer(hole_size/2)
            violations = [{'net':q.net,'ref':q.comp,'pin':q.name,'kind':q.kind,'gap':gap,'required':need,'native_record':q.src}
                          for q,gap,need in index.violations(via)]
            drill = [q.src for q in index.holes if q.geom.distance(hole)<G.hole_gap(q)-1e-6]
            pads = [q.src for q in index.near(via.geom,0) if q.kind == 'PAD' and via.geom.intersects(q.geom)]
            passed = not violations and not drill and not pads and G.edge_ok(via.geom)
            record = {'point':p,'diameter_mm':diameter,'hole_mm':hole_size,'distance_to_cs_seed_mm':math.dist(p,center),
                      'passed':passed,'copper_blockers':violations,'hole_blockers':drill,'pad_overlaps':pads}
            checked.append(record)
            if passed:
                nearby = [q for q in index.near(via.geom,1.0) if q.net != 'GND' and q.layers & via.layers]
                record['nearest_other_copper'] = sorted([
                    {'kind':q.kind,'net':q.net,'ref':q.comp,'pin':q.name,
                     'gap_mm':via.geom.distance(q.geom),'required_mm':G.required(via,q)} for q in nearby],
                    key=lambda r:r['gap_mm']-r['required_mm'])[:4]
                selected.append(record)
                index.add(via)
                index.add(G.Obj(hole,'GND','HOLE',set()))
                print('LEGAL_GND_STITCH '+json.dumps(record),flush=True)
                if len(selected)>=2:
                    break
        if len(selected)>=2:
            break
    report = {'inputs':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (GEOM,SEED)],
              'selected':selected,'checked':checked,'search_radius_mm':1.50,'limits':['Fixed copper and future CS seed included; no routing or CAD operation.',
              'Legal drill/copper sites do not prove poured-GND connectivity; native repour and L2/L4 attachment required.',
              'Two selected sites also checked against each other; no pad overlap allowed.']}
    (EV/'ASTRA_BF_CS_GND_STITCH_SITES.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    if selected:
        with (EV/'ASTRA_BF_CS_GND_STITCH_ADDS.csv').open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=['kind','group','net','layer','x1','y1','x2','y2','w','d','h','conn','relax'])
            writer.writeheader()
            for r in selected:
                writer.writerow(dict(kind='VIA',group='ASTRA_BF_CS_GND_STITCH',net='GND',layer='Multi Layer',
                    x1=r['point'][0],y1=r['point'][1],d=r['diameter_mm'],h=r['hole_mm'],conn='CS reference-plane stitch; verify native pours',relax=0))
    print(json.dumps({'selected_count':len(selected),'sites_checked':len(checked)},indent=2))


if __name__ == '__main__':
    main()
