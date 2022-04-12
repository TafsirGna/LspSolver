#!/usr/bin/python3.5
# -*-coding: utf-8 -*

import copy
import enum
import queue
import numpy as np
import random
from LspAlgorithms.GeneticAlgorithms.Gene import Gene
from LspAlgorithms.GeneticAlgorithms.MutationSearchNode import MutationSearchNode
from LspInputDataReading.LspInputDataInstance import InputDataInstance

class Chromosome(object):

	def __init__(self):
		"""
		"""
		self.cost = 0
		self.dnaArray = None
		self.startingGene, self.endingGene = None, None
		# self.zipDnaArray(dnaArray)


	def calculateCost(self):
		"""
		"""

		# if len(dnaArray) == inputDataInstance.nPeriods:
		# 	return cls.calculateCostPlainDNA(dnaArray, inputDataInstance)
		
		# if len(dnaArray) == inputDataInstance.nItems:
		# 	return cls.calculateCostZippedDNA(dnaArray, inputDataInstance)

		self.cost = Chromosome.classCalculateCost(self.dnaArray)


	@classmethod
	def classCalculateCost(cls, dnaArray):
		"""
		"""

		cost = 0
		
		for itemGenes in dnaArray:
			for gene in itemGenes:
				cost += gene.cost

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

		# going through the zipped dna array checking : ->
		# indices = []
		for item in range(inputDataInstance.nItems):
			demands = inputDataInstance.demandsArrayZipped[item]
			prods = dnaArray[item]

			if len(demands) != len(prods): # -> that the number of produced item meets the number of demand
				return False

			for j, demandIndex in enumerate(demands):
				gene = prods[j]

				if gene == None: # -> that item production index is a very period and there's no duplicate value
					return False

				prevProdIndex = (0 if j == 0 else (prods[j - 1]).period) # -> that previous period where the item has bee produced is always less than the current one
				if (prevProdIndex > gene.period):
					return False

				if gene.period > demandIndex: # checks that the item is produced before its demand period
					return False

				# indices.append(prodIndex)

		return True

	def zipDnaArray(self, dnaArray):
		"""
		"""
		self.dnaArrayZipped = Chromosome.classZipDnaArray(dnaArray)


	def renderDnaArray(self):
		"""
		"""
		return Chromosome.classRenderDnaArray(self.dnaArray)


	@classmethod
	def classRenderDnaArray(cls, dnaArray):
		"""
		"""
		result = [0 for _ in range(InputDataInstance.instance.nPeriods)]

		for item, itemIndices in enumerate(dnaArray):
			for gene in itemIndices:
				if gene != None:
					result[gene.period] = item + 1

		return result

	@classmethod
	def convertRawDNA(cls, rawDnaArray):
		"""
		"""
		dnaArray = [[] for _ in range(InputDataInstance.instance.nItems)]

		prevGene = None
		producedItemsCount = [0 for _ in range(InputDataInstance.instance.nItems)]
		for index, item in enumerate(rawDnaArray):
			if item != 0:
				position = producedItemsCount[item - 1]
				refinedItem = item - 1

				gene = Gene(refinedItem, index, position, prevGene)
				gene.calculateCost()
				dnaArray[refinedItem].append(gene)
				prevGene = refinedItem, position
				producedItemsCount[refinedItem] += 1
			
		# print(dnaArray)
		return dnaArray


	@classmethod
	def searchMutations(cls, dnaArray):
		"""
		"""

		mutations = []
		renderedDnaArray = Chromosome.classRenderDnaArray(dnaArray)

		for i1, itemProdGenes in enumerate(dnaArray):

			j1 = len(itemProdGenes) - 1
			while j1 >= 0:

				item1ProdGene = itemProdGenes[j1]
				item1DemandIndex = InputDataInstance.instance.demandsArrayZipped[i1][j1]
				bottomLimit = (0 if j1 == 0 else (dnaArray[i1][j1 - 1]).period + 1)
				#first approach

				for period, periodValue in enumerate(renderedDnaArray[bottomLimit:InputDataInstance.instance.demandsArrayZipped[i1][j1] + 1]):
					if (periodValue - 1) != i1:
						mutationItem = None
						if periodValue == 0:
							# mutationItem = [[i1, (dnaArray[i1][j1]).period], [-1, period + bottomLimit]]
							mutationItem = [[i1, j1], [-1, period + bottomLimit]]
						else:
							item2ProdIndex = period + bottomLimit
							item2ProdPosition = ([i for i, gene in enumerate(dnaArray[periodValue - 1]) if gene.period == item2ProdIndex])[0]
							item2DemandIndex = InputDataInstance.instance.demandsArrayZipped[periodValue - 1][item2ProdPosition]
							if item2DemandIndex >= item1ProdGene.period and item1DemandIndex >= item2ProdIndex:
								# mutationItem = [[i1, (dnaArray[i1][j1]).period], [periodValue - 1, (dnaArray[periodValue - 1][item2ProdPosition]).period]]
								mutationItem = [[i1, j1], [periodValue - 1, item2ProdPosition]]
						
						if mutationItem != None and not(mutationItem in mutations) and not([mutationItem[1], mutationItem[0]] in mutations):
							mutations.append(mutationItem)

				j1 -= 1

		# print("mutations --> ", mutations)

		return mutations


	@classmethod
	def bestMutation(cls, chromosome, mutations):
		"""
		"""

		fittestDnaArray = [None, 0, None]
		for mutation in mutations:

			dnaArray = [[copy.deepcopy(gene) for gene in itemGenes] for itemGenes in chromosome.dnaArray]
			# print("Mutation ---> ", mutation)
			if mutation[1][0] == -1:
				(dnaArray[mutation[0][0]][mutation[0][1]]).period = mutation[1][1]
			else:
				(dnaArray[mutation[0][0]][mutation[0][1]]).period, (dnaArray[mutation[1][0]][mutation[1][1]]).period = (dnaArray[mutation[1][0]][mutation[1][1]]).period, (dnaArray[mutation[0][0]][mutation[0][1]]).period

			genesList = sorted([gene for itemProdGenes in dnaArray for gene in itemProdGenes], key= lambda gene: gene.period)

			prevGene = None
			cost = 0
			for index, gene in enumerate(genesList):
				if ([gene.item, gene.position] in mutation):
					gene.prevGene = (prevGene.item, prevGene.position) if prevGene != None else None              
					gene.calculateCost()
				cost += gene.cost
				prevGene = gene

			# print("DnaArray ---> ", dnaArray, cost)

			if cost < chromosome.cost:
				fittestDnaArray[0] = dnaArray
				fittestDnaArray[1] = cost
				fittestDnaArray[2] = mutation

		if fittestDnaArray[0] != None:

			result = Chromosome()
			result.dnaArray = fittestDnaArray[0]
			result.cost = fittestDnaArray[1]
			return result

		return None


	def sliceDna(self, startingPeriod, endingPeriod):
		"""
		"""
		genesList = sorted([gene for itemProdGenes in self.dnaArray for gene in itemProdGenes], key= lambda gene: gene.period)
		slice = []
		for index, gene1 in enumerate(genesList):
			if startingPeriod <= gene1.period:
				for gene2 in genesList[index:]:
					if (endingPeriod > gene2.period):
						slice.append(gene2)
					else:
						break
				break

		return slice


	@classmethod
	def localSearch(cls, chromosome):
		"""
		"""

		mutations = Chromosome.searchMutations(chromosome.dnaArray)
		betterChromosome = Chromosome.bestMutation(chromosome, mutations)
		while betterChromosome is not None:
			chromosome = betterChromosome
			mutations = Chromosome.searchMutations(chromosome.dnaArray)
			betterChromosome = Chromosome.bestMutation(chromosome, mutations)

		return chromosome


	def mutate(self):
		"""
		"""
		chromosome = Chromosome.localSearch(self)
		self.dnaArray = chromosome.dnaArray
		self.cost = chromosome.cost


	def __lt__(self, chromosome):
		return self.cost < chromosome.cost

	def __repr__(self):
		# return " {} : {} --- {}".format(self.renderDnaArray(), self.cost, self.dnaArray)
		return " {} : {}".format(self.renderDnaArray(), self.cost)

	def __eq__(self, chromosome):
		return self.dnaArray == chromosome.dnaArray	