#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from operator import itruediv
import queue
from turtle import position
import numpy as np
from LspAlgorithms.GeneticAlgorithms.Gene import Gene
from LspInputDataReading.LspInputDataInstance import InputDataInstance

class Chromosome(object):

	def __init__(self):
		"""
		"""
		self.cost = 0
		self.dnaArray = [[None for _ in indices] for indices in InputDataInstance.instance.demandsArrayZipped]
		self.stringIdentifier = ""


	def calculateCost(self):
		"""
		"""

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
				# if gene.cost == 0:
				gene.calculateStockingCost()
				gene.calculateChangeOverCost()
				gene.calculateCost()
				cost += gene.cost

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

				if gene is None: # -> that item production index is a very period and there's no duplicate value
					return False

				prevProdIndex = (0 if j == 0 else (prods[j - 1]).period) # -> that previous period where the item has bee produced is always less than the current one
				if (prevProdIndex > gene.period):
					return False

				if gene.period > demandIndex: # checks that the item is produced before its demand period
					return False

				# indices.append(prodIndex)

		return True


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
	def evaluateDnaArray(cls, dnaArray, focus = []):
		"""
		"""

		genesList = sorted([gene for itemProdGenes in dnaArray for gene in itemProdGenes], key= lambda gene: gene.period)
		# genesList = sorted([gene for itemProdGenes in dnaArray for gene in itemProdGenes if gene is not None], key= lambda gene: gene.period)

		prevGene = None
		stringIdentifier = "0" * InputDataInstance.instance.nPeriods
		cost = 0
		for gene in genesList:
			compute = True
			
			if len(focus) > 0 and not ((gene.item, gene.position) in focus):
				compute = False

			if compute:
				gene.prevGene = (prevGene.item, prevGene.position) if prevGene is not None else None 
				gene.calculateChangeOverCost()             
				gene.calculateCost()
			cost += gene.cost
			prevGene = gene
			stringIdentifier = stringIdentifier[:gene.period] + str(gene.item + 1) + stringIdentifier[gene.period + 1:]

		return dnaArray, stringIdentifier, cost


	@classmethod
	def sliceDna(cls, dnaArray, startingPeriod, endingPeriod):
		"""
		"""

		genesList = sorted([gene for itemProdGenes in dnaArray for gene in itemProdGenes if gene is not None], key= lambda gene: gene.period)
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
	def classRenderDnaArray(cls, dnaArray):
		"""
		"""
		result = [0 for _ in range(InputDataInstance.instance.nPeriods)]

		for item, itemIndices in enumerate(dnaArray):
			for gene in itemIndices:
				if gene is not None:
					result[gene.period] = item + 1

		return result


	def __lt__(self, chromosome):
		return self.cost < chromosome.cost

	def __repr__(self):
		return "{} : {}".format(Chromosome.classRenderDnaArray(self.dnaArray), self.cost)
		return "{} : {}".format(self.stringIdentifier, self.cost)
		# return "{} : {} | {} - {} /".format(self.renderDnaArray(), self.cost, Chromosome.calculateCostPlainDNA(Chromosome.classRenderDnaArray(self.dnaArray), InputDataInstance.instance), Chromosome.feasible(self.dnaArray, InputDataInstance.instance))

	def __eq__(self, chromosome):
		return self.stringIdentifier == chromosome.stringIdentifier