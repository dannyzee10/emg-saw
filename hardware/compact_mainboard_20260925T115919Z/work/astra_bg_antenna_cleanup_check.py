"""Check only the four BG antenna branches, preserving the L5 interior junction."""
import csv
import hashlib
import json
import os
import time
from pathlib import Path

EV = Path(__file__).resolve().parent.parent / 'evidence'
SOURCE = EV/'GEOMETRY_C2_6L_BG.txt'
REPORT = EV/'ASTRA_BG_ANTENNA_BOUNDED_CHECK.json'
ADDS = EV/'ASTRA_BG_ANTENNA_BOUNDED_ADDS.csv'
DELS = EV/'ASTRA_BG_ANTENNA_BOUNDED_DELS.csv'
os.environ['GEOM_FILE'] = str(SOURCE)
os.environ['BOARD_BOX'] = '12,12,67.1,44'
import geom as G
from astra_check_final_opens_graph import preserved, power_thresholds
from shapely.ops import unary_union

TARGETS = [
 ('Top Layer','3V3_DIG',(44.775,41.625,46.225,41.625),.15),
 ('Mid Layer 2','WIFI_CHIP_EN',(45.975,34.975,48.6045,34.975),.20),
 ('Mid Layer 2','WIFI_CHIP_EN',(44.875,36.075,45.975,34.975),.20),
 ('Mid Layer 2','WIFI_UART_TX',(48.6045,41.925,48.9019,41.925),.15),
 ('Mid Layer 2','WIFI_UART_TX',(48.9019,41.925,49.225,41.925),.15),
 ('Mid Layer 4','3V3_DIG',(51.025,33.675,51.025,37.075),.15),
]


def detail(q):
    return {'kind':q.kind,'net':q.net,'ref':q.comp,'pin':q.name,'record':q.src}


def row(q, group):
    s=q.src
    return dict(kind='TRACK',group=group,net=q.net,layer=s[1],x1=s[3],y1=s[4],x2=s[5],y2=s[6],w=s[7],d='',h='',
                conn='bounded cleanup of four newly reported BG antenna branches',relax=0)


