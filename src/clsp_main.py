#!/usr/bin/python
# -*-coding: utf-8 -*

#--- importation of the modules

from clsp_ga import *
from clsp_ga_library import *
import sys

#---	Start 

# I retrieve the content of the file into an object of Instance class
filename = sys.argv[1]
instance = readFile(filename)

print("-------	Step 0 : Instance of Pigment Sequencing Problem to be used	-------")

print(instance)

startTime = time.clock()

print("-------	Step 1 : Initialization of the population	-------")

#print("Number of the population is : ", len(genAlgo.population))
#print(" 1 - Initialization of the population  ")

# I create an instance of the genetic algorithm to be used
genAlgo = GeneticAlgorithm(instance)
#c = [2, 1, 0, 1, 2]
c = [1, 3, 2, 1, 0, 0, 2, 0]

print("-------	Step 2 : Processing the genetic algorithm	--------")

genAlgo.initPopulation()
genAlgo.process()
#print("Feasible : ", genAlgo.makeItFeasible(c))
#print("Feasible : ", genAlgo.isFeasible(c))
#print("Feasible : ", 1.0/genAlgo.getChromosomeFitness(c))

endTime = time.clock()

print("-------	Step 3 : Statistics	-------")
print("time : " + str((endTime - startTime)) + " second(s)")
#genAlgo.printResults()

#print(int(str(bin(8))[2:]))
