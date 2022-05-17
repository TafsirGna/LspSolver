#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from collections import defaultdict
import threading
import numpy as np
from LspAlgorithms.GeneticAlgorithms.Gene import Gene
from LspInputDataReading.LspInputDataInstance import InputDataInstance
import concurrent.futures

class Chromosome(object):

	pool = defaultdict(lambda: None) 

	def __init__(self):
		"""
		"""
		self.cost = 0
		self.dnaArray = [[None for _ in indices] for indices in InputDataInstance.instance.demandsArrayZipped]
		self.stringIdentifier = []
		

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
	def evaluateDnaArrayTask(cls, taskIndex, slices, arguments):
		"""
		"""

		cost = 0
		for index, gene in enumerate(slices[taskIndex]): 
			(arguments["chromosome"]).dnaArray[gene.item][gene.position] = gene
			if index > 0:
				gene.prevGene = ((slices[taskIndex][index-1]).item, (slices[taskIndex][index-1]).position)
				gene.calculateChangeOverCost()
			else:
				if taskIndex > 0:
					gene.prevGene = ((slices[taskIndex - 1][-1]).item, (slices[taskIndex - 1][-1]).position)
					gene.calculateChangeOverCost()
			gene.calculateCost()
			cost += gene.cost
			(arguments["chromosome"]).stringIdentifier[gene.period] = gene.item + 1

		with arguments["lock"]:
			(arguments["chromosome"]).cost += cost
		


	@classmethod
	def evaluateDnaArray(cls, dnaArray):
		"""
		"""

		genesList = sorted([gene for itemProdGenes in dnaArray for gene in itemProdGenes], key= lambda gene: gene.period)

		chromosome = Chromosome()
		chromosome.stringIdentifier = [0] * InputDataInstance.instance.nPeriods
		arguments = {"chromosome": chromosome, "lock": threading.Lock()}
		nThreads = 3
		# slices = [my_list[i:i + chunk_size] for i in range(0, len(my_list), chunk_size)]

		slices = np.array_split(genesList, nThreads)
		print("Slices : ", slices)
		with concurrent.futures.ThreadPoolExecutor() as executor:
			for index in range(nThreads):
				executor.submit(cls.evaluateDnaArrayTask, index, slices, arguments)
		
		chromosome.stringIdentifier = tuple(chromosome.stringIdentifier)
		return chromosome


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

				cost += gene.cost
				chromosome.dnaArray[item][position] = gene
				prevGene = item, position
				producedItemsCount[item] += 1

		chromosome.cost = cost
		# print("test : ", chromosome.dnaArray)
		return chromosome


	def __lt__(self, chromosome):
		return self.cost < chromosome.cost

	def __repr__(self):
		# return "{} : {}".format(Chromosome.classRenderDnaArray(self.dnaArray), self.cost)
		return "{} : {}".format(self.stringIdentifier, self.cost)
		# return "{} : {} | {} - {} /".format(self.renderDnaArray(), self.cost, Chromosome.calculateCostPlainDNA(Chromosome.classRenderDnaArray(self.dnaArray), InputDataInstance.instance), Chromosome.feasible(self.dnaArray, InputDataInstance.instance))

	def __eq__(self, chromosome):
		return self.stringIdentifier == chromosome.stringIdentifier

	def __hash__(self) -> int:
		return hash(self.stringIdentifier)