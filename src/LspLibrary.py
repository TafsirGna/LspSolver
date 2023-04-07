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


fieldnames = ['dna', 'index', 'target', 'changeover_costs', 'stocking_costs', 'deadlines', 'cost', 'result_cost', "instance_file_root_name"]




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
    
    file = "data/ML/dataset0.csv"

    if not os.path.isfile(file):
        with open(file, "w") as csv_file:
            # print headers
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

    with open(file, mode='a') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        for datum in mlData:
            writer.writerow({fieldnames[0]: datum[0], fieldnames[1]: datum[1], fieldnames[2]: datum[2], fieldnames[3]: datum[3], fieldnames[4]: datum[4], fieldnames[5]: datum[5], fieldnames[6]: datum[6], fieldnames[7]: datum[7]})



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



#### ML Code

def readDNA(preProcRow, data):
	"""
	"""

	data = data.replace("(", "")
	data = data.replace(")", "")
	data = data.split(", ")

	for datum in data:
		preProcRow.append(int(datum))

	return preProcRow

def readStockingCosts(preProcRow, data):
	"""
	"""

	data = data.replace("[", "")
	data = data.replace("]", "")
	data = data.split(" ")

	# index = 0
	for datum in data:
		if len(datum) > 0:
			preProcRow.append(int(datum))
			# index += 1
	# print(index)

	return preProcRow

def readChangeOverCosts(preProcRow, data):
	"""
	"""

	data = data.replace("[", "")
	data = data.replace("]", "")
	data = data.split("\n")

	# index = 0
	for line in data:
		numbers = line.split(" ")
		for number in numbers:
			if len(number) > 0:
				preProcRow.append(int(number))
				# index += 1
	# print(index)

	return preProcRow

def readDeadlines(preProcRow, data):
	"""
	"""

	return readChangeOverCosts(preProcRow, data)


def extractMLFeatures(row):
    """
    """

    preProcRow = []
    # preProcRow.append(row[8])
    dna = readDNA(list(preProcRow), row[0])

    row1, row2 = int(row[1]), int(row[2])

    if row1 == row2 - 1:
        if row1 > 0:
            preProcRow.append(int(dna[row1 - 1]))
        else:
            preProcRow.append(0)
        preProcRow.append(int(dna[row1]))

        preProcRow.append(int(dna[row2]))
        if int(row[2]) < (len(dna) - 1):
            preProcRow.append(int(dna[row2 + 1]))
        else:
            preProcRow.append(0)
    elif row2 == row1 - 1:
        if row2 > 0:
            preProcRow.append(int(dna[row2 - 1]))
        else:
            preProcRow.append(0)
        preProcRow.append(int(dna[row2]))

        preProcRow.append(int(dna[row1]))
        if row1 < (len(dna) - 1):
            preProcRow.append(int(dna[row1 + 1]))
        else:
            preProcRow.append(0)
    else:
        for i in [1, 2]:
            if int(row[i]) > 0:
                preProcRow.append(int(dna[int(row[i]) - 1]))
            else:
                preProcRow.append(0)

            if int(row[i]) < (len(dna) - 1):
                preProcRow.append(int(dna[int(row[i]) + 1]))
            else:
                preProcRow.append(0)


    preProcRow.append(int(dna[row1]))
    preProcRow.append(int(dna[row2]))

    preProcRow.append(row1)
    preProcRow.append(row2)

    changeOverCosts = readChangeOverCosts(list(preProcRow), row[3])


    # readStockingCosts(preProcRow, row[4])
    deadlines = readDeadlines(list(preProcRow), row[5])
    preProcRow.append(deadlines[int(dna[row1]) - 1])
    preProcRow.append(deadlines[int(dna[row2]) - 1])

    dist = abs(row2 - row1)
    dist = 1 if dist == 1 else 0
    preProcRow.append(dist)

    preProcRow.append(row[7] > row[6])

    return preProcRow