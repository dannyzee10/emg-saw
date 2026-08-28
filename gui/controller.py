"""
MainController — coordinates the AcquisitionModel and high-level start/stop.
Keeps UI logic separated from data acquisition.
"""


class MainController:
    def __init__(self, model):
        self.model = model

    def start(self):
        self.model.start()

    def stop(self):
        self.model.stop()