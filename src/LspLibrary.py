#!/usr/bin/python3.5
# -*-coding: utf-8 -*

import math
from itertools import *
import os
import datetime
import numpy as np

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'







###
# Print Global Results
###

def printRow(fileStream):
    """
    """
    
    fileStream.write("-"*140+"\n")


def printGlobalResults(file, globalData):
    """
    """

    width = 20
    headers = ("|Best result", "|Worst result", "|best results mean",
               "|min time lengths", "|max time lengths", "|time lengths mean", "|When")

    if not os.path.isfile(file):
        with open(file, "a") as f:
            printRow(f)
            # print headers
            f.write(("{:{widths[0]}} {:{widths[0]}} {:{widths[0]}} {:{widths[0]}} {:{widths[0]}} {:{widths[0]}} {:{widths[0]}}\n").format(*headers, widths=([width]*len(headers))))
            printRow(f)

    with open(file, "a") as f:
        values = (min(globalData["mins"]), max(globalData["mins"]), "{:.2f}".format((np.mean(globalData["mins"]))),
                 "{:.2f}".format(min(globalData["timeLengths"])), "{:.2f}".format(max(globalData["timeLengths"])), "{:.2f}".format(np.mean(globalData["timeLengths"])), datetime.datetime.now())
        f.write(("{:{widths[0]}} {:{widths[0]}} {:{widths[0]}} {:{widths[0]}} {:{widths[0]}} {:{widths[0]}} {:{widths[0]}}\n").format(*values, widths=([width]*len(headers))))
