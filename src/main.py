#!/usr/bin/python3.5
# -*-coding: utf-8 -*

# importing modules
# import sys
import argparse
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome 
from LspAlgorithms.GeneticAlgorithms.Hcm.Solver import GeneticAlgorithm
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Population import Population
from LspInputDataReading.LspInputDataInstance import InputDataInstance
from LspInputDataReading.LspInputDataReader import InputDataReader
from LspStatistics.LspRuntimeStatisticsMonitor import LspRuntimeStatisticsMonitor
from ParameterSearch.ParameterData import ParameterData
from time import perf_counter


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

# print(Chromosome.feasible([1, 2, 0, 1, 2], InputDataInstance.instance))
# [2, 2, 2, 3, 1, 0, 0, 1]

# c = Chromosome()
# # c.dnaArray = Chromosome.convertRawDNA([2, 1, 2, 1, 0])
# c.dnaArray = Chromosome.convertRawDNA([2, 1, 2, 0, 2, 1, 3, 0])
# # print(Chromosome.sliceDna(c.dnaArray, 2 , 7))
# # [3, 2, 2, 2, 1, 1, 0, 0]
# c.calculateCost()
# print("cost ((((((((", c.cost)
# # # [2, 1, 2, 0, 1]
# c.mutate()
# print(c)

# print(Chromosome.localSearch([2, 3, 2, 2, 0, 1, 0, 1], InputDataInstance.instance))
# print(Chromosome.localSearch([2, 3, 2, 2, 0, 1, 0, 1], InputDataInstance.instance))

# dnaA, dnaB = Chromosome.convertRawDNA([2, 1, 0, 2, 1]), Chromosome.convertRawDNA([2, 1, 2, 0, 1])
# # dnaA, dnaB = Chromosome.convertRawDNA([1, 2, 2, 1, 3, 2, 0, 0]), Chromosome.convertRawDNA([2, 2, 3, 1, 1, 2, 0, 0] )
# cA, cB = Chromosome(), Chromosome()
# cA.dnaArray, cB.dnaArray  = dnaA, dnaB
# cA.calculateCost(), cB.calculateCost()
# print(cA, "\n", cB, "\n -----------------------------")
# print(Population.crossOverChromosomes(cA, cB))

###
LspRuntimeStatisticsMonitor.instance = LspRuntimeStatisticsMonitor()

# # I create an instance of the genetic algorithm to be used
lspSolver = GeneticAlgorithm(inputDataInstance)

##
if LspRuntimeStatisticsMonitor.instance:
    LspRuntimeStatisticsMonitor.instance.popInitClockStart = perf_counter()
###

lspSolver.solve()

###
if LspRuntimeStatisticsMonitor.instance:
    LspRuntimeStatisticsMonitor.instance.popInitClockEnd = perf_counter()
###

# # Reporting all statistics collected when running the selected algo
LspRuntimeStatisticsMonitor.instance.report()