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

# # I create an instance of the genetic algorithm to be used
lspSolver = GeneticAlgorithm()

#
LspRuntimeMonitor.started()
###

lspSolver.solve()

###
LspRuntimeMonitor.ended()
##

# Reporting all statistics collected when running the selected algo
LspRuntimeMonitor.report()