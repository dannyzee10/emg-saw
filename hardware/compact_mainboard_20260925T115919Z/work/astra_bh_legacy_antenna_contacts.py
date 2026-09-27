"""Bounded contact inventory for the six pre-BG antenna warnings in native BH."""
import hashlib
import json
import os
import time
from pathlib import Path

EV=Path(__file__).resolve().parent.parent/'evidence'
SOURCE=EV/'GEOMETRY_C2_6L_BH.txt'
os.environ['GEOM_FILE']=str(SOURCE)
os.environ['BOARD_BOX']='12,12,67.1,44'
import geom as G
from astra_check_final_opens_graph import preserved
from shapely.geometry import Point

TARGETS=[
 ('Top Layer','VBUS',(14.825,38.725,16.3,37.25)),
 ('Mid Layer 2','NetD_CC_ESD_1',(16.3,41.675,19.025,41.675)),
 ('Mid Layer 2','NetD_CC_ESD_2',(20.025,38.125,20.025,39.325)),
 ('Bottom Layer','3V3_DIG',(20.725,42.325,20.725,42.925)),
 ('Mid Layer 2','NetD_CC_ESD_2',(21.975,41.275,22.825,41.275)),
 ('Mid Layer 4','VSYS',(22.625,39.425,25.775,39.425)),
]


def desc(q):
    return {'kind':q.kind,'net':q.net,'ref':q.comp,'pin':q.name,'record':q.src}


def contacts(q,index):
    return [n for n in index.near(q.geom,.00015) if n is not q and n.net==q.net
            and n.layers&q.layers and q.geom.distance(n.geom)<=.00015]


def main():
    begin=time.monotonic()
    text=SOURCE.read_text(encoding='utf-8-sig')
    assert text.rstrip().endswith('READ_ONLY; COMPLETE')
    objects,_,_=G.load()
    index=G.Index(objects)
    report=[]
    for layer,net,xy in TARGETS:
        matches=[(i,q) for i,q in enumerate(objects) if q.kind=='TRACK' and q.net==net and layer in q.layers
                 and tuple(map(float,q.src[3:7]))==xy]
        assert len(matches)==1,(layer,net,xy)
        identity,target=matches[0]
        near=contacts(target,index)
        old=[(i,q) for i,q in enumerate(objects) if q.net==net and q.kind not in ('HOLE','KEEPOUT')]
        new=[(i,q) for i,q in old if i!=identity]
        _,_,splits=preserved(old,new,{identity})
        record={'target':desc(target),'whole_track_removal_preserves_retained_connections':not splits,
                'split_group_count':len(splits),
                'contacts':[dict(desc(q),covers_target_start=q.geom.buffer(.00015).covers(Point(*xy[:2])),
                                 covers_target_end=q.geom.buffer(.00015).covers(Point(*xy[2:]))) for q in near],
                'adjacent_contacts':[{'neighbor':desc(q),'contacts':[desc(n) for n in contacts(q,index)]} for q in near]}
        if not splits:
            branch=[target]
            for _ in range(20):
                frontier=[]
                for q in branch:
                    for n in contacts(q,index):
                        if any(n is b for b in branch) or any(n is f for f in frontier):continue
                        frontier.append(n)
                if len(frontier)!=1 or frontier[0].kind!='TRACK':break
                q=frontier[0]
                if 'INCOMP=False' not in q.src or 'INPOLY=False' not in q.src:break
                branch.append(q)
            record['unique_track_branch']=[desc(q) for q in branch]
            record['branch_frontier']=[dict(desc(q),contacts=[desc(n) for n in contacts(q,index)]) for q in frontier]
        report.append(record)
    result={'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            'tracks':report,'seconds':time.monotonic()-begin,
            'limits':['Six named legacy antenna tracks only; no blanket net pruning.',
                      'No native/router/CAD operations. Full poured geometry is absent.',
                      'No VREF or NetJ_FPC1_8 objects selected or modified.']}
    (EV/'ASTRA_BH_LEGACY_ANTENNA_CONTACTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'tracks':[{'target':r['target'],'unique_track_branch':r.get('unique_track_branch'),
                                'branch_frontier':r.get('branch_frontier')} for r in report],
                      'seconds':result['seconds']}),flush=True)


if __name__=='__main__':main()
