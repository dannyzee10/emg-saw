"""Read-only verification of the bounded BI-to-BJ antenna cleanup."""
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
FROZEN={
    'ASTRA_BH_ALL_ANTENNA_BOUNDED_ADDS.csv':'f24dd4dfefbdf815dfcf2d79d92ae562c9ca41320474c86ef86c65c633e494d0',
    'ASTRA_BH_ALL_ANTENNA_BOUNDED_DELS.csv':'a39e559cdb35abd7f5beddd1e76a865f999363c9c36a5b0d50a086531f3ed057',
}


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--after-pcb',type=Path,default=PCB,
                        help='Use an immutable BJ backup when reviewing after a subsequent save.')
    options=parser.parse_args()
    args=argparse.Namespace(before=EV/'GEOMETRY_C2_6L_BI.txt',after=EV/'GEOMETRY_C2_6L_BJ.txt',
                            adds=EV/'ASTRA_BH_ALL_ANTENNA_BOUNDED_ADDS.csv',
                            dels=EV/'ASTRA_BH_ALL_ANTENNA_BOUNDED_DELS.csv',tol_mm=.00015,allow_move=[])
    apply_path=EV/'ASTRA_APPLY_BJ.txt'
    lines=D.read_text(apply_path).splitlines()
    applied=(bool(lines) and lines[-1]=='COMPLETE' and 'SAVED' in lines
             and 'PHASE1_OK|TRACKS=8|VIAS=0|DELETES=19|RULES=0' in lines
             and 'AFTER_REOPEN|NET_TRACKS=2281|VIAS=470|TENTED_BOTH=0|RULES=147' in lines)
    adds,dels=D.plan(args.adds,True),D.plan(args.dels,False)
    plan_passed=(all(sha(EV/name)==digest for name,digest in FROZEN.items())
                 and Counter(r['kind'] for r in adds)=={'TRACK':8}
                 and Counter(r['kind'] for r in dels)=={'TRACK':19}
                 and all(r['net']!='NetJ_FPC1_8' for r in adds+dels))
    geometry=D.verify(args)
    before_geom,after_geom=D.geometry(args.before),D.geometry(args.after)
    count_passed=(sum(before_geom['pads'].values())==sum(after_geom['pads'].values())==812
                  and sum(before_geom['comps'].values())==sum(after_geom['comps'].values())==231)
    user_path=EV/'ASTRA_USER_EDIT_OBSERVED_ADDS.csv'
    user_rows=D.plan(user_path,True)
    user_matches=[{'track':r,'before_match_count':sum(D.match_error(r,o,.00015) is not None for o in before_geom['free']),
                   'after_match_count':sum(D.match_error(r,o,.00015) is not None for o in after_geom['free'])}
                  for r in user_rows]
    user_preserved=(len(user_rows)==7 and all(r['kind']=='TRACK' and r['net']=='NetJ_FPC1_8'
                                             and r['layer']=='Top Layer' and r['values'][4]==.2 for r in user_rows)
                    and all(r['before_match_count']==r['after_match_count']==1 for r in user_matches))
    tp_records=[r for r in after_geom['pads'].elements() if r.startswith('PAD|FREE|TP_GND_DIG|')]
    tp_passed=(len(tp_records)==1 and tp_records[0].split('|')[3:7]==['GND','Top Layer','56.8710','44.8290'])
    graph_path=EV/'ASTRA_BI_ANTENNA_GRAPH.json'
    graph=json.loads(graph_path.read_text(encoding='utf-8-sig'))
    input_hashes={str(p):sha(p) for p in (args.before,args.adds,args.dels)}
    graph_passed=(graph['passed'] and len(graph['inputs'])==3
                  and all(input_hashes.get(r['path'])==r['sha256'] for r in graph['inputs'])
                  and all(r['all_retained_copper_connections_preserved'] and not r['detached_additions']
                          for r in graph['graphs'].values())
                  and all(r['retained_connectivity_at_original_width_thresholds_preserved']
                          for r in graph['power_width_path_preservation'].values()))
    before_drc=EV/'DRC_C2_6L_BI.txt.html'
    after_drc=EV/'DRC_C2_6L_BJ.txt.html'
    before,after=drc(before_drc),drc(after_drc)
    old,new=Counter(before['details']),Counter(after['details'])
    antennas=lambda rows:Counter({r:n for r,n in rows.items() if r.startswith('Net Antennae:')})
    opens=lambda rows:Counter({r:n for r,n in rows.items() if r.startswith('Un-Routed Net Constraint:')})
    old_ant,new_ant=antennas(old),antennas(new)
    old_open,new_open=opens(old),opens(new)
    antenna_passed=sum(old_ant.values())==10 and not new_ant
    only_antennas_changed=new==old-old_ant
    prefixes=('Clearance Constraint','Short-Circuit Constraint','Width Constraint','Component Clearance Constraint',
              'Routing Layers','Routing Via')
    coverage={p:{'present':any(n.startswith(p) for n,_ in after['summary']),
                 'violation_count':sum(v for n,v in after['summary'] if n.startswith(p))
                 if any(n.startswith(p) for n,_ in after['summary']) else None} for p in prefixes}
    critical_clean=all(coverage[p]['present'] and coverage[p]['violation_count']==0 for p in prefixes)
    backup=EV/'ASTRA_BI_BEFORE_BJ_20260927/EMG_MainBoard_Layout.PcbDoc'
    a,b=S.snapshot(backup),S.snapshot(options.after_pcb)
    structure=S.compare(a,b)
    ca,na=S.board_parameters(a['streams']['Components6/Data'])
    cb,nb=S.board_parameters(b['streams']['Components6/Data'])
    changed_component_fields=[key for key in sorted(set(ca)|set(cb)) if ca.get(key)!=cb.get(key)]
    components_design=na==nb==231 and all(key=='SELECTION' for key in changed_component_fields)
    class_streams_unchanged=all(a['streams'].get(n)==b['streams'].get(n) and n in a['streams']
                                for n in ('Classes6/Data','Classes6/Header'))
    documents=[]
    manifest=EV/'ASTRA_BFS_BEFORE_BG_20260927/BEFORE_HASHES.json'
    for r in json.loads(manifest.read_text(encoding='utf-8-sig')):
        name=Path(r.get('Path',r.get('Name',''))).name
        if Path(name).suffix.lower() in ('.schdoc','.prjpcb'):
            expected=r.get('Hash',r.get('SHA256','')).lower()
            actual=sha(PCB.parent/name)
            documents.append({'name':name,'before_sha256':expected,'after_sha256':actual,'unchanged':actual==expected})
    documents_passed=len(documents)==9 and all(r['unchanged'] for r in documents)
    scope=(components_design and class_streams_unchanged and documents_passed
           and all(v for k,v in structure['separate_invariants'].items() if k!='components_bytes_unchanged'))
    authorized=applied and plan_passed and graph_passed and geometry['passed'] and count_passed and user_preserved and tp_passed and scope
    passed=bool(authorized and antenna_passed and not new_open and only_antennas_changed and critical_clean)
    report={'passed':passed,'authorized_copper_delta_and_saved_design_scope_passed':bool(authorized),
            'native_apply_save_reopen_passed':applied,'frozen_8_add_19_delete_plan_scope_passed':plan_passed,
            'prewrite_graph_and_power_input_hashes_match':graph_passed,'native_geometry_delta':geometry,
            'all_812_pads_231_components_preserved':count_passed and geometry['passed'],
            'all_seven_user_tracks_preserved':user_preserved,'user_track_matches':user_matches,
            'tp_gnd_dig_exact_saved_location_passed':tp_passed,'tp_gnd_dig_native_record':tp_records,
            'native_drc':{'before_total':before['total'],'after_total':after['total'],
                          'before_open_count':sum(old_open.values()),'after_open_count':sum(new_open.values()),
                          'before_antenna_count':sum(old_ant.values()),'after_antenna_count':sum(new_ant.values()),
                          'only_ten_antennas_removed_other_violations_identical':only_antennas_changed,
                          'added_violations':list((new-old).elements()),'removed_violations':list((old-new).elements()),
                          'category_coverage':coverage,'remaining_nonzero_summary_rows':[(n,v) for n,v in after['summary'] if v]},
            'saved_structure':structure,'component_design_parameters_preserved':components_design,
            'changed_component_fields':changed_component_fields,'classes_bytes_unchanged':class_streams_unchanged,
            'schematics_and_project':documents,
            'inputs':[{'path':str(p),'sha256':sha(p)} for p in (args.before,args.after,args.adds,args.dels,graph_path,
                       user_path,apply_path,before_drc,after_drc,manifest)],
            'limits':['Native geometry preserves fields exported for pads/components; raw opaque protected-stream differences remain recorded separately.',
                      'Power proof preserves prior track-width paths; it does not calculate thermal or current capacity.',
                      'Remaining silk/board violations and fabrication audit are separate from this routing-cleanup proof.',
                      'No native/CAD writes, full routing or geometry edits performed by this reviewer.']}
    out=EV/'ASTRA_BJ_INDEPENDENT_REVIEW.json'
    out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    summary={k:v for k,v in report.items() if k not in ('native_geometry_delta','saved_structure','inputs','schematics_and_project','limits','user_track_matches')}
    print(json.dumps(summary,indent=2))
    md=['# BJ independent cleanup review','',
        f"**{'PASS' if passed else 'REVIEW REQUIRED'}** for the exact BI-to-BJ bounded antenna cleanup.",'',
        f"Native apply/save/reopen: {applied}. Exact 8 track additions / 19 track deletions: {bool(plan_passed and geometry['passed'])}. No via, pad or component movement is authorized in this stage.",'',
        f"All 812 pads and 231 components preserved: {bool(count_passed and geometry['passed'])}. All seven user-edited tracks preserved: {user_preserved}. TP_GND_DIG remains at (56.871,44.829) mm: {tp_passed}.",'',
        f"Actual native DRC: {before['total']} to {after['total']} entries; opens {sum(old_open.values())} to {sum(new_open.values())}; antennae {sum(old_ant.values())} to {sum(new_ant.values())}. Only the ten antenna entries removed: {only_antennas_changed}. Newly added warnings: {sum((new-old).values())}.",'',
        f"All six required native categories (clearance, short, width, component clearance, routing layers and via style) present and zero: {critical_clean}.",'',
        f"Graph and power-path proof matches exact current inputs: {graph_passed}. Rules/nets/stack/component design/classes preserved: {scope}. All nine schematic/project hashes match BFS: {documents_passed}.",'',
        'Remaining native report entries:']
    md += [f'- {name}: {count}' for name,count in after['summary'] if count]
    if new-old: md += ['', 'New warnings requiring review:']+[f'- {r}' for r in (new-old).elements()]
    md += ['', 'Full hashes, exact native delta and raw stream diagnostics are retained in `ASTRA_BJ_INDEPENDENT_REVIEW.json`. This is routing-cleanup evidence, not fabrication release.']
    out.with_suffix('.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    return 0 if passed else 1


if __name__=='__main__': raise SystemExit(main())
