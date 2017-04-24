#!/usr/bin/python3.5
# -*-coding: utf-8 -*

# TODO 
# - give some updates to the implementation of the insertion of the new population into the the former one (test elistism)
# - implement a dynamic values for the parameters depending on the evolution of the algorithm over time
# - another one approach is to take into account the cost of each item to privilegiate a way of implementation of genetic operators 

#--- importation of the modules

from clsp_ga import *
import sys
import time

#---	Start 

# I store the content of the file into an object of Instance class
filename = sys.argv[1]
instance = readFile(filename)

print("-------	Step 0 : Instance of Pigment Sequencing Problem to be used	-------")

print(instance)

# i store the time of the beginning of the process
startTime = time.clock()

print("-------	Step 1 : Initialization of the population	-------")

#print("Number of the population is : ", len(genAlgo.population))
#print(" 1 - Initialization of the population  ")

# I create an instance of the genetic algorithm to be used
genAlgo = GeneticAlgorithm(instance)

print("-------	Step 2 : Processing the genetic algorithm	--------")

genAlgo.initPopulation()

print(genAlgo.population)

genAlgo.process()

endTime = time.clock()

print("-------	Step 3 : Statistics	-------")
print("time : " + str((endTime - startTime)) + " second(s)")
genAlgo.printResults()

#---	End