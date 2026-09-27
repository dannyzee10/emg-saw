"""Two tiny optional TX via-centre links and local return-via distances; no router."""
import csv
import hashlib
import json
import math
import os
from pathlib import Path
EV=Path(__file__).resolve().parent.parent/'evidence'
GEOM=EV/'GEOMETRY_C2_6L_BGM.txt'
ADDS=EV/'ASTRA_BGM_TX_LAST_WITH_SEED_ADDS.csv'
os.environ['GEOM_FILE']=str(GEOM)
os.environ['BOARD_BOX']='12,12,67.1,44'
import geom as G


def main():
    objects,_,keepouts=G.load()
    rows=list(csv.DictReader(ADDS.open(encoding='utf-8-sig')))
    idx=G.Index(objects)
    for r in rows:
        v={k:float(r[k]) for k in ('x1','y1')}
        idx.add(G.track(r['net'],r['layer'],[(v['x1'],v['y1']),(float(r['x2']),float(r['y2']))],float(r['w']))
                if r['kind']=='TRACK' else G.via(r['net'],v['x1'],v['y1'],float(r['d']),float(r['h'])))
    extensions=[('Mid Layer 4',(44.026,40.805),(43.825,40.675)),
                ('Mid Layer 2',(56.08,44.3),(56.175,44.125))]
    checks=[]
    new_rows=[]
    for layer,a,b in extensions:
        o=G.track('MCU_WIFI_UART_TX',layer,[a,b],.15)
        blockers=[{'net':q.net,'kind':q.kind,'ref':q.comp,'pin':q.name,'gap':d,'required':need,'native_record':q.src}
                  for q,d,need in idx.violations(o)]
        near=sorted([{'net':q.net,'kind':q.kind,'ref':q.comp,'pin':q.name,
                      'gap':o.geom.distance(q.geom),'required':G.required(o,q)}
                     for q in idx.near(o.geom,.7) if q.net!=o.net and q.layers&o.layers],key=lambda r:r['gap'])[:3]
        clear=not blockers and G.edge_ok(o.geom) and not any(k.intersects(o.geom) for k in keepouts)
        checks.append({'layer':layer,'start':a,'end':b,'width':.15,'passed':clear,'blockers':blockers,
                       'nearest_other_copper':near,'original_via_to_endpoint_distance':math.dist(a,b)})
        new_rows.append(dict(kind='TRACK',group='ASTRA_TX_CENTER_LINK',net='MCU_WIFI_UART_TX',layer=layer,
                             x1=a[0],y1=a[1],x2=b[0],y2=b[1],w=.15,conn='positive centre link; no deletions',relax=0))
    ground=[o for o in objects if o.kind=='VIA' and o.net=='GND']
    refs=[]
    for r in rows:
        if r['kind']!='VIA': continue
        p=(float(r['x1']),float(r['y1']))
        nearest=sorted([{'xy':list(map(float,q.src[2:4])),
                         'distance':math.dist(p,tuple(map(float,q.src[2:4]))),
                         'diameter':float(q.src[4]),'hole':float(q.src[5])} for q in ground],key=lambda v:v['distance'])[:2]
        refs.append({'signal_via':p,'nearest_retained_ground_vias':nearest})
    passed=all(c['passed'] for c in checks)
    output=EV/'ASTRA_BGM_TX_CENTERED_ADDS.csv'
    if passed:
        with output.open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows+new_rows)
    result={'both_center_links_clear':passed,'checks':checks,'return_via_distances':refs,
            'candidate_only_tx_net':all(r['net']=='MCU_WIFI_UART_TX' for r in rows),
            'candidate_signal_layers':sorted({r['layer'] for r in rows if r['kind']=='TRACK'}),
            'candidate_track_widths':sorted({float(r['w']) for r in rows if r['kind']=='TRACK'}),
            'output_if_clear':str(output) if passed else None,
            'inputs':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (GEOM,ADDS)],
            'limits':['Checks only the two optional additions; root must rerun combined exact and graph checks.',
                      'Ground-via proximity does not establish poured copper attachment or signal integrity.',
                      'No native operation, full router, deletion, or CAD edit.']}
    (EV/'ASTRA_BGM_TX_JUNCTION_REVIEW.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
    return 0 if passed else 1


if __name__=='__main__': raise SystemExit(main())
