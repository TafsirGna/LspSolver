from collections import defaultdict
import threading
# import numpy as np
import copy
import math
from LspAlgorithms.GeneticAlgorithms.LspRuntimeMonitor import LspRuntimeMonitor
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Gene import Gene
from LspInputDataReading.LspInputDataInstance import InputDataInstance
from .PseudoChromosome import PseudoChromosome
import concurrent.futures
from ParameterSearch.ParameterData import ParameterData

class Chromosome(object):

	pool = None
	popByThread = None

	def __init__(self):
		"""
		"""
		
		self.cost = 0
		self.dnaArray = [[None for _ in indices] for indices in InputDataInstance.instance.demandsArrayZipped]
		self.stringIdentifier = []
		self.genesByPeriod = defaultdict(lambda: None)
		# self.sortedGenesByCost = None


	# @classmethod
	# def dumbDistanceMeasure(cls, stringIdentifier, target):
	# 	"""
	# 	"""

	# 	distance = 0
	# 	itemGenesPositions = [0] * InputDataInstance.instance.nItems

	# 	for period1 in range(InputDataInstance.instance.nPeriods):
	# 		item = stringIdentifier[period1] - 1

	# 		if item >= 0:
	# 			position = itemGenesPositions[item]
	# 			period2 = (target.dnaArray[item][position]).period
	# 			distance += ((period1 - period2) * InputDataInstance.instance.stockingCostsArray[item]) ** 2

	# 			itemGenesPositions[item] += 1

	# 	return math.sqrt(distance)


	@classmethod
	def distanceMeasure(cls, chromosomeInput, target, chromosome_distances_dict):
		"""
		"""

		distance = 0
		stringIdentifier = None

		if isinstance(chromosomeInput, PseudoChromosome):
			stringIdentifier = chromosomeInput.stringIdentifier
			itemPositions = [0] * InputDataInstance.instance.nItems
			for period, item in enumerate(stringIdentifier):
				if item > 0:
					item -= 1
					distance += ((period - (target.dnaArray[item][itemPositions[item]]).period) * InputDataInstance.instance.stockingCostsArray[item]) ** 2
					itemPositions[item] += 1

		elif isinstance(chromosomeInput, Chromosome):

			stringIdentifier = chromosomeInput.stringIdentifier
			for itemGenes in chromosomeInput.dnaArray:
				for gene in itemGenes:
					distance += ((gene.period - (target.dnaArray[gene.item][gene.position]).period) * InputDataInstance.instance.stockingCostsArray[gene.item]) ** 2

		else:
			stringIdentifier = chromosomeInput["stringIdentifier"]

			distance = chromosome_distances_dict[((chromosomeInput["chromosome"]).stringIdentifier, target.stringIdentifier)]
			distance = distance ** 2
			distance -= (((chromosomeInput["gene"]).period - (target.dnaArray[(chromosomeInput["gene"]).item][(chromosomeInput["gene"]).position]).period) * InputDataInstance.instance.stockingCostsArray[(chromosomeInput["gene"]).item]) ** 2
			distance += ((chromosomeInput["altPeriod"] - (target.dnaArray[(chromosomeInput["gene"]).item][(chromosomeInput["gene"]).position]).period) * InputDataInstance.instance.stockingCostsArray[(chromosomeInput["gene"]).item]) ** 2

			if (chromosomeInput["chromosome"]).stringIdentifier[chromosomeInput["altPeriod"]] != 0:
				distance -= ((chromosomeInput["altPeriod"] - (target.dnaArray[((chromosomeInput["chromosome"]).genesByPeriod[chromosomeInput["altPeriod"]])[0]][((chromosomeInput["chromosome"]).genesByPeriod[chromosomeInput["altPeriod"]])[1]]).period) * InputDataInstance.instance.stockingCostsArray[((chromosomeInput["chromosome"]).genesByPeriod[chromosomeInput["altPeriod"]])[0]]) ** 2
				distance += (((chromosomeInput["gene"]).period - (target.dnaArray[((chromosomeInput["chromosome"]).genesByPeriod[chromosomeInput["altPeriod"]])[0]][((chromosomeInput["chromosome"]).genesByPeriod[chromosomeInput["altPeriod"]])[1]]).period) * InputDataInstance.instance.stockingCostsArray[((chromosomeInput["chromosome"]).genesByPeriod[chromosomeInput["altPeriod"]])[0]]) ** 2
			
		result = math.sqrt(distance)

		chromosome_distances_dict[(stringIdentifier, target.stringIdentifier)] = result
		chromosome_distances_dict[(target.stringIdentifier, stringIdentifier)] = result

		return result

	@classmethod
	def gettingCloser(cls, chromosome, target, gene, altPeriod, chromosome_distances_dict):
		"""
		"""

		distance1 = 0
		if (chromosome.stringIdentifier, target.stringIdentifier) in chromosome_distances_dict:
			distance1 = chromosome_distances_dict[(chromosome.stringIdentifier, target.stringIdentifier)]
		else:
			distance1 = Chromosome.distanceMeasure(chromosome, target, chromosome_distances_dict)

		variance = distance1

		distance2 = 0

		stringIdentifier = list(chromosome.stringIdentifier)
		stringIdentifier[gene.period], stringIdentifier[altPeriod] = stringIdentifier[altPeriod], stringIdentifier[gene.period]
		stringIdentifier = tuple(stringIdentifier)

		if (stringIdentifier, target.stringIdentifier) in chromosome_distances_dict:
			distance2 = chromosome_distances_dict[(stringIdentifier, target.stringIdentifier)]
		else:
			chromosomeInput = {"stringIdentifier": stringIdentifier, "gene": gene, "altPeriod": altPeriod, "chromosome": chromosome}
			distance2 = Chromosome.distanceMeasure(chromosomeInput, target, chromosome_distances_dict)

		variance -= distance2

		return (variance >= 0)

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

	def __le__(self, chromosome):
		return self.cost <= chromosome.cost

	def __repr__(self):
		return "{} : {}".format(self.stringIdentifier, self.cost)
		# return "{} : {} | {}".format(self.stringIdentifier, self.cost, self.dnaArray)
		# return "{} : {} | {} - {} /".format(self.renderDnaArray(), self.cost, Chromosome.calculateCostPlainDNA(Chromosome.classRenderDnaArray(self.dnaArray), InputDataInstance.instance), Chromosome.feasible(self.dnaArray, InputDataInstance.instance))

	def __eq__(self, chromosome):
		return self.stringIdentifier == chromosome.stringIdentifier

	def __hash__(self) -> int:
		return hash(self.stringIdentifier)