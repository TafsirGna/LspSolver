#!/usr/bin/python3.5
# -*-coding: utf-8 -*

import copy
import enum
from operator import itruediv
import queue
from turtle import position
import numpy as np
import random
from LspAlgorithms.GeneticAlgorithms.Gene import Gene
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


	def geneAtPeriod(self, period):
		"""
		"""

		for itemGenes in self.dnaArray:
			for gene in itemGenes:
				if gene.period == period:
					return gene

		return None
		

	@classmethod
	def classCalculateCost(cls, dnaArray):
		"""
		"""

		cost = 0
		
		for itemGenes in dnaArray:
			for gene in itemGenes:
				if gene.cost == 0:
					gene.calculateStockingCost()
					gene.calculateChangeOverCost()
					gene.calculateCost()
				cost += gene.cost

		return cost

	# @classmethod
	# def calculateCostPlainDNA(cls, dnaArray, inputDataInstance):
	# 	"""
	# 	"""

	# 	cost = 0
	# 	item1, item2 = dnaArray[0], dnaArray[0]
	# 	nOccurenceItem = np.array([0 for _ in range(inputDataInstance.nItems)])
	# 	if item2 is not 0:
	# 		nOccurenceItem[item2 - 1] += 1
	# 		cost += inputDataInstance.stockingCostsArray[item2 - 1] * (inputDataInstance.demandsArrayZipped[item2 - 1][nOccurenceItem[item2 - 1] -1] - 0)

	# 	for index in range(1, len(dnaArray)):
	# 		if dnaArray[index] != 0:
	# 			item2 = dnaArray[index]
	# 			cost += inputDataInstance.changeOverCostsArray[item1 - 1 , item2 - 1]
	# 			nOccurenceItem[item2 - 1] += 1
	# 			cost += inputDataInstance.stockingCostsArray[item2 - 1] * (inputDataInstance.demandsArrayZipped[item2 - 1][nOccurenceItem[item2 - 1] - 1] - index)

	# 			item1 = item2
	# 		else: 
	# 			continue

	# 	return cost

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

				if gene is None: # -> that item production index is a very period and there's no duplicate value
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
				if gene is not None:
					result[gene.period] = item + 1

		return result

	@classmethod
	def convertRawDNA(cls, rawDnaArray):
		"""
		"""
		dnaArray = [[] for _ in range(InputDataInstance.instance.nItems)]

		prevGene = None
		producedItemsCount = [0 for _ in range(InputDataInstance.instance.nItems)]
		for period, periodValue in enumerate(rawDnaArray):
			if periodValue != 0:
				item = periodValue - 1
				position = producedItemsCount[item]

				gene = Gene(item, period, position, prevGene)
				gene.calculateCost()
				dnaArray[item].append(gene)
				prevGene = item, position
				producedItemsCount[item] += 1
			
		# print(dnaArray)
		return dnaArray

	@classmethod
	def genePossibleMutations(cls, gene1, dnaArray, strategy = "all"): # strategy can be "all" or "null" only for mutations related to null periods
		"""
		"""
		mutations = []

		gene1LowerLimit = 0 if gene1.position == 0 else (dnaArray[gene1.item][gene1.position - 1]).period + 1
		gene1UpperLimit = InputDataInstance.instance.demandsArrayZipped[gene1.item][gene1.position] + 1 if gene1.position == len(InputDataInstance.instance.demandsArrayZipped[gene1.item]) - 1 else (dnaArray[gene1.item][gene1.position + 1]).period

		for index, periodValue in enumerate(Chromosome.sliceDna(dnaArray, gene1LowerLimit, gene1UpperLimit)):
			period = index + gene1LowerLimit
			if periodValue == 0:
				mutation = Chromosome.evaluateMutation(dnaArray, gene1.item, gene1.position, -1, period)
				mutations.append(mutation)
			else:
				if strategy == "all":
					item2 = periodValue - 1
					if item2 != gene1.item:
						gene2 = [gene for gene in dnaArray[item2] if gene.period == period]
						gene2 = gene2[0]

						gene2LowerLimit = 0 if gene2.position == 0 else (dnaArray[gene2.item][gene2.position - 1]).period + 1
						gene2UpperLimit = InputDataInstance.instance.demandsArrayZipped[gene2.item][gene2.position] + 1 if gene2.position == len(InputDataInstance.instance.demandsArrayZipped[gene2.item]) - 1 else (dnaArray[gene2.item][gene2.position + 1]).period
						
						if (gene2LowerLimit <= gene1.period and gene1.period < gene2UpperLimit) and (gene1LowerLimit <= gene2.period and gene2.period < gene1UpperLimit):
							mutation = Chromosome.evaluateMutation(dnaArray, gene1.item, gene1.position, gene2.item, gene2.position)
							mutations.append(mutation)

		return mutations


	@classmethod
	def evaluateMutation(cls, dnaArray, item1, position1, item2, position2):
		"""
		"""

		dnaArray = [[copy.deepcopy(gene) for gene in itemGenes] for itemGenes in dnaArray]

		gene1 = dnaArray[item1][position1] 

		if item2 == -1:
			gene1.period = position2
			gene1.calculateStockingCost()
		else:
			gene2 = dnaArray[item2][position2] 
			gene1.period, gene2.period = gene2.period, gene1.period
			gene1.calculateStockingCost()
			gene2.calculateStockingCost()

		genesList = sorted([gene for itemProdGenes in dnaArray for gene in itemProdGenes], key= lambda gene: gene.period)

		prevGene = None
		cost = 0
		for gene in genesList:
			if ((gene.item, gene.position) in [(item1, position1), (item2, position2)]):
				gene.prevGene = (prevGene.item, prevGene.position) if prevGene is not None else None 
				gene.calculateChangeOverCost()             
				gene.calculateCost()
			cost += gene.cost
			prevGene = gene

		return dnaArray, cost


	@classmethod
	def searchMutations(cls, dnaArray):
		"""
		"""

		mutations = []

		genesList = sorted([gene for itemProdGenes in dnaArray for gene in itemProdGenes], key= lambda gene: gene.cost, reverse=True)

		for gene in genesList:
			mutations += Chromosome.genePossibleMutations(gene, dnaArray)
		
		return mutations


	@classmethod
	def bestMutation(cls, chromosome, mutations):
		"""
		"""

		if len(mutations) == 0:
			return None

		mutation = min(mutations, key=lambda pair:pair[1])

		if (mutation[1] >= chromosome.cost):
			return None

		result = Chromosome()
		result.dnaArray = mutation[0]
		result.cost = mutation[1]

		return result

	@classmethod
	def arrangeDna(cls, dnaArray):
		"""
		"""

		genesList = sorted([gene for itemProdGenes in dnaArray for gene in itemProdGenes], key= lambda gene: gene.period)

		prevGene = None
		cost = 0
		for gene in genesList:
			gene.prevGene = (prevGene.item, prevGene.position) if prevGene != None else None 
			gene.calculateChangeOverCost()
			gene.calculateCost()          
			prevGene = gene
			cost += gene.cost
			
		return dnaArray, cost


	@classmethod
	def sliceDna(cls, dnaArray, startingPeriod, endingPeriod):
		"""
		"""

		genesList = sorted([gene for itemProdGenes in dnaArray for gene in itemProdGenes], key= lambda gene: gene.period)
		# print([gene.item + 1 for gene in genesList])
		slice = []
		cursor = startingPeriod
		for index, gene1 in enumerate(genesList):
			if startingPeriod <= gene1.period:
				for gene2 in genesList[index:]:
					if gene2 is not None:
						if (endingPeriod > gene2.period):
								slice += [0 for _ in range(gene2.period - cursor)] + [gene2.item + 1]
								cursor = gene2.period + 1
						else:
							break
				break

		return slice


	@classmethod
	def localSearch(cls, chromosome):
		"""
		"""

		mutations = Chromosome.searchMutations(chromosome.dnaArray)

		[print(mutation) for mutation in mutations]

		betterChromosome = Chromosome.bestMutation(chromosome, mutations)
		# print("----------------------------------------------------")
		while betterChromosome is not None:
			chromosome = betterChromosome
			mutations = Chromosome.searchMutations(chromosome.dnaArray)
			betterChromosome = Chromosome.bestMutation(chromosome, mutations)
			print("----------------------------------------------------")
			[print(mutation) for mutation in mutations]

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
		# return " {} : {} | {} - {} /".format(self.renderDnaArray(), self.cost, Chromosome.calculateCostPlainDNA(Chromosome.classRenderDnaArray(self.dnaArray), InputDataInstance.instance), Chromosome.feasible(self.dnaArray, InputDataInstance.instance))

	def __eq__(self, chromosome):
		return self.dnaArray == chromosome.dnaArray	