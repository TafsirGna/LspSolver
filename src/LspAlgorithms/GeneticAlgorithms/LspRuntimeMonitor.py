#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from collections import defaultdict
from threading import Thread
from time import perf_counter, time
from LspLibrary import bcolors
import time
import matplotlib.pyplot as plt
from datetime import datetime
import os


class LspRuntimeMonitor:
    """
    """

    fileName = "Not available"
    verbose = False
    outputFolderPath = "data/output/"

    instance = None

    def __init__(self) -> None:
        """
        """
        
        self.clockStart = None
        self.clockEnd = None
        self.popsData = defaultdict(lambda: {"min": [], "max": [], "mean": [], "std": []})
        self.outputString = ""
        self.timeLength = 0
        self.newInstanceAdded = None
        self.remainingMutations = None

        self.start()


    def duration(self):
        """
        """
        return  f"{self.timeLength} second(s)"


    def start(self):
        """
        """

        self.clockStart = perf_counter()

        print(f"{bcolors.OKGREEN}Processing input data.{bcolors.ENDC}")
        # Thread(cls.waitingAnimation())


    def stop(self):
        """
        """

        self.clockEnd = perf_counter()
        self.timeLength = self.clockEnd - self.clockStart


    def output(self, output):
        """
        """
        self.outputString += output

        if self.verbose:
            print(output)

    
    def saveOutput(self):
        """
        """

        if not os.path.exists(LspRuntimeMonitor.outputFolderPath):
            os.makedirs(LspRuntimeMonitor.outputFolderPath)

        now = datetime.now()
        f = open(LspRuntimeMonitor.outputFolderPath+"/"+str(datetime.timestamp(now))+".txt", "w")
        f.write(self.outputString)
        f.close()


    def report(self):
        """
        """
        # Duration
        durationStatement = self.duration()
        self.output(durationStatement)

        # Saving all generated output to a default file
        self.saveOutput()

        self.plotData()


    def plotData(self):
        """
        """

        print('-----------------------------------------')
        print(f"{bcolors.OKGREEN}Created : {bcolors.ENDC}", LspRuntimeMonitor.outputFolderPath)
        print('-----------------------------------------')
        print(self.popsData)

        data = list(self.popsData.values())[0]

        # Plots
        # Plotting the evolution of the minimal cost over generations
        plt.plot(list(range(len(data["min"]))), data["min"])
        plt.ylabel("Population minimal cost")
        plt.show()
        

    # @classmethod
    # def waitingAnimation(cls):
    #     """
    #     """

    #     animation = "|/-\\"
    #     idx = 0
    #     # while thing_not_complete():
    #     while cls.running:
    #         print(animation[idx % len(animation)], end="\r")
    #         idx += 1
    #         time.sleep(0.1)