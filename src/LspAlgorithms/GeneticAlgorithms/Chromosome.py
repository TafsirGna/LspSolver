#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from collections import defaultdict
import threading
import numpy as np
import copy
from LspAlgorithms.GeneticAlgorithms.Gene import Gene
from LspInputDataReading.LspInputDataInstance import InputDataInstance
import concurrent.futures

from ParameterSearch.ParameterData import ParameterData

class Chromosome(object):

	pool = defaultdict(lambda: None) 
	localOptima = {"lock": threading.Lock(), "values": set()}

	def __init__(self):
		"""
		"""
		self.cost = 0
		self.dnaArray = [[None for _ in indices] for indices in InputDataInstance.instance.demandsArrayZipped]
		self.stringIdentifier = []
		self.genesByPeriod = defaultdict(lambda: None)
		

	@classmethod
	def classLightCostCalculation(cls, dnaArray):
		"""
		"""
		cost = 0
		for itemGenes in dnaArray:
			for gene in itemGenes:
				# print("Calculation : ", gene.cost)
				cost += gene.cost
		
		return cost


	@classmethod
	def evalAndFixDnaArray(cls, chromosome):
		"""
		"""

		# print("flash : ", chromosome.dnaArray, chromosome)
		lastProducedGene = None
		cost = 0
		itemPositionsTab = [0 for _ in range(InputDataInstance.instance.nItems)]
		for period, periodValue in enumerate(chromosome.stringIdentifier):
			if periodValue > 0:
				item = periodValue - 1

				gene = chromosome.dnaArray[item][itemPositionsTab[item]]

				if lastProducedGene is None:
					prevGene = None  
				else:
					prevGene = (lastProducedGene.item, itemPositionsTab[lastProducedGene.item] - 1)
					lastProducedGene.nextGene = (gene.item, gene.position)
				# print("ok : ", gene)
				# if prevGene != gene.prevGene:
				gene.prevGene = prevGene
				gene.calculateChangeOverCost()
				gene.calculateCost()				

				itemPositionsTab[item] += 1

				lastProducedGene = gene
				chromosome.genesByPeriod[period] = gene
				cost += gene.cost

		# print("after flash : ", chromosome.dnaArray)
		chromosome.cost = cost

	
	@classmethod
	def geneAtPeriod(cls, chromosome, period):
		"""
		"""

		item0 = chromosome.stringIdentifier[period] - 1

		for gene in chromosome.dnaArray[item0]:
			if gene.period == period:
				return gene

		return None
		

	@classmethod
	def feasible(cls, chromosome):
		"""Checks if a given dnaArray leads to a feasible chromosome
		"""

		# print("Not feasible : ", chromosome, chromosome.dnaArray)

		# going through the zipped dna array checking : ->
		# indices = []
		for item in range(InputDataInstance.instance.nItems):
			demands = InputDataInstance.instance.demandsArrayZipped[item]
			prods = chromosome.dnaArray[item]

			if len(demands) != len(prods): # -> that the number of produced item meets the number of demand
				print("Not feasible Reason 1", chromosome, chromosome.dnaArray)
				return False

			for j, demand in enumerate(demands):
				gene = prods[j]

				if gene is None: # -> that item production index is a very period and there's no duplicate value
					print("Not feasible Reason 2", chromosome, chromosome.dnaArray)
					return False

				prevItemProdPeriod = (0 if j == 0 else (prods[j - 1]).period) # -> that previous period where the item has bee produced is always less than the current one
				if (prevItemProdPeriod > gene.period):
					print("Not feasible Reason 3", chromosome, chromosome.dnaArray, gene.period)
					return False

				if gene.period > demand: # checks that the item is produced before its demand period
					print("Not feasible Reason 4", chromosome, chromosome.dnaArray, InputDataInstance.instance.demandsArrayZipped)
					return False

				# indices.append(prodIndex)

		return True


	@classmethod
	def geneLowerUpperLimit(cls, chromosome, gene):
	    """
	    """
	    
	    geneLowerLimit = 0 if gene.position == 0 else (chromosome.dnaArray[gene.item][gene.position - 1]).period + 1
	    geneUpperLimit = InputDataInstance.instance.demandsArrayZipped[gene.item][gene.position] + 1 if gene.position == len(InputDataInstance.instance.demandsArrayZipped[gene.item]) - 1 else ((chromosome.dnaArray[gene.item][gene.position + 1]).period if (chromosome.dnaArray[gene.item][gene.position + 1]) is not None else InputDataInstance.instance.demandsArrayZipped[gene.item][gene.position] + 1)
	    geneUpperLimit = InputDataInstance.instance.demandsArrayZipped[gene.item][gene.position] + 1 if InputDataInstance.instance.demandsArrayZipped[gene.item][gene.position] + 1 < geneUpperLimit else geneUpperLimit

	    return geneLowerLimit, geneUpperLimit


	@classmethod
	def nextProdGene(cls, prodPeriod, dnaArray, stringIdentifier):
		"""
		"""

		# print("nextProdGene : ", prodPeriod, chromosome.stringIdentifier[prodPeriod + 1:])
		for index, item in enumerate(stringIdentifier[prodPeriod + 1:]):
			if item != 0:
				period = (prodPeriod + 1) + index
				item0 = item - 1
				for geneA in dnaArray[item0]:
					if geneA is not None and geneA.period == period:
						# print('next ', geneA)
						return geneA
		
		# print('next None')
		return None

	@classmethod
	def prevProdGene(cls, prodPeriod, dnaArray, stringIdentifier):
		"""
		"""

		# print("nextProdGene : ", prodPeriod, chromosome.stringIdentifier[prodPeriod + 1:])
		for index, item in enumerate(reversed(stringIdentifier[:prodPeriod])):
			if item != 0:
				period = (prodPeriod - 1) - index
				item0 = item - 1
				for geneA in dnaArray[item0]:
					if geneA.period == period:
						# print('next ', geneA)
						return geneA
		
		# print('next None')
		return None


	@classmethod
	def createFromIdentifier(cls, stringIdentifier):
		"""
		"""

		chromosome = Chromosome()
		chromosome.stringIdentifier = stringIdentifier

		prevGene = None
		producedItemsCount = [0 for _ in range(InputDataInstance.instance.nItems)]
		cost = 0
		for period, periodValue in enumerate(stringIdentifier):
			if int(periodValue) > 0:
				item = int(periodValue) - 1
				position = producedItemsCount[item]

				gene = Gene(item, period, position, prevGene)
				gene.calculateStockingCost()
				gene.calculateChangeOverCost()
				gene.calculateCost()

				if prevGene is not None:
					(chromosome.dnaArray[prevGene[0]][prevGene[1]]).nextGene = (item, position)

				cost += gene.cost
				chromosome.dnaArray[item][position] = gene
				chromosome.genesByPeriod[period] = gene
				prevGene = item, position
				producedItemsCount[item] += 1

		chromosome.cost = cost
		# print("test : ", chromosome.dnaArray)
		return chromosome


	def __lt__(self, chromosome):
		return self.cost < chromosome.cost

	def __repr__(self):
		return "{} : {}".format(self.stringIdentifier, self.cost)
		# return "{} : {} | {}".format(self.stringIdentifier, self.cost, self.dnaArray)
		# return "{} : {} | {} - {} /".format(self.renderDnaArray(), self.cost, Chromosome.calculateCostPlainDNA(Chromosome.classRenderDnaArray(self.dnaArray), InputDataInstance.instance), Chromosome.feasible(self.dnaArray, InputDataInstance.instance))

	def __eq__(self, chromosome):
		return self.stringIdentifier == chromosome.stringIdentifier

	def __hash__(self) -> int:
		return hash(self.stringIdentifier)