#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from threading import Thread
from time import perf_counter, time
from LspLibrary import bcolors
import time
import matplotlib.pyplot as plt


class LspRuntimeMonitor:
    """
    """

    clockStart = None
    clockEnd = None
    popStatistics = {"min": [], "max": [], "mean": [], "std": []}
    outputString = ""
    outputFilePath = "data/output/output.txt"
    verbose = False
    running = True

    def __init__(self) -> None:
        """
        """
        pass

    @classmethod
    def duration(cls):
        """
        """
        return  f"{cls.clockEnd - cls.clockStart} second(s)"

    @classmethod
    def started(cls):
        """
        """
        cls.running = True
        LspRuntimeMonitor.clockStart = perf_counter()

        print(f"{bcolors.OKGREEN}Processing input data.{bcolors.ENDC}")
        # Thread(cls.waitingAnimation())

    @classmethod
    def ended(cls):
        """
        """
        cls.running = False
        LspRuntimeMonitor.clockEnd = perf_counter()


    @classmethod
    def output(cls, output):
        """
        """
        cls.outputString += output

        if cls.verbose:
            print(output)

    
    @classmethod
    def saveOutput(cls):
        """
        """
        f = open(cls.outputFilePath, "w")
        f.write(cls.outputString)
        f.close()

    @classmethod
    def report(cls):
        """
        """
        # Duration
        durationStatement = cls.duration()
        cls.output(durationStatement)

        # Saving all generated output to a default file
        cls.saveOutput()

        cls.plotData()


    @classmethod
    def plotData(cls):
        """
        """

        # Plots
        # Plotting the evolution of the minimal cost over generations
        plt.plot(list(range(len(cls.popStatistics["max"]))), cls.popStatistics["max"])
        plt.ylabel("Population maximal cost")
        plt.show()

        # Plotting the evolution of the minimal cost over generations
        plt.plot(list(range(len(cls.popStatistics["min"]))), cls.popStatistics["min"])
        plt.ylabel("Population minimal cost")
        plt.show()

    @classmethod
    def waitingAnimation(cls):
        """
        """

        animation = "|/-\\"
        idx = 0
        # while thing_not_complete():
        while cls.running:
            print(animation[idx % len(animation)], end="\r")
            idx += 1
            time.sleep(0.1)