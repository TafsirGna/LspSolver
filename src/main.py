#!/usr/bin/python3.5
# -*-coding: utf-8 -*

# importing modules
import sys
import argparse 
from modules import *

# Setting solver's options 
parser = argparse.ArgumentParser(description = "LspSolver : Lot sizing problems solver tool implementing different AI methods" )
parser.add_argument("file", help = "Instance of lot sizing problem described as a plain text")
parser.add_argument("-v", "--verbose", help = "Display on the screen the details of search process", action = "store_true")
parser.add_argument("-o", "--output", help = "Redirect the output of the program to a given file")
parser.add_argument("-n", "--nbThreads", help = "Number of the threads involved in the search", type = int)

args = parser.parse_args()

# Reading the file to get the problem to solve
filename = args.file  #sys.argv[1]
instance = readFile(filename)

#print(instance)

# I create an instance of the genetic algorithm to be used
lspsolver = GeneticAlgorithm(instance)

print("-------	Performing the genetic algorithm	--------")

# i store the time when the solving began
startTime = time.clock()

genAlgo.start()

# i store the time when the solving ended
endTime = time.clock()

print(" ")
print("-------	Statistics	-------")
print("time : " + str((endTime - startTime)) + " second(s)")

#---	End