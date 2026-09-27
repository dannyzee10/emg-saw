"""Read-only proof before pruning two obsolete power-stub tracks in a proposal."""
import csv
import hashlib
import json
import os
from pathlib import Path
import astra_verify_routing_delta as D
EV=Path(__file__).resolve().parent.parent/'evidence'
GEOM=EV/'GEOMETRY_C2_6L_BF.txt'
ADDS=EV/'ASTRA_BF_CS_INSPECT_WIDE_BRIDGE_ADDS.csv'
DELS=EV/'ASTRA_BF_CS_INSPECT_DELS.csv'
os.environ['GEOM_FILE']=str(GEOM)
import geom as G
from shapely.geometry import LineString,Point


def main():
    objects,_,_=G.load()
    removed=set()
    for row in D.plan(DELS,False):
        matches=[]
        for i,o in enumerate(objects):
            if i in removed or o.src is None: continue
            s=o.src
            if o.kind=='TRACK' and 'INCOMP=False' in s and 'INPOLY=False' in s: p=D.primitive('TRACK',s[2],s[1],s[3:8],s)
            elif o.kind=='VIA': p=D.primitive('VIA',s[1],'',s[2:6],s)
            else: continue
            if D.match_error(row,p,.00015) is not None: matches.append(i)
        if len(matches)!=1: raise ValueError('nonunique delete')
        removed.add(matches[0])
    after=[o for i,o in enumerate(objects) if i not in removed]
    for row in D.plan(ADDS,True):
        v=row['values']
        after.append(G.track(row['net'],row['layer'],[(v[0],v[1]),(v[2],v[3])],v[4]) if row['kind']=='TRACK' else G.via(row['net'],*v))
    wanted={(52.675,37.825,52.675,38.3685,.4),(52.675,38.3685,52.675,38.675,.4)}
    stubs=[o for o in after if o.kind=='TRACK' and o.net=='3V3_DIG' and o.src is not None and o.src[1]=='Top Layer'
           and tuple(map(float,o.src[3:8])) in wanted]
    if len(stubs)!=2: raise ValueError('Expected exact two stubs')
    terminal=Point(52.675,38.675)
    junction=Point(52.7219,38.7281)
    centerline=LineString([(52.675,37.825),(52.675,38.675)])
    cluster=stubs[0].geom.union(stubs[1].geom)
    contacts=[]
    for o in after:
        if o in stubs or o.net!='3V3_DIG' or not (o.layers & stubs[0].layers) or o.geom.distance(cluster)>.00015: continue
        endpoint_only=False
        same_external_junction=False
        if o.kind=='TRACK' and o.src is not None:
            s=o.src
            line=LineString([(float(s[3]),float(s[4])),(float(s[5]),float(s[6]))])
            endpoint_only = (min(Point(p).distance(terminal) for p in line.coords)<.00015
                             and line.intersection(centerline).geom_type=='Point')
            same_external_junction = (min(Point(p).distance(junction) for p in line.coords)<.00015
                                      and line.intersection(centerline).is_empty and junction.distance(terminal)<.10)
        contacts.append({'kind':o.kind,'ref':o.comp,'pin':o.name,'native_record':o.src,
                         'attaches_only_at_terminal_centerline':endpoint_only,
                         'shares_external_junction_outside_stub_centerline':same_external_junction})
    safe=(len(contacts)==1 and all(r['kind']=='TRACK' and r['attaches_only_at_terminal_centerline'] for r in contacts)
          or len(contacts)==2 and all(r['kind']=='TRACK' and r['shares_external_junction_outside_stub_centerline'] for r in contacts))
    if safe:
        rows=list(csv.DictReader(DELS.open(encoding='utf-8-sig')))
        for o in stubs:
            s=o.src
            rows.append(dict(kind='TRACK',group='ASTRA_CS_OBSOLETE_POWER_STUB',net='3V3_DIG',layer='Top Layer',
                             x1=s[3],y1=s[4],x2=s[5],y2=s[6],w=s[7],d='',h='',
                             conn='single-ended obsolete wide stub; terminal proof in ASTRA_BF_CS_STUB_REVIEW.json',relax=0))
        with (EV/'ASTRA_BF_CS_INSPECT_PRUNED_DELS.csv').open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
    report={'safe_single_ended_stub_cluster':safe,'stubs':[o.src for o in stubs],'external_same_net_contacts':contacts,
            'external_contact_junction':list(junction.coords)[0],
            'junction_remains_without_stubs':safe,
            'inputs':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (GEOM,ADDS,DELS)],
            'limits':['Candidate-only exact deletion CSV emitted; no CAD or router operation.',
                      'All source and proposed copper contacts examined; full after-prune graph still required.']}
    (EV/'ASTRA_BF_CS_STUB_REVIEW.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__': main()
