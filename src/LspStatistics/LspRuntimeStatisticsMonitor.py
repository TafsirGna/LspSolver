#!/usr/bin/python3.5
# -*-coding: utf-8 -*

class LspRuntimeStatisticsMonitor:
    """
    """

    instance = None

    def __init__(self) -> None:
        """
        """
        self.popInitClockStart = None
        self.popInitClockEnd = None

        pass

    def reportPopInit(self):
        print(f"{self.popInitClockEnd - self.popInitClockStart} second(s)")

    def report(self):
        """
        """

        #
        self.reportPopInit()

        pass