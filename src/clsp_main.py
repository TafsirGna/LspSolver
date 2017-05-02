#!/usr/bin/python3.5
# -*-coding: utf-8 -*

# TODO 
# - give some updates to the implementation of the insertion of the new population into the the former one (test elistism)
# - implement a dynamic values for the parameters depending on the evolution of the algorithm over time
# - another one approach is to take into account the cost of each item to privilegiate a way of implementation of genetic operators 
# - another good clue is to put all the parameters value in a file and pass it as a parameter to the program via this file
# - after a given number of generations without a significative enhancement of the solutions yet found, the thread stops
# - try another way to initialize the population

#--- importation of the modules

from clsp_ga import *
import sys
import time

#---	Start 

# I store the content of the file into an object of Instance class
filename = sys.argv[1]
instance = readFile(filename)

print("-------	Instance of Pigment Sequencing Problem to be used	-------")

print(instance)

# i store the time when the solving began
startTime = time.clock()

# I create an instance of the genetic algorithm to be used
genAlgo = GeneticAlgorithm(instance)

print("-------	Performing the genetic algorithm	--------")

genAlgo.start()

# i store the time when the solving ended
endTime = time.clock()

print(" ")
print("-------	Statistics	-------")
print("time : " + str((endTime - startTime)) + " second(s)")

#---	End