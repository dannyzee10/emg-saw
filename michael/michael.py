"""Michael — the EMG research-centre AI assistant.

    ask(message) -> {"answer": str, "action": str|None, "source": "llm"|"fallback"}

Grounds a local Ollama model (Qwen2.5) on ``michael/knowledge.md`` and answers questions about
the EMG acquisition system. If the model/server is unreachable it falls back to a scripted
intent map, so the game never hard-fails. The whole LLM is behind this one ``ask()`` function,
so the host (URL/model) or a cloud swap never touches the game.

Config via env:
    MICHAEL_URL     default http://localhost:11434     (Ollama; use an SSH tunnel to the server)
    MICHAEL_MODEL   default qwen2.5:32b-instruct       (needs a ~20 GB pull on the GPU server)
    MICHAEL_TIMEOUT default 120 (seconds)              (bigger model + fuller answers = allow more time)

Standalone test:  python -m michael.michael "how do I smooth my data?"
"""
import json
import os
import re
import ssl
import urllib.request
from pathlib import Path

# the shared proxy uses a self-signed cert (to tunnel HTTPS through Chinese frp nodes), so skip verify
_NOVERIFY = ssl.create_default_context()
_NOVERIFY.check_hostname = False
_NOVERIFY.verify_mode = ssl.CERT_NONE

HERE = Path(__file__).resolve().parent
_kb = HERE / "knowledge.md"
KNOWLEDGE = _kb.read_text(encoding="utf-8") if _kb.exists() else ""

URL = os.environ.get("MICHAEL_URL", "http://localhost:11434").rstrip("/")
MODEL = os.environ.get("MICHAEL_MODEL", "qwen2.5:32b-instruct")
TIMEOUT = float(os.environ.get("MICHAEL_TIMEOUT", "120"))
TOKEN = os.environ.get("MICHAEL_TOKEN", "")   # sent as X-Michael-Token when reaching the shared proxy

SYSTEM = (
    "You are Michael, a knowledgeable senior researcher and AI lab assistant in an EMG (muscle-signal) "
    "research-centre. Answer ONLY about this EMG acquisition system, using the knowledge below. "
    "Give a COMPLETE, well-structured answer: briefly explain the concept, why it matters, and the "
    "concrete steps to do it in THIS system, including the relevant settings, typical values, and any "
    "pitfalls to watch for. Use short paragraphs or a few bullet points when that makes it clearer, and "
    "keep the language plain enough for a student to follow. Name the room to visit by name (e.g. 'the "
    "Methods room'). Do NOT output any code, 'ACTION', or 'goto' path -- just talk naturally. If asked "
    "something outside the EMG lab, briefly say you only help with the EMG lab and point them back to it."
    "\n\n=== SYSTEM KNOWLEDGE ===\n" + KNOWLEDGE
)

# scripted fallback: (keyword tuple) -> (answer, action). First match wins.
INTENTS = [
    (("smooth", "envelope", "rms env"),
     "Smoothing turns the spiky EMG into an activation curve: pick RMS or mean-absolute and a window (ms) "
     "-- a bigger window is smoother. The Smoothing researcher in the Methods room sets it.",
     "goto:methods/smoothing"),
    (("rectif",),
     "Rectify flips the signal so it's all positive (|EMG|) -- a step before smoothing. See the Rectify "
     "researcher in the Methods room.",
     "goto:methods/rectify"),
    (("filter", "noise", "mains", "notch", "bandpass", "band-pass", "hum"),
     "Filtering cleans the signal: a 20-450 Hz band-pass is on by default, and a 50/60 Hz notch removes "
     "power-line hum if you see it. The Filter researcher in the Methods room handles it.",
     "goto:methods/filter"),
    (("mvc", "normalize", "normalise", "percent", "%mvc", "calibrat", "maximum contraction", "compare"),
     "MVC is your strongest contraction; it becomes 100%, and %MVC then shows effort as a share of your max "
     "so results compare across people. Set it with the MVC researcher in the Live-Visualization room.",
     "goto:liveviz/mvc"),
    (("baseline", "electrode", "lead-off", "lead off", "connection", "connected", "dot", "drl"),
     "Before recording, relax the muscle and run the EMG Baseline check -- it should read green; the channel "
     "dot is green (connected), amber (poor/reference) or red (lead off). The Baseline researcher helps.",
     "goto:liveviz/baseline"),
    (("fatigue", "tired", "median freq", "mdf", "mnf", "mean freq", "target", "sustained"),
     "Fatigue shows as the median frequency falling during a sustained hold; use the %MVC Target guide to "
     "keep a constant effort. Set it up with the MVC researcher.",
     "goto:liveviz/mvc"),
    (("co-contraction", "cocontraction", "co contraction", "coactivation", "co-activation", "antagonist",
      "onset", "offset", "activation timing", "iemg", "integrated emg", "integral"),
     "Co-contraction, onset/offset timing and integrated EMG (iEMG) are computed after capture: record the "
     "muscles during your task, then open the recording in the Review room, which calculates these metrics "
     "and adds them to the report.",
     "goto:review/review"),
    (("review", "playback", "replay", "signal processing", "offline", "recorded"),
     "The Review room replays a recording, lets you re-process it, and makes a report; the Normalize "
     "researcher there scales it to a reference.",
     "goto:review/normalize"),
    (("record", "save", "capture", "report"),
     "Record captures the raw data and Stop saves it; then open it in the Review room to make a report.",
     "goto:review/review"),
    (("place", "placement", "where do i put", "forearm", "muscle", "sensor", "stick"),
     "The Sensor-Placement room has a researcher per body part who shows the correct vs incorrect electrode "
     "spot and checks your photo. Start there.",
     "goto:sensor/placement"),
    (("raw", "live", "scope", "see the signal", "visuali"),
     "The Live-Visualization room opens the scope so you can watch the raw EMG in real time.",
     "goto:liveviz/raw"),
]
DEFAULT = ("I'm Michael, your EMG lab assistant -- I can guide you through placing sensors, choosing methods "
           "like filtering or smoothing, calibrating MVC, recording, and reviewing your data. What would you "
           "like to do?", "goto:hall")

