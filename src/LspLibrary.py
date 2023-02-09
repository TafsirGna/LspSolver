#!/usr/bin/python3.5
# -*-coding: utf-8 -*

import math
from itertools import *
import os
import datetime
import numpy as np
import csv
# import pandas as pd

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

# def printRow(fileStream):
#     """
#     """
    
#     fileStream.write("-"*140+"\n")


def printMLData(mlData):
    """
    """
    fieldnames = ['dna', 'index', 'target', 'changeover_costs', 'stocking_costs', 'deadlines', 'cost', 'result_cost']
    
    file = "data/ML/dataset.csv"

    if not os.path.isfile(file):
        with open(file, "w") as csv_file:
            # print headers
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

    with open(file, mode='a') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        for datum in mlData:
            writer.writerow({'dna': datum[0], 'index': datum[1], 'target': datum[2], 'changeover_costs': datum[3], 'stocking_costs': datum[4], 'deadlines': datum[5], 'cost': datum[6], 'result_cost': datum[7]})



def printGlobalResults(file, globalData):
    """
    """

    fieldnames = ['Best result', 'Worst result', 'best results mean', 'min time lengths', 'max time lengths', 'time lengths mean', 'When']

    if not os.path.isfile(file):
        with open(file, "w") as csv_file:
            # print headers
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

    with open(file, mode='a') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writerow({'Best result': min(globalData["mins"]), 'Worst result': max(globalData["mins"]), 'best results mean': np.mean(globalData["mins"]), 'min time lengths': min(globalData["timeLengths"]), 'max time lengths': max(globalData["timeLengths"]), 'time lengths mean': np.mean(globalData["timeLengths"]), 'When': datetime.datetime.now()})


    # width = 20
    # headers = ("|Best result", "|Worst result", "|best results mean",
    #            "|min time lengths", "|max time lengths", "|time lengths mean", "|When")

    # if not os.path.isfile(file):
    #     with open(file, "a") as f:
    #         printRow(f)
    #         # print headers
    #         f.write(("{:{widths[0]}} {:{widths[0]}} {:{widths[0]}} {:{widths[0]}} {:{widths[0]}} {:{widths[0]}} {:{widths[0]}}\n").format(*headers, widths=([width]*len(headers))))
    #         printRow(f)

    # with open(file, "a") as f:
    #     values = (min(globalData["mins"]), max(globalData["mins"]), "{:.2f}".format((np.mean(globalData["mins"]))),
    #              "{:.2f}".format(min(globalData["timeLengths"])), "{:.2f}".format(max(globalData["timeLengths"])), "{:.2f}".format(np.mean(globalData["timeLengths"])), datetime.datetime.now())
    #     f.write(("{:{widths[0]}} {:{widths[0]}} {:{widths[0]}} {:{widths[0]}} {:{widths[0]}} {:{widths[0]}} {:{widths[0]}}\n").format(*values, widths=([width]*len(headers))))
