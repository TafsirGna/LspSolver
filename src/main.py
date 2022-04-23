#!/usr/bin/python3.5
# -*-coding: utf-8 -*

# import sys
import argparse
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.GAOperators.MutationOperator import MutationOperator
from LspAlgorithms.GeneticAlgorithms.GAOperators.CrossOverOperator import CrossOverOperator 
from LspAlgorithms.GeneticAlgorithms.Hcm.Solver import GeneticAlgorithm
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Population import Population
from LspInputDataReading.LspInputDataInstance import InputDataInstance
from LspInputDataReading.LspInputDataReader import InputDataReader
from LspRuntimeMonitor import LspRuntimeMonitor
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
LspRuntimeMonitor.verbose = args.verbose
inputDataReader = InputDataReader()
inputDataInstance = inputDataReader.readInput(inputFile)

###
ParameterData.instance = ParameterData()

# print(Chromosome.feasible([1, 2, 0, 1, 2], InputDataInstance.instance))
# [2, 2, 2, 3, 1, 0, 0, 1]

# c = Chromosome.createFromRawDNA([2, 1, 0, 1, 2])
# # c = Chromosome.createFromRawDNA([2, 2, 2, 3, 1, 0, 0, 1])
# # [3, 2, 2, 2, 1, 1, 0, 0]
# # [2, 2, 2, 3, 1, 0, 0, 1]
# print("Chromosome ", c)
# # # [2, 1, 2, 0, 1]
# print("1 -- ", (MutationOperator()).process(c, strategy="advanced"))

# print(Chromosome.localSearch([2, 3, 2, 2, 0, 1, 0, 1], InputDataInstance.instance))
# print(Chromosome.localSearch([2, 3, 2, 2, 0, 1, 0, 1], InputDataInstance.instance))

# cA, cB = Chromosome.createFromRawDNA([2, 1, 0, 2, 1]), Chromosome.createFromRawDNA([2, 1, 2, 0, 1])
# cA, cB = Chromosome.createFromRawDNA([1, 2, 2, 2, 1, 3, 0, 0]), Chromosome.createFromRawDNA([2, 2, 2, 3, 1, 1, 0, 0])
# print(cA, "\n", cB, "\n -----------------------------")
# print((CrossOverOperator([cA, cB])).process())

# # I create an instance of the genetic algorithm to be used
lspSolver = GeneticAlgorithm(inputDataInstance)

#
LspRuntimeMonitor.started()
###

lspSolver.solve()

###
LspRuntimeMonitor.ended()
##

# Reporting all statistics collected when running the selected algo
LspRuntimeMonitor.report()