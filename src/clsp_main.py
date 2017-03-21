#!/usr/bin/python
# -*-coding: utf-8 -*

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
c1 = [2, 1, 0, 1, 2]
c2 = [2, 1, 2, 0, 1]

#c = [3, 2, 1, 3, 0, 1, 2, 1]
c = [1, 1, 2, 2, 2, 0, 3, 0]

print("-------	Step 2 : Processing the genetic algorithm	--------")

genAlgo.initPopulation()
genAlgo.process()
#print(genAlgo.population.getCostof(1,1,1,c2))
#genAlgo.population.applyCrossOverto(Chromosome(c1) ,Chromosome(c2))

endTime = time.clock()

print("-------	Step 3 : Statistics	-------")
print("time : " + str((endTime - startTime)) + " second(s)")
genAlgo.printResults()

#---	End