#!/usr/bin/env python3
"""
EMG Scope launcher for the SAW (MVC) layout — always start the scope through this.

The GUI is a package (gui.emg_plotter) that imports gui.model / gui.controller /
communication.sources / dsp.dsp. This launcher puts the repo ROOT on sys.path so
those package imports resolve, then runs the scope.

    # real hardware (CP4 binary firmware @ 2 kHz on COM8):
    python emgscope.py --port COM8 --baud 921600 --channels 1 --fs 2000 --coupling AC --kick

    # 5 channels (after firmware NCH=5):
    python emgscope.py --port COM8 --baud 921600 --channels 5 --fs 2000 --kick

    # no hardware — UI demo:
    python emgscope.py --sim --channels 5
"""
import os
import runpy
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

runpy.run_module("gui.emg_plotter", run_name="__main__")
