#!/usr/bin/python3.5
# -*-coding: utf-8 -*

import math
from itertools import *
from random import *
from threading import *
import threading
import copy
import math
import time

#--------------------
# file : clsp_ga_library
# author : Tafsir GNA
# purpose : Containing all the functions or objects needed in the algorithm implementation process
#--------------------

def previousPeriodItemOf(indice, solution):

	if indice > 0:
		if solution[indice-1] != 0:
			return solution[indice-1], indice-1 
		else:
			j = indice-1
			while j >= 0:
				if solution[j] != 0:
					return solution[j], j
				j-=1
			return 0,0
	else:
		# The case where the variable indice corresponds to the first period and then, there's no previous period's item
		return 0,0


def getBestChroms(chromosomes):
	
	chromosome1 = chromosomes[0]

	i = 1
	it = 0
	while i < 4:
		c = chromosomes[i]
		if c.fitnessValue < chromosome1.fitnessValue:
			chromosome1 = c
			it = i
		i+=1

	del chromosomes[it]

	chromosome2 = chromosomes[0]

	i = 1
	while i < 3:
		c = chromosomes[i]
		if c.fitnessValue < chromosome2.fitnessValue:
			chromosome2 = c
		i+=1

	return chromosome1, chromosome2


def getManufactPeriodsGrid(nbItems, deadlineDemandPeriods):

	resultGrid = []
	i = 0
	while i < nbItems:

		tempNb = len(deadlineDemandPeriods[i])
		tempGrid = []
		j = 0
		while j < tempNb:
			tempGrid.append(-1)
			j+=1

		resultGrid.append(tempGrid)

		i+=1 
		
	return resultGrid

def switchGenes(chromosome,indice_gene1,indice_gene2):
	c = list(chromosome)
	c[indice_gene1] = chromosome[indice_gene2]
	c[indice_gene2] = chromosome[indice_gene1]
	return c

def getManufactPeriods(chromosome,item):

	itemManufactPeriods = []

	j = 0
	size_chromosome = len(chromosome)
	while j < size_chromosome:

		if (chromosome[j] == item):
			itemManufactPeriods.append(j)

		j+=1

	return itemManufactPeriods

#--------------------
# function : getDemandPeriods
# author : Tafsir GNA
# purpose : Getting the set of periods where there are demands for a given product
#--------------------

def getDemandPeriods(demand):

	i=0
	result = []
	size_demand = len(demand)
	while i< size_demand:
		if int(demand[i]) == 1:
			result.append(i)
		i+=1 
	return result


def formatOneReading(filename):

	# Input data's initialization 
	nbItems = 0
	nbTimes = 0
	demandsGrid = []
	holdingGrid = []
	chanOverGrid = []

	fileContent = ""
	# Here's the first way of reading that i apply to the input file, if it doesn't work, i'm gonna try a second way of reading using another format
	with open(filename, 'rt') as instance:
		for line in instance:
			fileContent += line

		#print(len(fileContent))
		nb = 1
		i = 0
		while i < len(fileContent):

			character = fileContent[i]
			if character == '=':
				string = ""
				j = i+1
				while fileContent[j] != ';' and j < len(fileContent):
					string += fileContent[j]
					j+=1

				if nb == 1:
					nbTimes = int(string)

				if nb == 2:
					nbItems = int(string)

				if nb == 3:
					demandsGrid = string

				if nb == 4:
					holdingGrid = string

				if nb == 5:
					chanOverGrid = string

				nb += 1

				i = j

			else:

				i+=1

		# The variables (demandGrid, holdingGrid, chanOverGrid) aren't yet in the right format, then, i'll make it right
		# demandGrid

		i = 0
		grid = []
		while i < len(demandsGrid):
			if demandsGrid[i] == '|':
				string = ""
				j = i+1
				while j < len(demandsGrid) and (demandsGrid[j] != '\n' and demandsGrid[j] != '|') :
					string += demandsGrid[j]
					j+=1 

				i = j-1

				tab = string.split(",")
				if len(tab) == nbTimes :
					grid.append(tab)
			else:
				i+=1

		demandsGrid = list(grid)

		# holdingCosts
		i = 0
		while i < len(holdingGrid):
			if holdingGrid[i] == '[':
				string = ""
				j = i+1
				while j < len(holdingGrid) and holdingGrid[j] != ']':
					string += holdingGrid[j]
					j+=1

				holdingGrid = list(string.split(","))

				i = j

			else:
				i+=1

		# chanOverGrid
		i = 0
		grid = []
		while i < len(chanOverGrid):
			if chanOverGrid[i] == '|':
				string = ""
				j = i+1
				while j < len(chanOverGrid) and (chanOverGrid[j] != '\n' and chanOverGrid[j] != '|') :
					string += chanOverGrid[j]
					j+=1 

				i = j-1

				tab = string.split(",")
				if len(tab) == nbItems :
					grid.append(tab)
			else:
				i += 1

		chanOverGrid = list(grid)

		#print(str(nbItems) + ", " + str(nbTimes) + ", " + str(demandsGrid) + ", " + str(holdingGrid) + ", " + str(chanOverGrid))

		if nbItems != 0 and nbTimes != 0 and demandsGrid != [] and holdingGrid != [] and chanOverGrid != []:
			return Instance(nbItems,nbTimes,demandsGrid,holdingGrid,chanOverGrid)
		return 0


