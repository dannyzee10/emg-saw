"""Merge/check the specific CL_4/L5 candidate; no CAD writes."""
import csv
import json
import os
from pathlib import Path
from collections import Counter
ev = Path('../evidence')
moved = ev / 'ASTRA_CH4_L5_TRIAL_PLANNING_ONLY/MOVED_ONLY_GEOMETRY.txt'
os.environ['GEOM_FILE'] = str(moved)
os.environ['BOARD_BOX'] = '12,12,67.1,44'
import geom as G
from shapely.geometry import box
from shapely.strtree import STRtree
rows = lambda p: list(csv.DictReader(p.open(newline='')))
adds = rows(ev / 'ASTRA_CH4_L5_TRIAL_COMBINED_ADDS.csv') + rows(ev / 'ASTRA_CH4_LOCAL3_ROUTE_ADDS.csv')
dels = rows(ev / 'ASTRA_CL4_HYPOTHETICAL_DELS_BB.csv')
fields = ['kind','group','net','layer','x1','y1','x2','y2','w','d','h','conn','relax']
# One explicitly bounded exception to the planner's former L5 reservation.
corridor = box(51.2, 15.1, 57.6, 17.35)
for row in adds:
    if row['kind'] == 'TRACK' and row['layer'] == 'Mid Layer 4':
        t = G.track(row['net'], row['layer'], [(float(row['x1']),float(row['y1'])),
                    (float(row['x2']),float(row['y2']))],float(row['w']))
        if row['net'] != 'NetINA4_3' or not corridor.covers(t.geom):
            raise SystemExit('Unauthorized L5 routing outside the channel-4 corridor')
for kind, data in [('ADDS',adds),('DELS',dels)]:
    with (ev / ('ASTRA_CH4_READY_' + kind + '.csv')).open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,restval='',extrasaction='ignore');w.writeheader();w.writerows(data)
objs,_,_ = G.load()
def same(r,o):
    s=o.src
    if not s: return False
    if r['kind']=='VIA':
        return s[0]=='VIA' and s[1]==r['net'] and abs(float(s[2])-float(r['x1']))<.00015 and abs(float(s[3])-float(r['y1']))<.00015
    return (o.kind=='TRACK' and s[1]==r['layer'] and s[2]==r['net'] and
            ((abs(float(s[3])-float(r['x1']))<.00015 and abs(float(s[4])-float(r['y1']))<.00015 and
              abs(float(s[5])-float(r['x2']))<.00015 and abs(float(s[6])-float(r['y2']))<.00015) or
             (abs(float(s[3])-float(r['x2']))<.00015 and abs(float(s[4])-float(r['y2']))<.00015 and
              abs(float(s[5])-float(r['x1']))<.00015 and abs(float(s[6])-float(r['y1']))<.00015)))
objs=[o for o in objs if not any(same(r,o) for r in dels)]
for r in adds:
    objs.append(G.via(r['net'],float(r['x1']),float(r['y1']),float(r['d']),float(r['h'])) if r['kind']=='VIA' else
                G.track(r['net'],r['layer'],[(float(r['x1']),float(r['y1'])),(float(r['x2']),float(r['y2']))],float(r['w'])))
proof={}
for net in ('NetINA4_3','INA_OUT_4','NetCL_4_1'):
    objects=[o for o in objs if o.net==net and o.kind in ('PAD','VIA','TRACK')]
    tree=STRtree([o.geom for o in objects]);seen=set();partitions=[]
    for start in range(len(objects)):
        if start in seen:continue
        todo=[start];seen.add(start);pads=[]
        while todo:
            i=todo.pop();a=objects[i]
            if a.kind=='PAD':pads.append(a.comp+'.'+a.name)
            for j in tree.query(a.geom.buffer(.00015)):
                j=int(j);b=objects[j]
                if j not in seen and a.layers&b.layers and a.geom.distance(b.geom)<.00015:
                    seen.add(j);todo.append(j)
        if pads:partitions.append(sorted(pads))
    proof[net]=partitions
    if len(partitions)!=1:raise SystemExit('Disconnected proposed signal: '+str((net,partitions)))
report={'planning_only':True,'status':'signal topology connected; requires exact full clearance check and native DRC',
        'signal_partitions':proof,'adds':dict(Counter(r['kind'] for r in adds)),
        'deletes':dict(Counter(r['kind'] for r in dels)),
        'move':{'component':'CL_4','from':[51.3,16.05],'to':[48.2,16.05],'side':'Bottom','rotation':180},
        'L5_exception':{'net':'NetINA4_3','copper_envelope_mm':[51.2,15.1,57.6,17.35],
                        'native_rule_change':False,'ground_layers_changed':False}}
(ev/'ASTRA_CH4_CANDIDATE_PROOF.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
