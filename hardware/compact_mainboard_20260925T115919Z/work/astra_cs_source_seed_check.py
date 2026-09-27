"""Local fixed-BF CS source pad via/stub checks, no router or CAD operations."""
import csv
import hashlib
import json
import math
import os
from pathlib import Path
EV = Path(__file__).resolve().parent.parent / 'evidence'
GEOM = EV/'GEOMETRY_C2_6L_BF.txt'
DEST = EV/'ASTRA_BF_CS_ESCAPE_SEED_ADDS.csv'
os.environ['GEOM_FILE'] = str(GEOM)
os.environ['BOARD_BOX'] = '12,12,67.1,44'
import geom as G
from shapely.geometry import Point


def main():
    objects,_,_ = G.load()
    index = G.Index(objects)
    net = 'WIFI_SPI_CS'
    trials, chosen = [], None
    targets = [('R_WIFI_CS_PD','1',(46.68,43.2)),('U_WIFI1','24',(42.126,43.745))]
    targets += [('EXISTING_CS_TRACK','-',(round(43.125+i*.2,4),43.875)) for i in range(14)]
    for ref,pin,start in targets:
        sites = ([(start[0],round(start[1]+offset,4)) for offset in (-.5,.5,-.6,.6,-.7,.7,-.8,.8,-.9,.9)]
                 if ref=='EXISTING_CS_TRACK' else [start]+[(round(start[0]+i*.1,4),round(start[1]+j*.1,4)) for i in range(-3,4) for j in range(-3,4) if (i or j)])
        sites.sort(key=lambda p:math.dist(p,start))
        for p in sites:
            via = G.via(net,*p,.45,.20)
            hole = Point(*p).buffer(.1)
            copper = [{'net':q.net,'ref':q.comp,'pin':q.name,'kind':q.kind,'gap':gap,'required':need,'native_record':q.src}
                      for q,gap,need in index.violations(via)]
            near_holes = [] if index.htree is None else [index.holes[int(i)] for i in index.htree.query(hole.buffer(.451))]
            drill = [q.src for q in near_holes if q.geom.distance(hole)<G.hole_gap(q)-1e-6]
            stub = None if p==start else G.track(net,'Top Layer',[start,p],.18)
            stub_ok = stub is None or (G.edge_ok(stub.geom) and not index.violations(stub))
            row = {'ref':ref,'pin':pin,'pad_center':start,'point':p,'copper_blockers':copper,'hole_blockers':drill,
                   'edge_clear':G.edge_ok(via.geom),'top_018_stub_clear':bool(stub_ok)}
            row['passed'] = not copper and not drill and row['edge_clear'] and stub_ok
            trials.append(row)
            if row['passed']:
                chosen=row
                print('FIRST_LEGAL '+json.dumps(row),flush=True)
                break
        if chosen:
            break
    report = {'geometry':str(GEOM),'sha256':hashlib.sha256(GEOM.read_bytes()).hexdigest(),'checked':trials,'chosen':chosen,
              'limits':['Local fixed copper only; native repour and DRC required.','Seed remains planning evidence, no CAD modification.']}
    (EV/'ASTRA_BF_CS_SOURCE_SEED_CHECK.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    if chosen:
        x,y=chosen['point']; sx,sy=chosen['pad_center']
        candidate=G.via(net,x,y,.45,.20)
        overlaps_pad=any(q.kind=='PAD' and q.net==net and candidate.geom.intersects(q.geom) for q in objects)
        group='ASTRA_BF_CS_SOURCE_ESCAPE'+(' VIP' if overlaps_pad else '')
        rows=[dict(kind='VIA',group=group,net=net,layer='Multi Layer',x1=x,y1=y,d=.45,h=.20,conn=chosen['ref']+'.'+chosen['pin']+' CS source seed',relax=0)]
        if (x,y)!=(sx,sy):
            rows.append(dict(kind='TRACK',group=group,net=net,layer='Top Layer',x1=sx,y1=sy,x2=x,y2=y,w=.18,conn='CS source stub',relax=0))
        fields=['kind','group','net','layer','x1','y1','x2','y2','w','d','h','conn','relax']
        for filename,output_rows in [('ASTRA_BF_CS_SOURCE_ESCAPE_SEED_ADDS.csv',rows),
                ('ASTRA_BF_CS_BOTH_ESCAPE_SEEDS_ADDS.csv',list(csv.DictReader(DEST.open()))+rows)]:
            with (EV/filename).open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(output_rows)
    print(json.dumps({'sites_checked':len(trials),'chosen':chosen},indent=2))


if __name__=='__main__':
    main()
