#!/usr/bin/python3.5
# -*-coding: utf-8 -*

import math
from itertools import *
from random import *
import copy
import math
import time

#--------------------
# file : clsp_ga_library
# author : Tafsir GNA
# purpose : Containing all the functions or objects needed in the algorithm implementation process
#--------------------

def getCostTabKey(item):
	return item[3]

def getPrecsTabKey(item):
	return item[1]

def getNextItem(solution, size, indice):
		
		for i in range(indice + 1, size):
			if solution[i] != 0:
				return solution[i], i
		return 0,0

def getPrevItem(solution, indice):
	
	i = indice - 1
	while i >= 0:
		#print("in prev : ", i , solution)
		if solution[i] != 0:
			return solution[i], i
		i -= 1
	return 0,0

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
	c[indice_gene1], c[indice_gene2] = c[indice_gene2], c[indice_gene1]
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


#---	Second part:	The classes 