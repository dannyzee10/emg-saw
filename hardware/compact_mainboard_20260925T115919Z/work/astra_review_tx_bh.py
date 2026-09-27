"""Read-only BGM-to-BH verification of the final TX-only centred route."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import astra_verify_routing_delta as D
import astra_verify_pcb_structure as S
from astra_review_vc1_bd import drc

EV=Path(__file__).resolve().parent.parent/'evidence'
PCB=EV.parent/'C2_COMPACT_4L_2SIDE/MainBoard/EMG_MainBoard_Layout.PcbDoc'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    args=argparse.Namespace(before=EV/'GEOMETRY_C2_6L_BGM.txt',after=EV/'GEOMETRY_C2_6L_BH.txt',
                            adds=EV/'ASTRA_BGM_TX_CENTERED_ADDS.csv',dels=EV/'ASTRA_EMPTY_COPPER.csv',
                            tol_mm=.00015,allow_move=[])
    apply_path=EV/'ASTRA_APPLY_BH_CENTERED.txt'
    lines=D.read_text(apply_path).splitlines()
    applied=(bool(lines) and lines[-1]=='COMPLETE' and 'SAVED' in lines
             and 'PHASE1_OK|TRACKS=23|VIAS=6|DELETES=0|RULES=0' in lines
             and 'AFTER_REOPEN|NET_TRACKS=2292|VIAS=470|TENTED_BOTH=0|RULES=147' in lines)
    adds,dels=D.plan(args.adds,True),D.plan(args.dels,False)
    plan_passed=(sha(args.adds)=='9323bf9baf5773f8903b223618418418f1a10d2da69f1483cfb88f79f411a99a'
                 and Counter(r['kind'] for r in adds)=={'TRACK':23,'VIA':6} and not dels
                 and all(r['net']=='MCU_WIFI_UART_TX' for r in adds)
                 and all((r['layer'] in ('Top Layer','Mid Layer 2','Mid Layer 4','Bottom Layer')
                          and r['values'][4] in (.15,.2)) if r['kind']=='TRACK'
                         else r['values'][2:]==(.45,.2) for r in adds))
    geometry=D.verify(args)
    graph_path=EV/'ASTRA_BGM_TX_CENTERED_GRAPH.json'
    graph=json.loads(graph_path.read_text(encoding='utf-8-sig'))
    input_hashes={str(p):sha(p) for p in (args.before,args.adds,args.dels)}
    graph_passed=(graph['passed'] and len(graph['inputs'])==3
                  and all(input_hashes.get(r['path'])==r['sha256'] for r in graph['inputs'])
                  and all(graph['graphs'][n]['requested_endpoints_connected_after']
                          for n in ('MCU_WIFI_UART_TX','WIFI_SPI_CS')))
    before,after=drc(EV/'DRC_C2_6L_BGM.txt.html'),drc(EV/'DRC_C2_6L_BH.txt.html')
    old,new=Counter(before['details']),Counter(after['details'])
    old_opens=Counter({r:n for r,n in old.items() if r.startswith('Un-Routed Net Constraint:')})
    new_opens=Counter({r:n for r,n in new.items() if r.startswith('Un-Routed Net Constraint:')})
    target=Counter({r:n for r,n in old_opens.items() if r.startswith('Un-Routed Net Constraint: Net MCU_WIFI_UART_TX Between ')})
    resolved=sum(target.values())==1 and not new_opens and new_opens==old_opens-target
    only_target_changed=new==old-target
    prefixes=('Clearance Constraint','Short-Circuit Constraint','Width Constraint','Component Clearance Constraint',
              'Routing Layers Constraint','Routing Via Style Constraint')
    coverage={p:{'present':any(n.startswith(p) for n,_ in after['summary']),
                 'violation_count':sum(v for n,v in after['summary'] if n.startswith(p))
                 if any(n.startswith(p) for n,_ in after['summary']) else None} for p in prefixes}
    core_clean=all(coverage[p]['present'] and coverage[p]['violation_count']==0 for p in prefixes[:4])
    backup=EV/'ASTRA_BGM_BEFORE_BH_20260927/EMG_MainBoard_Layout.PcbDoc'
    a,b=S.snapshot(backup),S.snapshot(PCB)
    structure=S.compare(a,b)
    ca,na=S.board_parameters(a['streams']['Components6/Data'])
    cb,nb=S.board_parameters(b['streams']['Components6/Data'])
    changed_fields=[key for key in sorted(set(ca)|set(cb)) if ca.get(key)!=cb.get(key)]
    components_design=(na==nb==231 and all(key=='SELECTION' for key in changed_fields))
    documents=[]
    manifest=EV/'ASTRA_BFS_BEFORE_BG_20260927/BEFORE_HASHES.json'
    for r in json.loads(manifest.read_text(encoding='utf-8-sig')):
        name=Path(r.get('Path',r.get('Name',''))).name
        if Path(name).suffix.lower() in ('.schdoc','.prjpcb'):
            expected=r.get('Hash',r.get('SHA256','')).lower()
            documents.append({'name':name,'before_sha256':expected,'after_sha256':sha(PCB.parent/name),
                              'unchanged':sha(PCB.parent/name)==expected})
    scope=(components_design and all(v for k,v in structure['separate_invariants'].items()
                                     if k!='components_bytes_unchanged')
           and len(documents)==9 and all(r['unchanged'] for r in documents))
    user_rows=D.plan(EV/'ASTRA_USER_EDIT_OBSERVED_ADDS.csv',True)
    before_geom,after_geom=D.geometry(args.before),D.geometry(args.after)
    user_preserved=(len(user_rows)==7 and all(sum(D.match_error(r,o,.00015) is not None for o in g['free'])==1
                                            for r in user_rows for g in (before_geom,after_geom)))
    authorized=applied and plan_passed and graph_passed and geometry['passed'] and resolved and core_clean and scope and user_preserved
    report={'passed':bool(authorized and only_target_changed),'authorized_copper_delta_and_scope_passed':bool(authorized),
            'native_apply_save_reopen_passed':applied,'frozen_plan_scope_passed':plan_passed,
            'prewrite_graph_inputs_and_cs_tx_endpoints_passed':graph_passed,'native_geometry_delta':geometry,
            'all_seven_user_tracks_preserved':user_preserved,
            'native_drc':{'before_total':before['total'],'after_total':after['total'],
                          'before_open_count':sum(old_opens.values()),'after_open_count':sum(new_opens.values()),
                          'only_mcu_wifi_uart_tx_resolved':resolved,'only_target_violation_changed':only_target_changed,
                          'added_violations':list((new-old).elements()),'removed_violations':list((old-new).elements()),
                          'category_coverage':coverage},
            'saved_structure':structure,'component_design_fields_unchanged_except_ui_selection':components_design,
            'changed_component_fields':changed_fields,'schematics_and_project':documents,
            'inputs':[{'path':str(p),'sha256':sha(p)} for p in (args.before,args.after,args.adds,args.dels,graph_path,apply_path,
                       EV/'DRC_C2_6L_BGM.txt.html',EV/'DRC_C2_6L_BH.txt.html')],
            'limits':['Missing DRC categories are unverified, not checked zero.',
                      'Raw protected-stream differences remain reported; exported pads/components and non-selection component parameters are checked separately.',
                      'Zero opens is connectivity completion, not fabrication release; prior antenna/silkscreen/board issues remain.',
                      'No native/CAD writes or router calls.']}
    out=EV/'ASTRA_BH_INDEPENDENT_REVIEW.json'
    out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('native_geometry_delta','saved_structure','inputs','schematics_and_project','limits')},indent=2))
    print('Geometry: '+str(geometry['passed'])+'; saved scope: '+str(scope)+'; report: '+str(out))
    return 0 if report['passed'] else 1


if __name__=='__main__': raise SystemExit(main())
