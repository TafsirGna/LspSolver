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

	def __init__(self, dnaArray = []):
		"""
		"""
		self.cost = 0	#self.calculateCost(self.dnaArray, InputDataInstance.instance)
		self.zipDnaArray(dnaArray)


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
		dnaArrayZipped = [[] for _ in range(0, InputDataInstance.instance.nItems)]

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

	def zipDnaArray(self, dnaArray):
		"""
		"""
		self.dnaArrayZipped = [[] for _ in range(0, InputDataInstance.instance.nItems)]

		for index, item in enumerate(dnaArray):
			if (item != 0):
				self.dnaArrayZipped[item - 1].append(index)

	def unzipDnaArray(self):
		"""
		"""
		dnaArray = [0 for _ in range(0, InputDataInstance.instance.nPeriods)]

		for item, itemIndexes in enumerate(self.dnaArrayZipped):
			for index in itemIndexes:
				dnaArray[index] = item + 1

		return dnaArray


	def mutate(self, strategy = "minimal"):
		"""
		"""

		mutations = []

		if strategy == "maximal":
			bestCost = 10 ** 100
			bestDnaArrayZipped = None

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

							dnaArrayZipped = [[index for index in itemIndexes] for itemIndexes in self.dnaArrayZipped]
							dnaArrayZipped[i1][j1], dnaArrayZipped[i2][j2] = dnaArrayZipped[i2][j2], dnaArrayZipped[i1][j1] 

							if not(dnaArrayZipped in mutations):
								mutations.append(dnaArrayZipped)

							if strategy == "minimal":
								if len(mutations) == 1:
									self.dnaArrayZipped = dnaArrayZipped
									self.cost = 0	#Chromosome.calculateCost(dnaArray, InputDataInstance.instance)
									return None
							if strategy == "maximal":
								cost = 0	#Chromosome.calculateCost(dnaArray, InputDataInstance.instance)
								if (cost < bestCost):
									bestDnaArrayZipped = dnaArrayZipped
									bestCost = cost

						j2 -= 1

				j1 -= 1

		if strategy == "random":
			random.shuffle(mutations)
			bestDnaArrayZipped = mutations[0]

			self.dnaArrayZipped = dnaArrayZipped
			self.cost = 0 #Chromosome.calculateCost(dnaArray, InputDataInstance.instance)

		elif strategy == "maximal":
			self.dnaArrayZipped = bestDnaArrayZipped
			self.cost = bestCost


	def __lt__(self, chromosome):
		return self._fitnessValue < chromosome.fitnessValue

	def __repr__(self):
		return " {} : {} ".format(self.unzipDnaArray(), self.cost)

	def __eq__(self, chromosome):
		return self._solution == chromosome.solution

	def __ne__(self, chromosome):
		return self._solution != chromosome.solution

	