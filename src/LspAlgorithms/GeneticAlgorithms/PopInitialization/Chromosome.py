#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from collections import defaultdict
import threading
# import numpy as np
import copy
import math
from LspAlgorithms.GeneticAlgorithms.LspRuntimeMonitor import LspRuntimeMonitor
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Gene import Gene
from LspInputDataReading.LspInputDataInstance import InputDataInstance
import concurrent.futures
import bisect
from ParameterSearch.ParameterData import ParameterData

class Chromosome(object):

	pool = dict({"lock": threading.Lock(), "content": dict()})
	# localOptima = {"lock": threading.Lock(), "content": set()}
	popByThread = defaultdict(lambda: dict({"content": dict()}))

	def __init__(self):
		"""
		"""
		
		self.cost = 0
		self.dnaArray = [[None for _ in indices] for indices in InputDataInstance.instance.demandsArrayZipped]
		self.stringIdentifier = []
		self.genesByPeriod = defaultdict(lambda: None)
		# self.sortedGenesByCost = None


	@classmethod
	def distanceMeasure(cls, stringIdentifier, target):
		"""
		"""

		distance = 0
		itemGenesPositions = [0] * InputDataInstance.instance.nItems

		for period in range(InputDataInstance.instance.nPeriods):
			item = stringIdentifier[period] - 1

			if item >= 0:
				position = itemGenesPositions[item]
				distance += ((period - (target.dnaArray[item][position]).period) * InputDataInstance.instance.stockingCostsArray[item]) ** 2

				itemGenesPositions[item] += 1

		return math.sqrt(distance)

	@classmethod
	def gettingCloser(cls, chromosome, target, gene, altPeriod):
		"""
		"""

		# second calculus
		stringIdentifier = list(chromosome.stringIdentifier)
		stringIdentifier[gene.period], stringIdentifier[altPeriod] = stringIdentifier[altPeriod], stringIdentifier[gene.period]

		variance = Chromosome.distanceMeasure(chromosome.stringIdentifier, target)
		variance -= Chromosome.distanceMeasure(stringIdentifier, target)

		return (variance > 0)

	@classmethod
	def addToPop(cls, threadIdentifier, chromosome):
		"""
		"""

		if chromosome.stringIdentifier not in Chromosome.pool["content"]:
			Chromosome.popByThread[threadIdentifier]["content"][chromosome.stringIdentifier] = chromosome
			# TODO
			# with Chromosome.pool["lock"]:
			Chromosome.pool["content"][chromosome.stringIdentifier] = set({threadIdentifier})
		else:
			Chromosome.copyToThread(threadIdentifier, chromosome)


	@classmethod
	def copyToThread(cls, threadIdentifier, chromosome):
		"""
		"""
		if chromosome.stringIdentifier not in Chromosome.popByThread[threadIdentifier]["content"]:
			Chromosome.popByThread[threadIdentifier]["content"][chromosome.stringIdentifier] = chromosome
			with Chromosome.pool["lock"]:
				(Chromosome.pool["content"][chromosome.stringIdentifier]).add(threadIdentifier)

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

		print("creating from stringIdentifier : ", stringIdentifier)

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
				chromosome.genesByPeriod[period] = (gene.item, gene.position)
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