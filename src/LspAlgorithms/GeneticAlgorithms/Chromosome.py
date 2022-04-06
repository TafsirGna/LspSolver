#!/usr/bin/python3.5
# -*-coding: utf-8 -*

import numpy as np
import random
from LspInputDataReading.LspInputDataInstance import InputDataInstance

class Chromosome(object):

	def __init__(self, dnaArray = []):
		"""
		"""
		self.cost = 0
		self.zipDnaArray(dnaArray)


	@classmethod
	def calculateCost(cls, dnaArray, inputDataInstance):
		"""
		"""

		if len(dnaArray) == inputDataInstance.nPeriods:
			return cls.calculateCostPlainDNA(dnaArray, inputDataInstance)
		
		if len(dnaArray) == inputDataInstance.nItems:
			return cls.calculateCostZippedDNA(dnaArray, inputDataInstance)

		return None

	@classmethod
	def calculateCostZippedDNA(cls, dnaArrayZipped, inputDataInstance):
		"""
		"""

		cost = 0
		tupleList = []

		# print(dnaArrayZipped, inputDataInstance.demandsArrayZipped)

		for item, itemIndices in enumerate(dnaArrayZipped):
			for i, index in enumerate(itemIndices):
				cost += (inputDataInstance.demandsArrayZipped[item][i] - dnaArrayZipped[item][i]) \
					* inputDataInstance.stockingCostsArray[item]
				pair = (index, item + 1)
				tupleList.append(pair)

		tupleList.sort(key=lambda pair: pair[0])
		# print(tupleList)
		
		for i in range(1, len(tupleList)):
			cost += inputDataInstance.chanOverArray[tupleList[i - 1][1] - 1][tupleList[i][1] - 1]
			# print(cost)

		return cost

	@classmethod
	def calculateCostPlainDNA(cls, dnaArray, inputDataInstance):
		"""
		"""

		cost = 0
		item1, item2 = dnaArray[0], dnaArray[0]
		nOccurenceItem = np.array([0 for _ in range(inputDataInstance.nItems)])
		if item2 is not 0:
			nOccurenceItem[item2 - 1] += 1
			cost += inputDataInstance.stockingCostsArray[item2 - 1] * (inputDataInstance.demandsArrayZipped[item2 - 1][nOccurenceItem[item2 - 1] -1] - 0)

		for index in range(1, len(dnaArray)):
			if dnaArray[index] is not 0:
				item2 = dnaArray[index]
				cost += inputDataInstance.chanOverArray[item1 - 1 , item2 - 1]
				nOccurenceItem[item2 - 1] += 1
				cost += inputDataInstance.stockingCostsArray[item2 - 1] * (inputDataInstance.demandsArrayZipped[item2 - 1][nOccurenceItem[item2 - 1] - 1] - index)

				item1 = item2
			else: 
				continue

		return cost

	@classmethod
	def feasible(cls, dnaArray, inputDataInstance):
		"""Checks if a given dnaArray leads to a feasible chromosome
		"""

		dnaArrayZipped = None
		if len(dnaArray) == inputDataInstance.nPeriods:
			dnaArrayZipped = Chromosome.classZipDnaArray(dnaArray)
		elif len(dnaArray) == inputDataInstance.nItems:
			dnaArrayZipped = dnaArray

		indices = []
		for i in range(inputDataInstance.nItems):
			demands = inputDataInstance.demandsArrayZipped[i]
			prods = dnaArrayZipped[i]

			if len(demands) is not len(prods): # checks that the number of produced item meets the number of demand
				return False

			for j, value in enumerate(demands):
				prodIndex = prods[j]

				if prodIndex is None or prodIndex in indices:
					return False
				indices.append(prodIndex)

				if value < prodIndex: # checks that the item is produced before its demand period
					return False

		return True

	def zipDnaArray(self, dnaArray):
		"""
		"""
		self.dnaArrayZipped = Chromosome.classZipDnaArray(dnaArray)


	@classmethod
	def classZipDnaArray(cls, dnaArray):
		"""
		"""
		dnaArrayZipped = [[] for _ in range(InputDataInstance.instance.nItems)]

		for index, item in enumerate(dnaArray):
			if item is not 0:
				dnaArrayZipped[item - 1].append(index)
			
		return dnaArrayZipped


	def unzipDnaArray(self):
		"""
		"""
		return Chromosome.classUnzipDnaArray(self.dnaArrayZipped)


	@classmethod
	def classUnzipDnaArray(cls, dnaArrayZipped):
		"""
		"""
		dnaArray = [0 for _ in range(InputDataInstance.instance.nPeriods)]

		for item, itemIndices in enumerate(dnaArrayZipped):
			for index in itemIndices:
				if index is not None:
					dnaArray[index] = item + 1

		return dnaArray


	@classmethod
	def localSearch(cls, dnaArray, inputDataInstance):
		"""
		"""

		dnaArrayZipped = None
		if len(dnaArray) == inputDataInstance.nPeriods:
			dnaArrayZipped = Chromosome.classZipDnaArray(dnaArray)
		elif len(dnaArray) == inputDataInstance.nItems:
			dnaArrayZipped = dnaArray
			dnaArray = Chromosome.classUnzipDnaArray(dnaArrayZipped)

		bestCost = Chromosome.calculateCost(dnaArrayZipped, inputDataInstance)
		bestDnaArrayZipped = dnaArrayZipped

		# print("fuuuuuuuuuuuuuuuuuuuuuuuck", Chromosome.calculateCost(dnaArrayZipped, inputDataInstance))

		for i1, itemProdIndexes in enumerate(dnaArrayZipped):

			j1 = len(itemProdIndexes) - 1
			while j1 >= 0:

				item1ProdIndex = itemProdIndexes[j1]
				item1DemandIndex = InputDataInstance.instance.demandsArrayZipped[i1][j1]
				bottomLimit = (0 if j1 == 0 else dnaArrayZipped[i1][j1 - 1])
				#first approach
				for period, periodValue in enumerate(dnaArray[bottomLimit:InputDataInstance.instance.demandsArrayZipped[i1][j1] + 1]):
					if periodValue == 0:
						dnaArrayZ = [[index for index in itemIndexes] for itemIndexes in dnaArrayZipped]
						dnaArrayZ[i1][j1] = period + bottomLimit								

						cost = Chromosome.calculateCost(dnaArrayZ, InputDataInstance.instance)
						if (cost < bestCost):
							bestDnaArrayZipped = dnaArrayZ
							bestCost = cost

				# second approach
				for i2, indexes in enumerate(dnaArrayZipped):

					if i1 == i2:
						continue

					j2 = len(indexes) - 1
					while j2 >=0:
						item2ProdIndex = indexes[j2]
						item2DemandIndex = InputDataInstance.instance.demandsArrayZipped[i2][j2]
						# print(InputDataInstance.instance.demandsArrayZipped, '|',self.dnaArrayZipped)
						# print(item1ProdIndex, item2ProdIndex, '|',i1, j1, '|',i2, j2)
						
						if item1ProdIndex <= item2DemandIndex and item2ProdIndex <= item1DemandIndex:

							bottomLimit1 , topLimit1 = (-1 if j1 == 0 else dnaArrayZipped[i1][j1 - 1]), (item1DemandIndex + 1 if j1 == len(itemProdIndexes) - 1 else dnaArrayZipped[i1][j1 + 1])
							bottomLimit2 , topLimit2 = (-1 if j2 == 0 else dnaArrayZipped[i2][j2 - 1]), (item2DemandIndex + 1 if j2 == len(indexes) - 1 else dnaArrayZipped[i2][j2 + 1])

							if (bottomLimit2 < item1ProdIndex and item1ProdIndex < topLimit2) and (bottomLimit1 < item2ProdIndex and item2ProdIndex < topLimit1):

								dnaArrayZ = [[index for index in itemIndexes] for itemIndexes in dnaArrayZipped]
								dnaArrayZ[i1][j1], dnaArrayZ[i2][j2] = dnaArrayZ[i2][j2], dnaArrayZ[i1][j1]								

								cost = Chromosome.calculateCost(dnaArrayZ, InputDataInstance.instance)
								if (cost < bestCost):
									bestDnaArrayZipped = dnaArrayZ
									bestCost = cost

						j2 -= 1

				j1 -= 1

		# print(dnaArrayZipped, bestDnaArrayZipped, bestCost, bestDnaArrayZipped == dnaArrayZipped)

		if (bestDnaArrayZipped == dnaArrayZipped):
			chromosome = Chromosome()
			chromosome.dnaArrayZipped = dnaArrayZipped
			chromosome.cost = bestCost
			return chromosome

		return Chromosome.localSearch(bestDnaArrayZipped, inputDataInstance)


	def mutate(self, strategy = "maximal"):
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
				bottomLimit = (0 if j1 == 0 else self.dnaArrayZipped[i1][j1 - 1])
				#first approach
				for period, periodValue in enumerate((self.unzipDnaArray())[bottomLimit:InputDataInstance.instance.demandsArrayZipped[i1][j1] + 1]):
					if periodValue == 0:
						dnaArrayZipped = [[index for index in itemIndexes] for itemIndexes in self.dnaArrayZipped]
						dnaArrayZipped[i1][j1] = period + bottomLimit								

						if not(dnaArrayZipped in mutations):
							mutations.append(dnaArrayZipped)

						if strategy == "minimal":
							if len(mutations) == 1:
								self.dnaArrayZipped = dnaArrayZipped
								self.cost = Chromosome.calculateCost(dnaArrayZipped, InputDataInstance.instance)
								return None
						if strategy == "maximal":
							cost = Chromosome.calculateCost(dnaArrayZipped, InputDataInstance.instance)
							if (cost < bestCost):
								bestDnaArrayZipped = dnaArrayZipped
								bestCost = cost

				# second approach
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

							bottomLimit1 , topLimit1 = (-1 if j1 == 0 else self.dnaArrayZipped[i1][j1 - 1]), (item1DemandIndex + 1 if j1 == len(itemProdIndexes) - 1 else self.dnaArrayZipped[i1][j1 + 1])
							bottomLimit2 , topLimit2 = (-1 if j2 == 0 else self.dnaArrayZipped[i2][j2 - 1]), (item2DemandIndex + 1 if j2 == len(indexes) - 1 else self.dnaArrayZipped[i2][j2 + 1])

							if (bottomLimit2 < item1ProdIndex and item1ProdIndex < topLimit2) and (bottomLimit1 < item2ProdIndex and item2ProdIndex < topLimit1):
								dnaArrayZipped = [[index for index in itemIndexes] for itemIndexes in self.dnaArrayZipped]
								dnaArrayZipped[i1][j1], dnaArrayZipped[i2][j2] = dnaArrayZipped[i2][j2], dnaArrayZipped[i1][j1] 

								if not(dnaArrayZipped in mutations):
									mutations.append(dnaArrayZipped)

								if strategy == "minimal":
									if len(mutations) == 1:
										self.dnaArrayZipped = dnaArrayZipped
										self.cost = Chromosome.calculateCost(dnaArrayZipped, InputDataInstance.instance)
										return None
								if strategy == "maximal":
									cost = Chromosome.calculateCost(dnaArrayZipped, InputDataInstance.instance)
									if (cost < bestCost):
										bestDnaArrayZipped = dnaArrayZipped
										bestCost = cost

						j2 -= 1

				j1 -= 1

		if strategy == "random":
			random.shuffle(mutations)
			self.dnaArrayZipped = mutations[0]
			self.cost = Chromosome.calculateCost(self.dnaArrayZipped, InputDataInstance.instance)

		elif strategy == "maximal":
			self.dnaArrayZipped = bestDnaArrayZipped
			self.cost = bestCost


	# def __lt__(self, chromosome):
	# 	return self._fitnessValue < chromosome.fitnessValue

	def __repr__(self):
		return " {} : {} ".format(self.unzipDnaArray(), self.cost)

	# def __eq__(self, chromosome):
	# 	return self._solution == chromosome.solution

	# def __ne__(self, chromosome):
	# 	return self._solution != chromosome.solution

	