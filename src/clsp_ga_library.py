#!/usr/bin/python
# -*-coding: utf-8 -*

import math
from itertools import *
from random import *

#--------------------
# file : clsp_ga_library
# author : Tafsir GNA
# purpose : Containing all the functions or objects needed in the algorithm implementation process
#--------------------

#---	First part:  The functions

def getItemsRanks(chromosome, counters):

	ranks = []

	i = 0 
	while i < len(chromosome):
		if chromosome[i] != 0:

			item = chromosome[i]
			counter = counters[item-1]
			ranks.append(counter)

			# then, i increment the counter of this item
			del counters[item-1]
			counters.insert(item-1,(counter+1))

		else:
			ranks.append(0)
		i+=1

	return ranks

def getMax(n1,n2):
	if n1 > n2 :
		return n1
	else:
		return n2

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

#def readFile():
#	pass

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

class Chromosome:

	mutationRate = 0
	problem = 0

	# Builder 
	def __init__(self, solution):
		self.solution = list(solution)
		self._valueFitness = 0 
		self.manufactGrid = []
		pass

	def __repr__(self):
		return " Solution : {}, valueFitness : {}".format(self.solution,self._valueFitness)

	def __eq__(self, chromosome):
		return self.solution == chromosome.solution

	def getFeasible(self):

		if self.isFeasible() is False:
			#print("F Start : ", chromosome)
			# i make sure that the number of goods producted isn't superior to the number expected
			i = 0
			while i < Chromosome.problem.nbItems:

				itemDemandPeriods = getDemandPeriods(Chromosome.problem.demandsGrid[i])

				j = 0
				nb = 0
				while j <= itemDemandPeriods[len(itemDemandPeriods)-1]:

					if self.solution[j] == i+1 :

						nb += 1
						if nb > len(itemDemandPeriods):

							del self.solution[j]
							self.solution.insert(j,0)

						else:
							if j > itemDemandPeriods[nb-1]:
								del self.solution[j]
								self.solution.insert(j,0)

					j+=1

				i+=1

			#print(chromosome)
			
			# i make sure that the number of items producted isn't inferior to the number expected
			i = 0
			while i < Chromosome.problem.nbItems:

				itemDemandPeriods =  getDemandPeriods(Chromosome.problem.demandsGrid[i])

				#print("item : ", i+1)

				nb = 0
				j = 0
				while nb < len(itemDemandPeriods) and j < len(self.solution):

					contain = False
					zeroperiods = []
					#print(" item nb : ", itemDemandPeriods[nb], " , ", nb)
					while j <= itemDemandPeriods[nb]:

						if self.solution[j] == 0:
							zeroperiods.append(j)

						if self.solution[j] == i+1 :
							#print("Yes : ", j)
							nb += 1	
							contain = True
							j += 1
							break

						j += 1

					#print("nb : ", nb, " j : ", j, " bool : ", contain, " zeroperiods : ", zeroperiods)

					if contain is False:
						if len(zeroperiods) > 0:
							del self.solution[zeroperiods[0]]
							self.solution.insert(zeroperiods[0], i+1)
							nb += 1
							j = zeroperiods[0]+1

				#print("Inter : ", chromosome)

				i+=1
	
	
	def isFeasible(self):

		# i check first that there's not shortage or backlogging
		i = 0
		feasible = False
		while i < Chromosome.problem.nbItems:

			demandProductPeriods = getDemandPeriods(Chromosome.problem.demandsGrid[i])

			manufactProductPeriods = getManufactPeriods(self.solution,i+1)

			if (len(manufactProductPeriods) != len(demandProductPeriods)):
				return False
			else:
				j = 0
				while j < len(manufactProductPeriods):

					if (manufactProductPeriods[j] > demandProductPeriods[j]):
						return False

					j+=1

				feasible = True

			i+=1

		if (feasible is True):
			return True
		return False

	#--------------------
	# function : mutate
	# Class : Chromosome
	# purpose : Applying mutation to a given chromosome and returning the resulting one
	#--------------------

	def mutate(self):

		#print("M Start : ", chromosome)

		if (randint(0,100) < (Chromosome.mutationRate*100)):

			mutated = False
			# i make sure that the returned chromosome's been actually mutated
			while mutated is False:

				randomIndice = randint(0,(len(self.solution)-1))
				item1 = self.solution[randomIndice]

				# i make sure that the randomIndice variable never corresponds to a zero indice
				while item1 == 0:
					randomIndice = randint(0,(len(self.solution)-1))
					# i get the item corresponding the gene to be flipped
					item1 = self.solution[randomIndice]

				item1DemandPeriods = getDemandPeriods(Chromosome.problem.demandsGrid[item1-1])

				i = 0
				nbItem1 = 0
				while i <= randomIndice:
					if self.solution[i] == item1:
						nbItem1 += 1
					i+=1

				deadlineItem1 = item1DemandPeriods[nbItem1-1]

				# i make sure that the second item chosen to replace the first one won't be the same with the item 1.
				item2 = randint(1, Chromosome.problem.nbItems)
				while item2 == item1:
					item2 = randint(1, Chromosome.problem.nbItems)

				item2ManufactPeriods = getManufactPeriods(self.solution, item2)

				item2DemandPeriods = getDemandPeriods(Chromosome.problem.demandsGrid[item2-1])

				#print(" item1 : ", item1, " item2 : ", item2, " randomIndice : ", randomIndice)
				#print(item2DemandPeriods)
				i = 0
				while i < len(item2DemandPeriods):
					if item2DemandPeriods[i] >= randomIndice and deadlineItem1 > item2ManufactPeriods[i]:
						self.solution = switchGenes(self.solution, randomIndice, item2ManufactPeriods[i])
						mutated = True
						break
					i += 1


	def _get_valueFitness(self):

		if self._valueFitness == 0:
			grid = Chromosome.problem.chanOverGrid
			#print(chromosome)

			# Calculation of all the change-over costs
			
			i = 1
			tmp = self.solution[0]
			while i < len(self.solution) :

				n = self.solution[i]

				if (tmp == 0):
					i+=1
					tmp = n
				else:
					
					if (n != 0):
						if (n != tmp):
							self._valueFitness += int((grid[tmp-1])[n-1])
							tmp = n
					else:
						tmp = self.solution[i-1]

						j=i
						while j < len(self.solution) and self.solution[j] == 0:
							j+=1
						i=j-1
					
					i+=1

			# Calculation of the sum of holding costs

			i=0
			while i < Chromosome.problem.nbItems:

				itemDemands = Chromosome.problem.demandsGrid[i]

				itemDemandPeriods = getDemandPeriods(itemDemands)

				itemManufactPeriods = getManufactPeriods(self.solution, i+1)

				j = 0
				while j < len(itemDemandPeriods):
					self._valueFitness += int(Chromosome.problem.holdingGrid[i])*(itemDemandPeriods[j]-itemManufactPeriods[j])
					j+=1

				i+=1


		return self._valueFitness

	def _set_valueFitness(self, valueFitness):
		self._valueFitness = valueFitness

	# Definition of the properties
	valueFitness = property(_get_valueFitness,_set_valueFitness)


'''
class Population(object):
	"""docstring for Population"""
	def __init__(self, arg):
		super(Population, self).__init__()
		self.arg = arg
'''
		
