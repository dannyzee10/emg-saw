"""Rebase the bounded four-antenna cleanup and six legacy branches onto native BH."""
import csv
import hashlib
import json
import os
import time
from pathlib import Path

EV=Path(__file__).resolve().parent.parent/'evidence'
SOURCE=EV/'GEOMETRY_C2_6L_BH.txt'
OLD_ADDS=EV/'ASTRA_BG_ANTENNA_BOUNDED_ADDS.csv'
OLD_DELS=EV/'ASTRA_BG_ANTENNA_BOUNDED_DELS.csv'
OUT_ADDS=EV/'ASTRA_BH_ALL_ANTENNA_BOUNDED_ADDS.csv'
OUT_DELS=EV/'ASTRA_BH_ALL_ANTENNA_BOUNDED_DELS.csv'
REPORT=EV/'ASTRA_BH_ALL_ANTENNA_BOUNDED_CHECK.json'
os.environ['GEOM_FILE']=str(SOURCE)
os.environ['BOARD_BOX']='12,12,67.1,44'
import geom as G
from astra_check_final_opens_graph import preserved,power_thresholds
from shapely.geometry import Point,box
from shapely.ops import unary_union

LEGACY_DELS=[
 ('VBUS','Top Layer',(14.825,38.725,16.3,37.25),.15),
 ('NetD_CC_ESD_1','Mid Layer 2',(16.3,41.675,19.025,41.675),.15),
 ('NetD_CC_ESD_1','Mid Layer 2',(16.125,41.675,16.3,41.675),.15),
 ('NetD_CC_ESD_1','Mid Layer 2',(15.625,41.625,16.075,41.625),.20),
 ('NetD_CC_ESD_1','Mid Layer 2',(15.15,42.1,15.625,41.625),.20),
 ('NetD_CC_ESD_1','Mid Layer 2',(15.075,42.175,15.15,42.1),.20),
 ('NetD_CC_ESD_2','Mid Layer 2',(20.025,38.125,20.025,39.325),.15),
 ('3V3_DIG','Bottom Layer',(20.725,42.325,20.725,42.925),.40),
 ('3V3_DIG','Bottom Layer',(20.875,43.025,21.075,43.225),.40),
 ('NetD_CC_ESD_2','Mid Layer 2',(21.975,41.275,22.825,41.275),.15),
 ('VSYS','Mid Layer 4',(22.625,39.425,25.775,39.425),.15),
 ('VSYS','Mid Layer 4',(25.775,39.425,26.475,40.125),.15),
 ('VSYS','Mid Layer 4',(26.475,40.125,32.825,40.125),.15),
]
LEGACY_PATHS=[
 ('VBUS','Top Layer',[(15.775,37.675),(15.875,37.675),(16.3,37.25)],.15),
 ('NetD_CC_ESD_2','Mid Layer 2',[(22.125,41.225),(22.175,41.275),(22.825,41.275)],.15),
 ('VSYS','Mid Layer 4',[(27.525,40.175),(27.575,40.125),(32.825,40.125)],.15),
]


def make_row(net,layer,xy,width,group):
    return dict(kind='TRACK',group=group,net=net,layer=layer,x1=xy[0],y1=xy[1],x2=xy[2],y2=xy[3],
                w=width,d='',h='',conn='bounded cleanup of ten native BH antenna branches',relax=0)


def desc(q):return {'kind':q.kind,'net':q.net,'ref':q.comp,'pin':q.name,'record':q.src}


