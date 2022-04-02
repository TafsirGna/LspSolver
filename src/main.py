#!/usr/bin/python3.5
# -*-coding: utf-8 -*

# importing modules
# import sys
import argparse
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome 
from LspAlgorithms.GeneticAlgorithms.Hcm.Solver import GeneticAlgorithm
from LspInputDataReading.LspInputDataReader import InputDataReader
from LspStatistics.LspRuntimeStatisticsMonitor import LspRuntimeStatisticsMonitor
from ParameterSearch.ParameterData import ParameterData

# Setting solver's options 
parser = argparse.ArgumentParser(description = "LspSolver : Lot sizing problems solver tool implementing different AI methods" )
parser.add_argument("file", help = "Instance of lot sizing problem described as a plain text")
parser.add_argument("-v", "--verbose", help = "Display on the screen the details of search process", action = "store_true")
parser.add_argument("-o", "--output", help = "Redirect the output of the program to a given file")
parser.add_argument("-n", "--nbThreads", help = "Number of the threads involved in the search", type = int)
parser.add_argument("-s", "--stats", help = "Display on the screen the stats gathered when applying the algo")

args = parser.parse_args()

# Reading the file to get the problem to solve
inputFile = args.file  #sys.argv[1]
inputDataReader = InputDataReader()
inputDataInstance = inputDataReader.readInput(inputFile)

###
ParameterData.instance = ParameterData()

# print(Chromosome.feasible([1, 2, 0, 1, 2]))

# c = Chromosome([2, 1, 0, 1, 2])
# c.zipDnaArray()
# c.mutate("maximal")
# print(c)

###
LspRuntimeStatisticsMonitor.instance = LspRuntimeStatisticsMonitor()

# I create an instance of the genetic algorithm to be used
lspSolver = GeneticAlgorithm(inputDataInstance)

# i store the time when the solving began
# startTime = time.clock()

lspSolver.solve()

LspRuntimeStatisticsMonitor.instance.report()