# navigation targets the game understands (used to validate any stray action the model emits)
VALID_ACTIONS = {a for _, _, a in INTENTS} | {DEFAULT[1]}


def _fallback(message):
    m = (message or "").lower()
    for keys, answer, action in INTENTS:
        if any(k in m for k in keys):
            return {"answer": answer, "action": action, "source": "fallback"}
    return {"answer": DEFAULT[0], "action": DEFAULT[1], "source": "fallback"}


def _parse_action(text):
    """Pull any trailing 'ACTION: goto:...' out, and strip stray goto/(room)/(npc) junk the model
    may append, so the user only ever sees clean prose."""
    action = None
    m = re.search(r"ACTION:\s*(goto:[\w/\-]+)", text, flags=re.IGNORECASE)
    if m:
        action = m.group(1)
        text = text[:m.start()] + text[m.end():]
    text = re.sub(r"\(\s*room\s*\)\s*/?\s*\w*\s*\(\s*npc\s*\)", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bACTION:\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"goto:[\w/\-]+", "", text, flags=re.IGNORECASE)
    text = text.replace("`", "").strip()
    return text, action


def ask(message, url=None, model=None, timeout=None):
    """Answer a user message. Uses Ollama; falls back to the scripted intents on any error."""
    message = (message or "").strip()
    if not message:
        return {"answer": DEFAULT[0], "action": DEFAULT[1], "source": "fallback"}
    base = (url or URL).rstrip("/")
    payload = json.dumps({
        "model": model or MODEL,
        "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": message}],
        "stream": False,
        "options": {"temperature": 0.3},
    }).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if TOKEN:
        headers["X-Michael-Token"] = TOKEN
    req = urllib.request.Request(base + "/api/chat", data=payload, headers=headers)
    ctx = _NOVERIFY if base.startswith("https") else None
    try:
        with urllib.request.urlopen(req, timeout=timeout or TIMEOUT, context=ctx) as r:
            data = json.loads(r.read().decode("utf-8"))
        content = (data.get("message") or {}).get("content", "").strip()
        if not content:
            return _fallback(message)
        # LLM writes the natural answer; navigation comes from the reliable intent rules where they
        # match, else the model's target (validated) — so the game is never sent to an invalid/wrong room.
        answer, model_action = _parse_action(content)
        scripted_action = _fallback(message)["action"]
        if scripted_action != DEFAULT[1]:
            action = scripted_action               # message clearly matches an intent -> reliable route
        elif model_action in VALID_ACTIONS:
            action = model_action                  # no clear intent -> trust the model's valid choice
        else:
            action = DEFAULT[1]                     # model invented/omitted + no intent -> the hall
        return {"answer": answer, "action": action, "source": "llm"}
    except Exception:
        return _fallback(message)


def main():
    import sys
    q = " ".join(sys.argv[1:]) or "how do I smooth my data?"
    print(json.dumps(ask(q), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
