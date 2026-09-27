"""Read-only exact review of the user edit exported before the stopped BG apply."""
from collections import Counter
import csv
import hashlib
import json
import os
from pathlib import Path
import astra_verify_routing_delta as D
from astra_check_final_opens_graph import partitions, preserved

EV = Path(__file__).resolve().parent.parent / 'evidence'
BEFORE = EV / 'GEOMETRY_C2_6L_BF.txt'
AFTER = EV / 'GEOMETRY_UNSAVED_BEFORE_BG.txt'


def write_rows(path, objects):
    columns = 'kind,group,net,layer,x1,y1,x2,y2,w,d,h,conn,relax'.split(',')
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for o in objects:
            row = dict(kind=o['kind'], group='USER_EDIT_PRESERVE', net=o['net'],
                       layer=o['layer'] or 'Multi Layer', conn='observed user edit; read-only evidence', relax=0)
            names = ('x1','y1','x2','y2','w') if o['kind']=='TRACK' else ('x1','y1','d','h')
            row.update(zip(names, o['values']))
            writer.writerow(row)


def main():
    before, after = D.geometry(BEFORE), D.geometry(AFTER)
    old_rows = Counter(o['source'] for o in before['free'])
    new_rows = Counter(o['source'] for o in after['free'])
    lookup = {o['source']: o for o in before['free']+after['free']}
    removed = [lookup[r] for r in (old_rows-new_rows).elements()]
    added = [lookup[r] for r in (new_rows-old_rows).elements()]
    unchanged = {key:before[key]==after[key] for key in ('pads','comps','fixed')}
    user_adds, user_dels = EV/'ASTRA_USER_EDIT_OBSERVED_ADDS.csv', EV/'ASTRA_USER_EDIT_OBSERVED_DELS.csv'
    write_rows(user_adds, added)
    write_rows(user_dels, removed)
    os.environ['GEOM_FILE'] = str(BEFORE)
    import geom as G
    def net_objects(path):
        G.GEOM = str(path)
        return [('native:'+ '|'.join(o.src), o) for o in G.load()[0]
                if o.net=='NetJ_FPC1_8' and o.kind not in ('HOLE','KEEPOUT')]
    old, new = net_objects(BEFORE), net_objects(AFTER)
    removed_ids = {i for i,_ in old} - {i for i,_ in new}
    first, second, splits = preserved(old, new, removed_ids)
    before_pad_components = {o.comp+'.'+o.name:first[i] for i,o in old if o.kind=='PAD'}
    after_pad_components = {o.comp+'.'+o.name:second[i] for i,o in new if o.kind=='PAD'}
    target_pads_connected = (set(after_pad_components)=={'J_FPC1.8','R_VREF1.2'}
                             and len(set(after_pad_components.values()))==1)
    original_dels = D.plan(EV/'ASTRA_CS_FINAL_DELS.csv', False)
    candidate_rows = D.plan(EV/'ASTRA_CS_FINAL_ADDS.csv', True)+original_dels
    deleted=set()
    matches=[]
    for row in original_dels:
        ids=[i for i,o in enumerate(after['free']) if i not in deleted and D.match_error(row,o,.00015) is not None]
        matches.append({'row':row['source'],'match_count':len(ids)})
        if len(ids)==1:
            deleted.add(ids[0])
    scope = (all(unchanged.values()) and len(added)==7 and len(removed)==6
             and all(o['kind']=='TRACK' and o['net']=='NetJ_FPC1_8'
                     and o['layer']=='Top Layer' and o['values'][4]==.2 for o in added+removed))
    report = {
        'observed_scope_passed':scope,
        'unchanged_exported_groups':unchanged,
        'exported_group_counts':{key:sum(before[key].values()) for key in ('pads','comps','fixed')},
        'free_counts_before':D.counts(before['free']), 'free_counts_after':D.counts(after['free']),
        'removed_free_copper':removed, 'added_free_copper':added,
        'zero_length_added_tracks':[o for o in added if o['kind']=='TRACK' and o['values'][:2]==o['values'][2:4]],
        'user_net_graph':{'before_component_count':len(set(first.values())),
                          'after_component_count':len(set(second.values())),
                          'retained_connections_preserved':not splits,
                          'pad_components_before':before_pad_components,
                          'pad_components_after':after_pad_components,
                          'j_fpc1_pin8_r_vref1_pin2_connected':target_pads_connected},
        'cs_rebase':{'all_48_deletions_still_match_uniquely':len(matches)==48 and all(r['match_count']==1 for r in matches),
                     'candidate_never_touches_user_edited_net':all(r['net']!='NetJ_FPC1_8' for r in candidate_rows),
                     'deletion_matches':matches,
                     'note':'Candidate CSVs remain unchanged. Run full geometric checks and graph checks against the newly saved user-state native export before any native apply.'},
        'inputs':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in
                  (BEFORE,AFTER,EV/'ASTRA_CS_FINAL_ADDS.csv',EV/'ASTRA_CS_FINAL_DELS.csv')],
        'limits':['Unsaved native export is evidence of the live state, not proof of a saved PCB document.',
                  'This script does not change, clean, or remove the user edit, including its zero-length track.',
                  'No routing or native calls. Native save/reopen, DRC and rule/stack comparison remain separate.']}
    out=EV/'ASTRA_USER_EDIT_BEFORE_BG_REVIEW.json'
    out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    summary={k:v for k,v in report.items() if k not in ('removed_free_copper','added_free_copper','inputs','limits','cs_rebase')}
    summary['cs_rebase']={k:v for k,v in report['cs_rebase'].items() if k!='deletion_matches'}
    print(json.dumps(summary,indent=2))
    print('Evidence: '+str(out))
    return 0 if scope and not splits and target_pads_connected and report['cs_rebase']['all_48_deletions_still_match_uniquely'] else 1


if __name__=='__main__':
    raise SystemExit(main())
