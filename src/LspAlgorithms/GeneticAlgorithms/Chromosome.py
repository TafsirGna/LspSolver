#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from random import randint
import copy
from xmlrpc.client import Boolean
import numpy as np
import random

from LspInputDataReading.LspInputDataInstance import InputDataInstance
# from ...LspLibrary.lspLibrary import *

class Chromosome(object):

	def __init__(self, dnaArray):
		"""
		"""

		self.dnaArray = np.array(dnaArray)
		self.cost = 0 #self.calculateCost(self.dnaArray, InputDataInstance.instance)
		self.dnaArrayZipped = [[] for i in range(0, InputDataInstance.instance.nItems)]


	@classmethod
	def calculateCost(cls, dnaArray, inputDataInstance):
		"""
		"""
		# print(dnaArray)
		cost = 0
		item1, item2 = dnaArray[0], dnaArray[0]
		nOccurenceItem = np.array([0 for _ in range(0, inputDataInstance.instance.nItems)])
		if (item2 != 0):
			nOccurenceItem[item2 - 1] += 1
			cost += inputDataInstance.instance.stockingCostsArray[item2 - 1] * (inputDataInstance.instance.demandsArrayZipped[item2 - 1][nOccurenceItem[item2 - 1] -1] - 0)

		for index in range(1, len(dnaArray)):
			if dnaArray[index] != 0:
				item2 = dnaArray[index]
				cost += inputDataInstance.chanOverArray[item1 - 1 , item2 - 1]
				nOccurenceItem[item2 - 1] += 1
				cost += inputDataInstance.instance.stockingCostsArray[item2 - 1] * (inputDataInstance.instance.demandsArrayZipped[item2 - 1][nOccurenceItem[item2 - 1] - 1] - index)

				item1 = item2
			else: 
				continue

		return cost

	@classmethod
	def feasible(cls, dnaArray) -> Boolean:
		"""Checks if a given dnaArray leads to a feasible chromosome
		"""

		dnaArray = np.array(dnaArray)
		dnaArrayZipped = [[] for i in range(0, InputDataInstance.instance.nItems)]

		for index, item in enumerate(dnaArray):
			if (item != 0):
				dnaArrayZipped[item - 1].append(index)

		for i in range(0, InputDataInstance.instance.nItems):
			demands = InputDataInstance.instance.demandsArrayZipped[i]
			prods = dnaArrayZipped[i]
			for j, value in enumerate(demands):
				if value < prods[j]:
					return False

		return True

	def zipDnaArray(self):
		"""
		"""
		self.dnaArrayZipped = [[] for i in range(0, InputDataInstance.instance.nItems)]

		for index, item in enumerate(self.dnaArray):
			if (item != 0):
				self.dnaArrayZipped[item - 1].append(index)


	def mutate(self, strategy = "minimal"):
		"""
		"""

		mutations = []

		if strategy == "maximal":
			bestDnaArrayCost = 0
			bestDnaArray = None

		for i1, itemProdIndexes in enumerate(self.dnaArrayZipped):

			j1 = len(itemProdIndexes) - 1
			while j1 >= 0:

				item1ProdIndex = itemProdIndexes[j1]
				item1DemandIndex = InputDataInstance.instance.demandsArrayZipped[i1][j1]
				for i2, indexes in enumerate(self.dnaArrayZipped):

					if i1 == i2:
						continue

					j2 = len(indexes) - 1
					while j2 >=0:
						item2ProdIndex = indexes[j2]
						item2DemandIndex = InputDataInstance.instance.demandsArrayZipped[i2][j2]
						# print(InputDataInstance.instance.demandsArrayZipped, '|',self.dnaArrayZipped)
						# print(item1ProdIndex, item2ProdIndex, '|',i1, j1, '|',i2, j2)

						if (item1ProdIndex <= item2DemandIndex and item2ProdIndex <= item1DemandIndex):
							dnaArray = [i for i in self.dnaArray]
							dnaArray[item1ProdIndex], dnaArray[item2ProdIndex] = dnaArray[item2ProdIndex], dnaArray[item1ProdIndex] 
							# print(dnaArray)
							if not(dnaArray in mutations):
								mutations.append(dnaArray)

							if strategy == "minimal":
								if len(mutations) == 1:
									self.dnaArray = dnaArray
									self.zipDnaArray()
									self.cost = Chromosome.calculateCost(dnaArray, InputDataInstance.instance)
									return None
							elif strategy == "maximal":
								cost = Chromosome.calculateCost(dnaArray, InputDataInstance.instance)
								if (cost > bestDnaArrayCost):
									bestDnaArray = dnaArray
									bestDnaArrayCost = cost

						j2 -= 1

				j1 -= 1

		if strategy == "random":
			random.shuffle(mutations)
			dnaArray = mutations[0]

			self.dnaArray = dnaArray
			self.zipDnaArray()
			self.cost = Chromosome.calculateCost(dnaArray, InputDataInstance.instance)

		elif strategy == "maximal":
			self.dnaArray = bestDnaArray
			self.cost = bestDnaArrayCost
			self.zipDnaArray()

		# Variables
		# self._solution = [] 
		# self.itemsRank = []
		# self._fitnessValue = 0
		# self._hashSolution = ""
		# self.manufactItemsPeriods = [] 

		# for i in range(0, Chromosome.problem.nbItems+1):
		# 	self.manufactItemsPeriods.append([])

	# the following lines have to be removed, they've been added just for test
	def init1(self, solution, fitnessValue = 0):

		self._solution = list(solution)
		self._get_hashSolution()

		self._fitnessValue = Node.evaluate(self._solution)
		#self.get_itemsRanks()

	def __lt__(self, chromosome):
		return self._fitnessValue < chromosome.fitnessValue

	# Getters

	def _get_fitnessValue(self):
		return self._fitnessValue

	def _get_solution(self):
		return self._solution

	def _get_hashSolution(self):
		return self._hashSolution

	# Setters

	def _set_hashSolution(self, new_value):
		self._hashSolution = new_value

	def _set_solution(self, new_solution):
		self._solution = new_solution

	def _set_fitnessValue(self, new_value):
		self._fitnessValue = new_value

	def __repr__(self):
		return " {} : {} ".format(self.dnaArray, self.cost)

	def __eq__(self, chromosome):
		return self._solution == chromosome.solution

	def __ne__(self, chromosome):
		return self._solution != chromosome.solution
	
	# Genetic operators and other function

	def isFeasible(self):

		# i check first that there's not shortage or backlogging
		i = 0
		feasible = False
		while i < Chromosome.problem.nbItems:

			itemDemandPeriods = Chromosome.problem.deadlineDemandPeriods[i]

			itemManufactPeriods = getManufactPeriods(self._solution,i+1)

			if (len(itemManufactPeriods) != len(itemDemandPeriods)):
				return False
			else:
				j = 0
				nbitemManufactPeriods = len(itemManufactPeriods)
				while j < nbitemManufactPeriods:

					if (itemManufactPeriods[j] > itemDemandPeriods[j]):
						return False

					j+=1

				feasible = True

			i+=1

		if feasible:
			#print("Feasible True")
			return True
		#print("Feasible False")
		return False

	def mutate2(self):


		randomIndice = randint(0,(Chromosome.problem.nbTimes-1))

		item1 = self._solution[randomIndice]

		# i make sure that the randomIndice variable never corresponds to a zero indice
		while item1 == 0:
			randomIndice = randint(0,(Chromosome.problem.nbTimes-1))
			# i get the item corresponding the gene to be flipped
			item1 = self._solution[randomIndice]

		#print(" randomIndice : ", randomIndice)
		itemsRank = self.itemsRank
		item1DemandPeriod = Chromosome.problem.deadlineDemandPeriods[item1-1][itemsRank[randomIndice]-1]

		i = item1DemandPeriod

		while i > 0:

			if self._solution[i] != item1:

				if self._solution[i] != 0: 

					if Chromosome.problem.deadlineDemandPeriods[self._solution[i]-1][self.itemsRank[i]-1] >= randomIndice and item1DemandPeriod >= i:

						item2 = self._solution[i]
						item2DemandPeriod = Chromosome.problem.deadlineDemandPeriods[item2-1][itemsRank[i]-1]
						if item2DemandPeriod >= randomIndice:

							c = Chromosome()
							c.solution = switchGenes(self.solution, randomIndice, i)
							c.itemsRank = switchGenes(self.itemsRank, randomIndice, i)
							c.fitnessValue = AdvMutateNode.evalSwitchedChrom(self.solution, self.fitnessValue, self.itemsRank, randomIndice, i)
							self.manufactItemsPeriods = list(self.manufactItemsPeriods)
							#print("OKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK")
							break

				else:
					
					c = Chromosome()
					c.solution = switchGenes(self.solution, randomIndice, i)
					c.itemsRank = switchGenes(self.itemsRank, randomIndice, i)
					c.fitnessValue = AdvMutateNode.evalSwitchedChrom(self.solution, self.fitnessValue, self.itemsRank, randomIndice, i)
					self.manufactItemsPeriods = list(self.manufactItemsPeriods)
					#print("OKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK1")
					break


			i-=1
		

	#--------------------
	# function : mutate
	# Class : Chromosome
	# purpose : Applying mutation to a given chromosome and returning the resulting one
	#--------------------


	def getCostTab(self):

		i = 0
		costTab = []

		size1 = len(self._solution)
		for i in range(0, size1):

			if self._solution[i] != 0:

				rec = []
				rec.append(self._solution[i])
				rec.append(Chromosome.problem.deadlineDemandPeriods[self._solution[i]-1][self.itemsRank[i]-1])
				rec.append(self.itemsRank[i])
				rec.append(i)
				costTab.append(rec)

		#costTab = sorted(costTab, key = getCostTabKey)
		return costTab

	def checkItemRank(self):

		i = 0 
		while i < Chromosome.problem.nbTimes:

			if self.itemsRank[i] > len(Chromosome.problem.deadlineDemandPeriods[self.solution[i]-1]):
				print (" OKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK ")

			i+=1


	def advmutate(self):
		# In order to implement this local search, i try to find out the gene that i call the critical gene, that's to say, the gene
		# with the highest cost depending on the changeover cost and the holding cost	
		
		# We're gonna search the nearby era to find out a better solution to this problem
		nbResults = 1
		queue = []
		currentNode = AdvMutateNode(self)
		
		while True:

			#print("Current node : ", currentNode)
			child = currentNode.getChild()
			#print("Child : ", child)

			if child == []:

				self._solution = copy.deepcopy(currentNode.chromosome.solution)
				self.itemsRank = copy.deepcopy(currentNode.chromosome.itemsRank)
				self._fitnessValue = currentNode.chromosome.fitnessValue
				#self._hashSolution = copy.deepcopy(currentNode.chromosome.hashSolution)

				return

			queue.append(child)

			if queue == []:
				break

			currentNode = queue[len(queue)-1]
			del queue[len(queue)-1]
			

	def getProductionPeriodsByItem(self):

		
		data = []

		for i in range(0, Chromosome.problem.nbItems):
			data.append([])

		for i in range(0, Chromosome.problem.nbTimes):

			if self._solution[i] != 0:

				(data[self._solution[i] - 1]).append([i, Chromosome.problem.deadlineDemandPeriods[self._solution[i] - 1][self.itemsRank[i] - 1]])

		return data

	def getFeasible(self):

		# i make sure that the number of goods producted isn't superior to the number expected
		# and doing that, we take this opportunity to get the fitness value of the chromosome, we're getting feasible
		self.fitnessValue = 0
		zeroperiods = []
		copy_solution = list(self._solution)
		copy_itemRank = list(self.itemsRank)
		self.manufactItemsPeriods = getManufactPeriodsGrid(Chromosome.problem.nbItems, Chromosome.problem.deadlineDemandPeriods)

		i = 0
		while i < Chromosome.problem.nbTimes:

			#print("1 ----------- : ", self._solution[i], i, self._solution)
			if self._solution[i] != 0:

				item = self._solution[i]
				rank = self.itemsRank[i]
				#print("1 ----------- : ", item, rank, self.manufactItemsPeriods)
				value = self.manufactItemsPeriods[item-1][rank-1]

				if value == -1:

					self.manufactItemsPeriods[item-1][rank-1] = i
					self.fitnessValue += Chromosome.getCostof(i, item, rank, copy_solution)
					#print("1 --------- : ", item, i, self.fitnessValue, self._solution, copy_solution)

				else:

					cost1 = Chromosome.getEnvItemCost(value, item, rank, copy_solution, i)
					cost2 = Chromosome.getEnvItemCost(i, item, rank, copy_solution, value)

					#print(" cost 1 : ", cost1, " cost2 : ", cost2, i, self.fitnessValue)
					if cost2 < cost1 :

						self.manufactItemsPeriods[item-1][rank-1] = i
						nextItem, nextIndice = getNextItem(copy_solution, Chromosome.problem.nbTimes, value)

						self._solution[value] = 0
						self.itemsRank[value] = 0
						zeroperiods.append(value)
						copy_solution = list(self._solution)
						copy_itemRank = list(self.itemsRank)

						if nextIndice >= i:
							self.fitnessValue -= Chromosome.getCostof(value, item, rank, copy_solution)
							#print("2-  cost 1 : ", cost1, " cost2 : ", cost2, i, self.fitnessValue, Chromosome.getCostof(i, item, rank, copy_solution))
							self.fitnessValue += Chromosome.getCostof(i, item, rank, copy_solution)

						else:
							self.fitnessValue = Chromosome.getRemNewFitnessValue(value, item, rank, self._solution, self.fitnessValue)
							#print("ooh", self.fitnessValue)
							self.fitnessValue += Chromosome.getCostof(i, item, rank, copy_solution)

					else:

						self._solution[i] = 0
						self.itemsRank[i] = 0
						copy_solution = list(self._solution)
						copy_itemRank = list(self.itemsRank)
						zeroperiods.append(i)

					#print("2 --------- : ", item, i, self.fitnessValue, self._solution, copy_solution)
			else:
				zeroperiods.append(i)

			i+=1

		#print(" in middle getFeasible : ", self._solution, self.fitnessValue, zeroperiods)
		# i make sure that the number of items producted isn't inferior to the number expected

		copy_solution = list(self._solution)
		copy_itemRank = list(self.itemsRank)

		i = 0
		while i < Chromosome.problem.nbItems:

			nbmanufactItemsPeriods = len(self.manufactItemsPeriods[i])
			j = nbmanufactItemsPeriods - 1
			
			while j >= 0 :

				if self.manufactItemsPeriods[i][j] == -1:

					#print("in if : ", i+1, j+1, zeroperiods, copy_solution)

					deadline = Chromosome.problem.deadlineDemandPeriods[i][j]
					nbZeroPeriods = len(zeroperiods)

					cost1 = Chromosome.getEnvItemCost(zeroperiods[0], i+1, j+1, copy_solution)
					#print(" deadline : ", deadline )

					k = 0 
					indice = zeroperiods[0]
					while k < nbZeroPeriods and zeroperiods[k] <= deadline : #nbZeroPeriods:
						cost2 = Chromosome.getEnvItemCost(zeroperiods[k], i+1, j+1, copy_solution)
						#print(" cost2 : ", cost2 , zeroperiods[k], k)
						if cost2 < cost1:
							#print(" cost2 < cost1 : ", cost1 , cost2 )
							indice = zeroperiods[k]
							cost1 = cost2
						k+=1

					zeroperiods.remove(indice)
					self.fitnessValue = Chromosome.getPutNewFitnessValue(indice, i+1, j+1, self._solution, self.fitnessValue)
					self._solution[indice] = i+1
					self.itemsRank[indice] = j+1
					self.manufactItemsPeriods[i][j] = indice
					copy_solution = list(self._solution)
					copy_itemRank = list(self.itemsRank)

				j-=1
			i+=1

	def getEnvItemCost(cls, indice, item, rank, solution, secondIndice = -1):

		solution = list(solution) # TODO

		if secondIndice != -1:
			solution[secondIndice] = 0

		nextItem, nextIndice = getNextItem(solution, Chromosome.problem.nbTimes, indice)
		cost = cls.getCostof(indice, item, rank, solution)
		if nextItem != 0:
			cost += int(Chromosome.problem.chanOverGrid[item-1][nextItem-1])
		return cost

	getEnvItemCost = classmethod(getEnvItemCost)

	
	def getRemNewFitnessValue(cls, indice, item, rank, solution, fitnessValue):

			prevItem, prevIndice = getPrevItem(solution, indice)
			nextItem, nextIndice = getNextItem(solution, Chromosome.problem.nbTimes, indice)
			fitnessValue -= cls.getCostof(indice, item, rank, solution)
			if nextItem != 0:
				fitnessValue -= int(Chromosome.problem.chanOverGrid[item-1][nextItem-1])
				#print('in rem ', prevItem, prevIndice, nextItem, nextIndice, fitnessValue)
				if prevItem != 0:
					fitnessValue += int(Chromosome.problem.chanOverGrid[prevItem-1][nextItem-1])

			return fitnessValue
	getRemNewFitnessValue = classmethod(getRemNewFitnessValue)



	def getPutNewFitnessValue(cls, indice, item, rank, solution, fitnessValue):

		prevItem, prevIndice = getPrevItem(solution, indice)
		nextItem, nextIndice = getNextItem(solution, Chromosome.problem.nbTimes, indice)
		fitnessValue += cls.getCostof(indice, item, rank, solution)
		if nextItem != 0:
			if prevItem != 0:
				fitnessValue -= int(Chromosome.problem.chanOverGrid[prevItem-1][nextItem-1])
			fitnessValue += int(Chromosome.problem.chanOverGrid[item-1][nextItem-1])

		return fitnessValue
	getPutNewFitnessValue = classmethod(getPutNewFitnessValue)
	


	def getCostof(cls, indice, item, rank, solution):

		#solution = list(solution)

		cost = 0
		if item == 0:
			return cost

		# stocking cost 
		deadline = cls.problem.deadlineDemandPeriods[item-1][rank-1]
		cost += (deadline - indice)* int(Chromosome.problem.holdingGrid[item-1])

		#print(" cost 1 : ", cost)

		pItem, pIndice = previousPeriodItemOf(indice, solution)
		#print(" pItem : ", pItem, " pIndice : ", pIndice, " solution : ", solution)
		if pItem != 0:
			cost += int(Chromosome.problem.chanOverGrid[pItem-1][item-1])

		#print(" cost 3 : ", cost)

		return cost

	# Class' methods
	getCostof = classmethod(getCostof)

	# Properties
	solution = property(_get_solution,_set_solution)
	fitnessValue = property(_get_fitnessValue,_set_fitnessValue)


