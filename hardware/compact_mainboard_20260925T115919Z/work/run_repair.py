"""Launch repair.py with the standard C2 6L router env and the full list of routed plan CSVs.
usage: python run_repair.py STATE OUT_TAG [KEY=VALUE ...]
  STATE   geometry/DRC state letter(s), e.g. Z  -> GEOMETRY_C2_6L_Z.txt + DRC_C2_6L_Z.json
  OUT_TAG output prefix in evidence/, e.g. REP_Y -> REP_Y_ADDS.csv / REP_Y_DELS.csv
  KEY=VALUE extra env (MARGIN, PASSES, REGIONS, FIRST_NETS, ONLY_NETS, DEBUG, ...)
Add each new write-safe round (*_ADDS_OK.csv) to PLANS."""
import os, subprocess, sys

PLANS = ['ROUTE_PLAN_C2TRIAL_OK', 'ROUTE_PLAN_C2R2_OK', 'ROUTE_PLAN_C2_6L1_OK', 'BATCH_C_OK', 'ROUTE_PLAN_C2_6L3_OK',
         'ROUTE_PLAN_C2_6L5_OK', 'ROUTE_PLAN_C2_6L6A_OK', 'ROUTE_PLAN_C2_6L7B_OK', 'REPAIR_ADDS_N3_OK', 'REG_MCU_ADDS_OK',
         'ROUTE_PLAN_C2_6L8A_OK', 'REG_ANA_ADDS_OK', 'REP_S_ADDS_OK', 'REP_T_ADDS_OK', 'REP_U_ADDS_OK', 'REP_V_ADDS_OK',
         'REP_X_ADDS_OK', 'REP_Y_ADDS_OK', 'REP_AC_ADDS_OK', 'REP_AE_ADDS_OK', 'REP_AI_ADDS_OK', 'REP_AJ_ADDS_OK', 'REP_AM_ADDS_OK', 'REP_AN_ADDS_OK', 'REP_AO_ADDS_OK', 'REP_AQ_ADDS_OK', 'REP_AS_ADDS_OK', 'REP_AU_ADDS_OK',
         'MERGE_G_ADDS_OK']
ENV = {'VIP': '1', 'NO_RELAX': '1', 'MCU_FANOUT': '1', 'BIG': '1', 'EXACT': '1', 'MARGIN': '0.025',
       'BK13_ZONES': '../evidence/BK13_ZONES_C2.csv', 'GRID': '9.5,9.5,69.6,46.5', 'BOARD_BOX': '12,12,67.1,44',
       'L5_RESERVED': '3V0_ANA:10.5,10.5,68.6,25.3;3V0_ANA:10.5,25.3,47.5,27.2;3V0_ANA:31.6,27.2,35.8,30.4',
       'R_ANA': '10.5,10.5;68.6,10.5;68.6,25.3;47.5,25.3;47.5,27.2;35.8,27.2;35.8,30.4;31.6,30.4;31.6,27.2;10.5,27.2',
       'PLANE_DEAD': '10.8,10.45,15.7,11.55'}      # L2/L4 pour fragment cut off by the corner TH pads (state Z export)
state, tag = sys.argv[1], sys.argv[2]
env = dict(os.environ, **ENV)
for kv in sys.argv[3:]:
    k, v = kv.split('=', 1)
    env[k] = v
env['GEOM_FILE'] = f'../evidence/GEOMETRY_C2_6L_{state}.txt'
ev = '../evidence/'
extra = [p for p in env.get('EXTRA_PLANS', '').split(',') if p]     # e.g. BK13_ESCAPE_PLAN_C2 together with RIP_BK13=1
cmd = [sys.executable, '-u', 'repair.py', f'{ev}DRC_C2_6L_{state}.json', f'{ev}{tag}_ADDS.csv', f'{ev}{tag}_DELS.csv'] + \
      [f'{ev}{p}.csv' for p in PLANS + extra]
sys.exit(subprocess.call(cmd, env=env))