def formatTwoReading(filename):

	# Input data's initialization 
	nbItems = 0
	nbTimes = 0
	demandsGrid = []
	holdingGrid = []
	chanOverGrid = []

	with open(filename, 'rt') as instance:

		i = 1
		for line in instance:
			
			if i == 1:
				nbTimes = int(line)

			if i == 2:
				nbItems = int(line)

			if i >= 5 and i < (5 + nbItems):
				data = []
				data = line.split(" ")
				chanOverGrid.append(data)

			if i == (5 + nbItems + 1):
				holdingGrid = line.split(" ")

			if i >= (5 + nbItems + 3) and i < (5 + nbItems*2 + 3):
				data = []
				data = line.split(" ")
				demandsGrid.append(data)

			i += 1

		if nbItems != 0 and nbTimes != 0 and demandsGrid != [] and holdingGrid != [] and chanOverGrid != []:
			return Instance(nbItems,nbTimes,demandsGrid,holdingGrid,chanOverGrid)
		return 0	
	
#--------------------
# function : readFile
# author : Tafsir GNA
# purpose : Reading the given file in order to extract input data
#-------------------- 

def readFile(filename):

	# Opening and reading of the file 
	inst = formatOneReading(filename)

	# i test if the reading has been successfull, if no then, i try again to read it using another format
	if inst == 0:
		inst = formatTwoReading(filename)

	return inst


#---	Second part:	The classes 

#--------------------
# Class : Instance
# author : Tafsir GNA
# purpose : Describing the structure of an instance to the algorithm
#--------------------

class Instance:

	#	Builder	
	def __init__(self, nbItems, nbTimes, demandsGrid, holdingGrid, chanOverGrid):
		self.nbItems = nbItems
		self.nbTimes = nbTimes
		self.demandsGrid = demandsGrid
		self.holdingGrid = holdingGrid
		self.chanOverGrid = chanOverGrid

		# then, i perform a process over the 'demandsGrid' to obtain a grid with all the deadlines corresponding to all the demands of items
		self.deadlineDemandPeriods = []
		i = 0
		while i < nbItems:
			self.deadlineDemandPeriods.append(getDemandPeriods(demandsGrid[i]))
			i+=1

		# Additionnal variables
		#self.manufactItemsPeriods = getManufactPeriodsGrid(nbItems, self.deadlineDemandPeriods)

	#	implementation of the function called when an object is printed to the screen
	def __repr__(self):
		return "Number of Items is : {} \n".format(self.nbItems) + \
		"Number of Times is : {} \n".format(self.nbTimes) + \
		"Demands for each item are : {} \n".format(self.demandsGrid) + \
		"Holding costs for each item are : {} \n".format(self.holdingGrid) + \
		"Changeover costs from one item to another one are : {} \n".format(self.chanOverGrid)