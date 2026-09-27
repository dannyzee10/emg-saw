"""Four short exact-collision alternatives for the CS candidate's thin 3V3 feed."""
import csv
import hashlib
import json
import os
from pathlib import Path
import astra_verify_routing_delta as D
EV=Path(__file__).resolve().parent.parent/'evidence'
GEOM=EV/'GEOMETRY_C2_6L_BF.txt'
ADDS=EV/'ASTRA_BF_CS_INSPECT_RAW_ADDS.csv'
DELS=EV/'ASTRA_BF_CS_INSPECT_DELS.csv'
os.environ['GEOM_FILE']=str(GEOM)
os.environ['BOARD_BOX']='12,12,67.1,44'
import geom as G


def main():
    objects,_,_=G.load()
    removed=set()
    for row in D.plan(DELS,False):
        matches=[]
        for i,o in enumerate(objects):
            if i in removed or o.src is None: continue
            s=o.src
            if o.kind=='TRACK' and 'INCOMP=False' in s and 'INPOLY=False' in s:
                p=D.primitive('TRACK',s[2],s[1],s[3:8],s)
            elif o.kind=='VIA': p=D.primitive('VIA',s[1],'',s[2:6],s)
            else: continue
            if D.match_error(row,p,.00015) is not None: matches.append(i)
        if len(matches)!=1: raise ValueError('nonunique delete '+repr(row))
        removed.add(matches[0])
    after=[o for i,o in enumerate(objects) if i not in removed]
    for row in D.plan(ADDS,True):
        v=row['values']
        after.append(G.track(row['net'],row['layer'],[(v[0],v[1]),(v[2],v[3])],v[4]) if row['kind']=='TRACK' else G.via(row['net'],*v))
    index=G.Index(after)
    routes=[('same_coordinates',[(48.975,38.925),(49.625,38.925)]),
            ('centered_on_mcu_pad6',[(48.975,39.0),(49.625,39.0)]),
            ('extend_existing_vertical',[(48.825,38.825),(48.825,39.0),(49.625,39.0)]),
            ('diagonal_from_existing_endpoint',[(48.825,38.825),(49.0,39.0),(49.625,39.0)])]
    trials=[]
    for name,points in routes:
        blockers=[]
        for a,b in zip(points,points[1:]):
            track=G.track('3V3_DIG','Top Layer',[a,b],.4)
            blockers += [{'net':q.net,'kind':q.kind,'ref':q.comp,'pin':q.name,'gap':gap,'required':need,'native_record':q.src}
                         for q,gap,need in index.violations(track)]
            if not G.edge_ok(track.geom): blockers.append({'edge':False})
        trials.append({'name':name,'points':points,'width_mm':.4,'passed':not blockers,'blockers':blockers})
    bridge_trials=[]
    for name,points in [
            ('direct',[(47.075,42.375),(48.675,42.575)]),
            ('diagonal_then_horizontal',[(47.075,42.375),(47.275,42.575),(48.675,42.575)]),
            ('upper_to_testpad',[(47.075,42.375),(47.075,41.825),(48.675,41.825)]),
            ('around_old_feed',[(47.075,42.375),(47.425,42.725),(48.675,42.725)])]:
        blockers=[]
        for a,b in zip(points,points[1:]):
            track=G.track('3V3_DIG','Top Layer',[a,b],.4)
            blockers += [{'net':q.net,'kind':q.kind,'ref':q.comp,'pin':q.name,'gap':gap,'required':need,'native_record':q.src}
                         for q,gap,need in index.violations(track)]
        bridge_trials.append({'name':name,'points':points,'width_mm':.4,'passed':not blockers,'blockers':blockers})
    bridge=next((r for r in bridge_trials if r['name']=='diagonal_then_horizontal' and r['passed']),None)
    if bridge is None: bridge=next((r for r in bridge_trials if r['passed']),None)
    chosen=next((r for r in trials if r['name']=='extend_existing_vertical' and r['passed']),None)
    if chosen is None: chosen=next((r for r in trials if r['passed']),None)
    if chosen:
        rows=list(csv.DictReader(ADDS.open(encoding='utf-8-sig')))
        old=[r for r in rows if r['kind']=='TRACK' and r['net']=='3V3_DIG' and r['layer']=='Top Layer'
             and tuple(float(r[k]) for k in ('x1','y1','x2','y2','w'))==(48.975,38.925,49.625,38.925,.15)]
        if len(old)!=1: raise ValueError('thin planned feed not unique')
        rows=[r for r in rows if r is not old[0]]
        for a,b in zip(chosen['points'],chosen['points'][1:]):
            rows.append(dict(kind='TRACK',group='ASTRA_CS_POWER_FEED',net='3V3_DIG',layer='Top Layer',
                x1=a[0],y1=a[1],x2=b[0],y2=b[1],w=.4,d='',h='',conn='preserve original power-width path at MCU6',relax=0))
        with (EV/'ASTRA_BF_CS_INSPECT_WIDE_ADDS.csv').open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
        if bridge:
            for a,b in zip(bridge['points'],bridge['points'][1:]):
                rows.append(dict(kind='TRACK',group='ASTRA_CS_MCU100_POWER_BRIDGE',net='3V3_DIG',layer='Top Layer',
                    x1=a[0],y1=a[1],x2=b[0],y2=b[1],w=.4,d='',h='',conn='preserve regulator-to-MCU100 supply threshold',relax=0))
            with (EV/'ASTRA_BF_CS_INSPECT_WIDE_BRIDGE_ADDS.csv').open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
    report={'inputs':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (GEOM,ADDS,DELS)],
            'trials':trials,'chosen':chosen,'bridge_trials':bridge_trials,'chosen_bridge':bridge,
            'limits':['Short feed/bridge alternatives only; all retained and candidate copper included.',
            'No router/CAD operation. Full candidate precheck, graph and native DRC remain required.']}
    (EV/'ASTRA_BF_CS_POWER_FEED_FIX.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__': main()
