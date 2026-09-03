"""Tests for the Michael assistant: scripted-fallback intents, ACTION parsing, and that ask()
degrades gracefully (never crashes) when the Ollama server is unreachable."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from michael.michael import ask, _fallback, _parse_action


def test_fallback_maps_core_intents():
    assert _fallback("how do I smooth my data")["action"] == "goto:methods/smoothing"
    assert _fallback("what filter removes mains hum")["action"] == "goto:methods/filter"
    assert _fallback("how do I set the MVC")["action"] == "goto:liveviz/mvc"
    assert _fallback("check the electrode baseline")["action"] == "goto:liveviz/baseline"
    assert _fallback("I want to review my recorded data")["action"] == "goto:review/normalize"


def test_fallback_default_for_unknown():
    r = _fallback("tell me a joke about cats")
    assert r["action"] == "goto:hall" and r["source"] == "fallback"


def test_parse_action_extracts_and_strips():
    text, action = _parse_action("Do it in the Methods room.\nACTION: goto:methods/smoothing")
    assert action == "goto:methods/smoothing"
    assert "ACTION" not in text and "smoothing" not in text.lower()


def test_ask_falls_back_when_server_unreachable():
    # point at a dead port -> must fall back to the scripted answer, not raise
    r = ask("how do I smooth my data", url="http://127.0.0.1:1", timeout=1)
    assert r["source"] == "fallback" and r["action"] == "goto:methods/smoothing"


def test_ask_empty_message():
    r = ask("   ", url="http://127.0.0.1:1", timeout=1)
    assert r["action"] == "goto:hall"