def main():
    begin=time.monotonic()
    objects,_,keepouts=G.load()
    index=G.Index(objects)
    removed=set()
    targets=[]
    for layer,net,xy,width in TARGETS:
        matches=[(i,q) for i,q in enumerate(objects) if q.kind=='TRACK' and q.net==net and layer in q.layers
                 and tuple(map(float,q.src[3:8]))==(*xy,width)]
        assert len(matches)==1,(layer,net,xy,width)
        i,q=matches[0];removed.add(i);targets.append(q)
    remaining=[(i,q) for i,q in enumerate(objects) if i not in removed]
    old_l5=targets[-1]
    l5_contacts=[q for q in index.near(old_l5.geom,.00015) if q is not old_l5 and q.net==old_l5.net
                 and q.layers & old_l5.layers and q.geom.distance(old_l5.geom)<=.00015]
    # Keep every existing feed-contact area, while ending the new horizontal
    # segment on the centerline of the retained 0.40 mm diagonal.
    paths=[[(51.025,33.675),(51.025,35.025)],[(51.025,35.025),(50.725,35.025)]]
    additions=[G.track('3V3_DIG','Mid Layer 4',p,.15) for p in paths]
    for q,p in zip(additions,paths):
        q.src=['TRACK','Mid Layer 4','3V3_DIG',*map(str,(*p[0],*p[1],.15)),'BOUNDED_ANTENNA_REPLACEMENT']
    new_l5=unary_union([q.geom for q in additions])
    contact_checks=[]
    for q in l5_contacts:
        original=old_l5.geom.intersection(q.geom)
        retained=new_l5.intersection(q.geom)
        lost=original.difference(new_l5).area
        contact_checks.append(dict(detail(q),old_contact_area_mm2=original.area,
                                   replacement_contact_area_mm2=retained.area,
                                   lost_original_contact_area_mm2=lost,all_original_contact_area_preserved=lost<1e-12))
    index_after=G.Index([q for _,q in remaining])
    blockers=[dict(detail(q),gap=gap,required=need) for a in additions for q,gap,need in index_after.violations(a)]
    edge=all(G.edge_ok(a.geom) for a in additions)
    keepout=any(k.intersects(a.geom) for a in additions for k in keepouts)
    final=remaining+[(f'new_{i}',q) for i,q in enumerate(additions)]
    widths={i:float(q.src[7]) for i,q in enumerate(objects) if q.kind=='TRACK'}
    widths.update({f'new_{i}':.15 for i in range(len(additions))})
    graph_checks={}
    power_checks=[]
    for net in sorted({q.net for q in targets}):
        old=[(i,q) for i,q in enumerate(objects) if q.net==net and q.kind not in ('HOLE','KEEPOUT')]
        new=[(i,q) for i,q in final if q.net==net and q.kind not in ('HOLE','KEEPOUT')]
        _,_,splits=preserved(old,new,removed)
        graph_checks[net]={'retained_connections_preserved':not splits,'split_group_count':len(splits)}
        if net=='3V3_DIG':
            for threshold in power_thresholds(old,widths):
                wide_old=[(i,q) for i,q in old if q.kind!='TRACK' or widths[i]>=threshold-.00015]
                wide_new=[(i,q) for i,q in new if q.kind!='TRACK' or widths[i]>=threshold-.00015]
                _,_,wide_splits=preserved(wide_old,wide_new,removed)
                power_checks.append({'threshold_mm':threshold,'retained_connections_preserved':not wide_splits,
                                     'split_group_count':len(wide_splits)})
    # Identify every contact left outside each removed local branch, and
    # require the surviving termination itself to have another fixed contact.
    branch_contacts={}
    for label,group in [('Top_3V3',[targets[0]]),('WIFI_CHIP_EN',targets[1:3]),('WIFI_UART_TX',targets[3:5])]:
        neighbors=[]
        for q in group:
            for other in index.near(q.geom,.00015):
                if any(other is r for r in targets) or other.net!=q.net or not(q.layers&other.layers):continue
                if q.geom.distance(other.geom)>.00015 or any(other is n for n in neighbors):continue
                neighbors.append(other)
        branch_contacts[label]=[dict(detail(q),remaining_other_contacts=[detail(n) for n in index_after.near(q.geom,.00015)
            if n is not q and n.net==q.net and n.layers&q.layers and n.geom.distance(q.geom)<=.00015]) for q in neighbors]
    passed=not blockers and edge and not keepout and all(r['all_original_contact_area_preserved'] for r in contact_checks)
    passed=passed and all(r['retained_connections_preserved'] for r in graph_checks.values())
    passed=passed and all(r['retained_connections_preserved'] for r in power_checks)
    report={'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            'passed':passed,'deletions':[q.src for q in targets],'additions':[q.src for q in additions],
            'l5_contact_preservation':contact_checks,'new_copper_blockers':blockers,'edge_clear':edge,'keepout':keepout,
            'graphs':graph_checks,'power_thresholds':power_checks,'surviving_branch_contacts':branch_contacts,
            'seconds':time.monotonic()-begin,'limits':['Bounded six-track deletion/two-track replacement only.',
            'All existing pads/vias retained. Exported copper contact graphs omit full poured geometry.',
            'Fresh current-state exact check and native DRC remain required before/after applying.']}
    REPORT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    if passed:
        fields=list(row(targets[0],'').keys())
        for path,items in ((DELS,targets),(ADDS,additions)):
            with path.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
                w.writerows(row(q,'ASTRA_BG_ANTENNA_BOUNDED') for q in items)
    print(json.dumps({k:report[k] for k in ('passed','l5_contact_preservation','new_copper_blockers','graphs','power_thresholds','surviving_branch_contacts','seconds')}),flush=True)


if __name__=='__main__':main()
