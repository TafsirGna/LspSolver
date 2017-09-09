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

#---	Start 

# I store the content of the file into an object of Instance class
filename = sys.argv[1]
instance = readFile(filename)

print("-------	Instance of Pigment Sequencing Problem to be used	-------")

print(instance)

# I create an instance of the genetic algorithm to be used
genAlgo = GeneticAlgorithm(instance)

print("-------	Performing the genetic algorithm	--------")

# i store the time when the solving began
startTime = time.clock()

'''
c = Chromosome()
#c.init2([2,1,0,2,1], [1,1,0,2,2])
#c.init2([0,2,2,2,0,1,3,1], [0,1,2,3,0,1,1,2])
#c.init1([5, 2, 9, 4, 2, 9, 6, 10, 10, 4, 7, 1, 8, 3, 10, 10, 10, 8, 8, 8, 5, 2, 4, 4, 9, 9, 9, 9, 9, 9, 2, 7, 3, 6, 1, 8, 5, 2, 8, 10, 10, 4, 4, 7, 1, 1, 8, 8, 8, 3, 3, 3, 6, 6, 6, 6, 5, 10, 4, 7, 7, 7, 3, 3, 6, 2, 8, 8, 10, 10, 10, 10, 10, 10, 10, 10, 8, 6, 6, 6, 6, 2, 2, 5, 5, 5, 5, 2, 2, 2, 2, 7, 7, 1, 1, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 6, 10, 4, 7, 1, 1, 1, 1, 1, 1, 1, 1, 6, 2, 8, 10, 10, 4, 4, 4, 7, 7, 7, 7, 3, 6, 2, 5, 6, 6, 6, 6, 6, 2, 8, 5, 5, 2, 2, 7, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 7, 7, 1, 8, 5, 6, 6, 6, 5, 0, 8, 7, 7, 4, 4, 4, 0, 0, 0, 0, 0, 5, 5, 5, 2, 2, 2, 2, 2, 8, 0, 10, 10, 10, 0, 7, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7, 7, 7, 7, 7, 0, 5, 0, 0, 0, 8, 0, 0, 2, 2, 8, 0, 0, 4, 0, 0, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 2, 5, 5, 5, 0, 0, 8, 0, 0, 0, 0, 0, 4, 4, 0, 0, 2, 2, 2, 2, 8, 8, 0, 0, 0, 0, 0, 0, 7, 7, 7, 7, 0, 5, 5, 0, 0, 0, 8, 0, 0, 0, 0, 4, 4, 4, 4, 0, 0, 0, 0, 0, 5, 2, 2, 8, 0, 10, 0, 10, 0, 6, 6, 6, 6, 6, 6, 0, 3, 4, 4, 0, 0, 5, 2, 2, 2, 2, 8, 0, 0, 0, 0, 5, 5, 0, 7, 3, 0, 5, 0, 3, 3, 3, 0, 0, 4, 0, 2, 2, 5, 0, 8, 0, 4, 0, 0, 0, 8, 3, 0, 0, 0, 7, 0, 0, 5, 5, 0, 4, 0, 8, 0, 0, 0, 0, 4, 0, 0, 3])
c.init1([3, 6, 7, 10, 5, 3, 8, 3, 6, 4, 9, 5, 1, 7, 7, 10, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 6, 5, 1, 1, 1, 1, 1, 1, 10, 6, 5, 3, 3, 6, 6, 4, 4, 4, 10, 10, 2, 7, 7, 9, 9, 2, 2, 2, 2, 3, 3, 5, 5, 5, 5, 10, 6, 6, 6, 6, 6, 6, 4, 4, 4, 4, 4, 9, 9, 9, 9, 9, 2, 2, 7, 0, 0, 7, 10, 0, 0, 10, 0, 2, 2, 2, 7, 0, 10, 10, 10, 0, 3, 3, 3, 5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 4, 0, 10, 0, 10, 0, 4, 0, 5, 10, 0, 6, 6, 6, 5, 5, 0, 10, 0, 5, 0, 0, 2, 7, 0, 0, 3, 6, 6, 0, 0, 4, 0, 0, 9, 9, 9, 9, 2, 2, 2, 3, 5, 0, 7, 4, 4, 0, 0, 6, 6, 5, 0, 8, 7, 7, 0, 0, 0, 0, 0, 0, 2, 2, 3, 3, 5, 0, 1, 0, 4, 10, 0, 6, 6, 10, 0, 8, 2, 0, 10, 0, 4, 1, 0])
print(c)
#
c.advmutate()
print(c, c.isFeasible())
'''

#print(Node.evaluate([2,1,0,2,1]))
genAlgo.start()

# i store the time when the solving ended
endTime = time.clock()

print(" ")
print("-------	Statistics	-------")
print("time : " + str((endTime - startTime)) + " second(s)")

#---	End