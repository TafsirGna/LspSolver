#!/usr/bin/python
# -*-coding: utf-8 -*

import math
from itertools import *

#--------------------
# file : clsp_ga_library
# author : Tafsir GNA
# purpose : Containing all the functions or objects needed in the algorithm implementation process
#--------------------

#---	First part:  The functions


def switchGenes(chromosome,indice_gene1,indice_gene2):
	c = list(chromosome)

	del c[indice_gene1]
	c.insert(indice_gene1, chromosome[indice_gene2])

	del c[indice_gene2]
	c.insert(indice_gene2, chromosome[indice_gene1])

	return c

def getManufactPeriods(chromosome,item):

	itemManufactPeriods = []

	j = 0
	while j < len(chromosome):

		if (int(chromosome[j],2) == item):
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
	while i<len(demand):
		if int(demand[i]) == 1:
			result.append(i)
		i+=1 
	return result

#--------------------
# function : getGeneBits
# author : Tafsir GNA
# purpose : allowing to determine the number of bits on which a gene can be represented 
#--------------------

def getGeneBits(number):
	i = 0
	while math.pow(2,i) < number :
		i+=1
	return i

#--------------------
# function : readFile
# author : Tafsir GNA
# purpose : Reading the given file in order to extract input data
#-------------------- 

def readFile(filename):
	''' Input data's initialization '''
	nbItems = 0
	nbTimes = 0
	demandsGrid = []
	holdingGrid = []
	chanOverGrid = []
	i = 0

	formatGood = True

	''' Opening and reading of the file '''
	with open(filename, 'rt') as instance:
		for line in instance:
			data = []
			data = line.split(" ")

			# I read the first line to retrieve the first inputs
			if i==1 :
				if len(data) != 2:
					formatGood = False
					break
				else:
					nbItems=int(data[0])
					nbTimes=int(data[1])

			# Once, the nbItems and nbTimes have been retrieved, i read the following lines 
			if i>2 and i<=nbItems+2:
				if len(data) != nbTimes:
					formatGood = False
					break
				else:
					demandsGrid.append(data)

			if i==(nbItems+4):
				if len(data) != nbItems:
					formatGood = False
					print("phrack")
					break
				else:
					holdingGrid = data
			
			if i>=nbItems+6 and i <= (2*nbItems)+6 :
				if len(data) != nbItems:
					formatGood = False
					break
				else:
					chanOverGrid.append(data)
			
			i+=1

		inst = 0
		if formatGood is False:
			print("Bad instance format")
		else:
			#print("instance read")
			inst = Instance(nbItems,nbTimes,demandsGrid,holdingGrid,chanOverGrid)
			#print(inst)
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

	#	implementation of the function called when an object is printed to the screen
	def __repr__(self):
		return "Number of Items is : {} \n".format(self.nbItems) + \
		"Number of Times is : {} \n".format(self.nbTimes) + \
		"Demands for each item are : {} \n".format(self.demandsGrid) + \
		"Holding costs for each item are : {} \n".format(self.holdingGrid) + \
		"Changeover costs from one item to another one are : {} \n".format(self.chanOverGrid)