def main():
    began=time.monotonic()
    assert SOURCE.read_text(encoding='utf-8-sig').rstrip().endswith('READ_ONLY; COMPLETE')
    objects,_,keepouts=G.load()
    with (EV/'BK13_ZONES_C2.csv').open() as f:
        for z in csv.DictReader(f):
            G.ZONES.append((box(float(z['x0']),float(z['y0']),float(z['x1']),float(z['y1'])),set(z['nets'].split(';')),z['ref']))
    adds=list(csv.DictReader(OLD_ADDS.open(encoding='utf-8-sig')))
    dels=list(csv.DictReader(OLD_DELS.open(encoding='utf-8-sig')))
    dels += [make_row(n,l,xy,w,'ASTRA_BH_LEGACY_ANTENNA') for n,l,xy,w in LEGACY_DELS]
    for n,l,path,w in LEGACY_PATHS:
        adds += [make_row(n,l,(*a,*b),w,'ASTRA_BH_LEGACY_JUNCTION') for a,b in zip(path,path[1:])]
    assert not any(r['net'].startswith('VREF') or r['net']=='NetJ_FPC1_8' for r in adds+dels)
    removed=set(); matched=[]
    for r in dels:
        values=tuple(float(r[k]) for k in ('x1','y1','x2','y2','w'))
        matches=[(i,q) for i,q in enumerate(objects) if i not in removed and q.kind=='TRACK' and q.net==r['net']
                 and r['layer'] in q.layers and tuple(map(float,q.src[3:8]))==values
                 and 'INCOMP=False' in q.src and 'INPOLY=False' in q.src and 'KEEPOUT=False' in q.src]
        assert len(matches)==1,r
        i,q=matches[0];removed.add(i);matched.append(q)
    remaining=[(i,q) for i,q in enumerate(objects) if i not in removed]
    new=[]
    for i,r in enumerate(adds):
        a=(float(r['x1']),float(r['y1']));b=(float(r['x2']),float(r['y2']))
        q=G.track(r['net'],r['layer'],[a,b],float(r['w']))
        q.src=['TRACK',r['layer'],r['net'],*map(str,(*a,*b,float(r['w']))),'BH_BOUNDED_REPLACEMENT']
        new.append((f'new_{i}',q))
    index=G.Index([q for _,q in remaining])
    blockers=[dict(desc(q),gap=gap,required=need,candidate=a.src) for _,a in new for q,gap,need in index.violations(a)]
    for i,(_,a) in enumerate(new):
        for _,b in new[i+1:]:
            if a.net!=b.net and a.layers&b.layers and a.geom.distance(b.geom)<G.required(a,b)-1e-6:
                blockers.append({'new_new':[a.src,b.src]})
    edge=all(G.edge_ok(q.geom) for _,q in new)
    keepout=any(k.intersects(q.geom) for _,q in new for k in keepouts)
    # No additions enter any reserved L5 analog pour region.
    reserved=[box(10.5,10.5,68.6,25.3),box(10.5,25.3,47.5,27.2),box(31.6,27.2,35.8,30.4)]
    l5_res_clear=not any('Mid Layer 4' in q.layers and any(z.intersects(q.geom) for z in reserved) for _,q in new)
    final=remaining+new
    widths={i:float(q.src[7]) for i,q in enumerate(objects) if q.kind=='TRACK'}
    widths.update({i:float(q.src[7]) for i,q in new})
    power_nets=set()
    for line in Path(G.CLASSES).read_text(encoding='utf-8',errors='replace').splitlines():
        f=line.split('|')
        if len(f)>=3 and f[:2]==['MEMBER','EMG_POWER']:power_nets.add(f[2])
    graphs={};power={}
    for net in sorted({r['net'] for r in adds+dels}):
        old=[(i,q) for i,q in enumerate(objects) if q.net==net and q.kind not in ('HOLE','KEEPOUT')]
        after=[(i,q) for i,q in final if q.net==net and q.kind not in ('HOLE','KEEPOUT')]
        before_parts,after_parts,splits=preserved(old,after,removed)
        anchors={after_parts[i] for i,q in remaining if q.net==net and q.kind not in ('HOLE','KEEPOUT')}
        detached=[i for i,q in new if q.net==net and after_parts[i] not in anchors]
        graphs[net]={'retained_connections_preserved':not splits,'split_group_count':len(splits),'detached_additions':detached,
                     'before_components':len(set(before_parts.values())),'after_components':len(set(after_parts.values()))}
        if net in power_nets:
            checks=[]
            for threshold in power_thresholds(old,widths):
                wo=[(i,q) for i,q in old if q.kind!='TRACK' or widths[i]>=threshold-.00015]
                wn=[(i,q) for i,q in after if q.kind!='TRACK' or widths[i]>=threshold-.00015]
                _,_,splits=preserved(wo,wn,removed)
                checks.append({'threshold_mm':threshold,'retained_connections_preserved':not splits,'split_group_count':len(splits)})
            power[net]=checks
    # Ensure each retained contact of a replaced needed bridge survives.
    contact_checks=[]
    all_index=G.Index(objects)
    bridges=[q for q in matched if (q.net=='VBUS' or
              (q.net=='NetD_CC_ESD_2' and tuple(map(float,q.src[3:7]))==(21.975,41.275,22.825,41.275)) or
              (q.net=='VSYS' and tuple(map(float,q.src[3:7]))==(26.475,40.125,32.825,40.125)) or
              (q.net=='3V3_DIG' and q.layers=={'Mid Layer 4'}))]
    for old in bridges:
        replacement=unary_union([q.geom for _,q in new if q.net==old.net and q.layers&old.layers])
        for other in all_index.near(old.geom,.00015):
            if any(other is q for q in matched) or other.net!=old.net or not(other.layers&old.layers):continue
            if old.geom.distance(other.geom)>.00015:continue
            before=old.geom.intersection(other.geom);after=replacement.intersection(other.geom)
            contact_checks.append({'bridge':old.src,'retained_contact':desc(other),'before_area_mm2':before.area,
                                   'after_area_mm2':after.area,'lost_old_area_mm2':before.difference(replacement).area,
                                   'contact_preserved':replacement.distance(other.geom)<=.00015})
    # New starts of legacy bridges intentionally match existing centerline endpoints.
    junctions=[]
    for net,layer,path,width in LEGACY_PATHS:
        point=Point(path[0])
        owners=[q for _,q in remaining if q.net==net and layer in q.layers and q.kind=='TRACK'
                and (tuple(map(float,q.src[3:5]))==path[0] or tuple(map(float,q.src[5:7]))==path[0])]
        junctions.append({'net':net,'point':path[0],'replacement_width_mm':width,
                          'exact_retained_endpoint_matches':[desc(q) for q in owners],
                          'full_endpoint_disk_inside_retained_copper':any(q.geom.buffer(1e-12).covers(point.buffer(width/2,16)) for q in owners)})
    passed=not blockers and edge and not keepout and l5_res_clear
    passed &= all(r['retained_connections_preserved'] and not r['detached_additions'] for r in graphs.values())
    passed &= all(r['retained_connections_preserved'] for checks in power.values() for r in checks)
    passed &= all(r['contact_preserved'] for r in contact_checks)
    passed &= all(r['exact_retained_endpoint_matches'] and r['full_endpoint_disk_inside_retained_copper'] for r in junctions)
    result={'passed':bool(passed),'inputs':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (SOURCE,OLD_ADDS,OLD_DELS)],
            'deletion_count':len(dels),'addition_count':len(adds),'graphs':graphs,'power_thresholds':power,
            'bridge_contacts':contact_checks,'explicit_centerline_junctions':junctions,'blockers':blockers,
            'edge_clear':edge,'keepout':keepout,'L5_reserved_clear':l5_res_clear,
            'all_pads_and_vias_retained':True,'VREF_untouched':True,'NetJ_FPC1_8_untouched':True,
            'seconds':time.monotonic()-began,'limits':['Only ten reported BH antenna branches and their bounded terminal chains.',
            'Some legacy bridge contact area changes, with full-width centerline endpoint connections replacing offset contacts.',
            'No CAD/native/router operation; full polygon topology remains outside exported-copper model.',
            'Native DRC must establish antenna count after apply.']}
    REPORT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    if passed:
        fields=list(make_row('', '',(0,0,0,0),0,'').keys())
        for path,rows in ((OUT_ADDS,adds),(OUT_DELS,dels)):
            with path.open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    print(json.dumps({k:result[k] for k in ('passed','deletion_count','addition_count','graphs','power_thresholds','bridge_contacts',
                                           'explicit_centerline_junctions','blockers','seconds')}),flush=True)


if __name__=='__main__':main()
