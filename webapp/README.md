# EMG Research-Centre — Web Front-End (webapp/)

A pixel-art "research-centre" GUI (Phaser 3) that guides a user through the EMG acquisition
system with NPC "researchers" and an AI assistant, **Michael**. This front-end **launches and
configures the existing, tested Python EMG engine** — it never re-implements EMG DSP.

> **Golden rule:** do **NOT** edit `dsp/` or `gui/` (the validated engine). The game talks to
> Python only through the localhost server endpoints below.

## Folder layout
```
webapp/
  index.html                  # loads Phaser + src/main.js
  src/
    main.js                   # Phaser game config + scene registry
    scenes/                   # Boot, Reception, Hall, SensorRoom, MethodsRoom, LiveVizRoom, ReviewRoom
    systems/
      dialogue.js             # Pokemon-style dialogue box + multiple-choice
      npc.js                  # NPC sprite + bouncing "come here" bubble
      michael.js              # Michael chat UI -> POST /ask
      api.js                  # fetch() wrappers for the endpoints below
    data/rooms.json           # room / NPC / question tree (seed from ../AGENT_OWNERSHIP.yml)
  assets/{tiles,sprites,portraits,ui}/   # free pixel art (Kenney CC0 recommended)
```

## Run it
1. Backend (serves this folder + endpoints):  `python scripts/clinic_server.py`
   -> opens `http://127.0.0.1:8787/`
2. Front-end deps: install Node.js, then `npm i phaser` (or load Phaser from a CDN in index.html to start).
3. Michael (optional at first): install **Ollama**, `ollama pull llama3.1:8b` (or `qwen2.5:7b`).
   `/ask` falls back to scripted answers when Ollama isn't running.

## Backend endpoint contract (`scripts/clinic_server.py` — extends `scripts/emg_map_server.py`)
All JSON, same-origin, host `127.0.0.1:8787`. Every response includes `{ "ok": true/false, ... }`.

| Method | Path | Body / query | Returns |
|---|---|---|---|
| GET  | `/`, static | — | serves `webapp/` (index.html, src, assets) |
| GET  | `/rooms` | — | `{ok, rooms:[{id,name,npcs:[{id,name,question,choices}]}]}` (from `data/rooms.json`) |
| POST | `/config` | `{subject,age,session,sensor:{bodypart,side,muscle},methods:{smoothing:{algo,window_ms},notch,amp_pct}}` | `{ok, config_id}` — persists the session choices |
| POST | `/ask` | `{message, context?}` | `{ok, answer, action?}`  (`action` e.g. `"goto:methods/smoothing"`) |
| GET  | `/launch` | `?target=<key>` (+ uses the saved config) | `{ok, msg}` — starts the PyQt scope (existing whitelist pattern) |
| POST | `/verify_electrode` | multipart image | `{ok, verdict, message}` — *(later phase)* |

`launch` targets reuse the whitelist already in `emg_map_server.py` (`sim1/sim5/live1/live5`), extended so
the saved `/config` (coupling, channels, smoothing, notch, %MVC) is applied when the scope opens.

## Front-end API wrappers (`src/systems/api.js`)
```js
const BASE = "";  // same origin
export const getRooms    = ()       => fetch(`${BASE}/rooms`).then(r => r.json());
export const saveConfig  = (cfg)    => fetch(`${BASE}/config`, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(cfg)}).then(r => r.json());
export const askMichael  = (message)=> fetch(`${BASE}/ask`,    {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({message})}).then(r => r.json());
export const launchScope = (target) => fetch(`${BASE}/launch?target=${encodeURIComponent(target)}`).then(r => r.json());
```

## Michael contract
- `POST /ask {message}` -> `{answer, action?}`. `answer` is text for the dialogue box; optional `action`
  (`goto:<room>/<npc>`) lets the game walk the user there.
- Backed by Ollama (`127.0.0.1:11434`) grounded on `michael/knowledge.md`; a **scripted fallback** covers
  the core intents (filter, smooth, MVC, baseline, record, review) so it works with no model installed.

## Build order (start here)
- **P0** — a Phaser "hello room": tilemap + walking player + one NPC + a dialogue box. (Learn Phaser.)
- **P1** — Reception (name/age -> `POST /config`) -> Main Hall with Michael (intro + chat via `/ask`) + a Map button.
- Then P2 (Live-Viz room -> `/launch` the scope), P3 (Methods), P4 (Sensor placement), P5 (Review).

## Conventions
- Work on branch `webapp` (never `main`); commit + `git push origin webapp` daily with a one-line note.
- Keep commits small. The engine's existing 55 tests must stay green (you never touch `dsp/`/`gui/`).
