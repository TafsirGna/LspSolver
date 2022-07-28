#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from collections import defaultdict
import concurrent.futures
import multiprocessing
from queue import Queue
import threading
import uuid
from LspAlgorithms.GeneticAlgorithms.GAOperators.LocalSearchEngine import LocalSearchEngine
from LspRuntimeMonitor import LspRuntimeMonitor
from ..PopInitialization.PopInitializer import PopInitializer
from ..PopInitialization.Population import Population
from ..Chromosome import Chromosome
from ..GAOperators.CrossOverOperator import CrossOverOperator
from ..GAOperators.MutationOperator import MutationOperator
from ParameterSearch.ParameterData import ParameterData


class GeneticAlgorithm:
	"""
	"""


	def __init__(self):
		"""
		"""

		self.popInitializer = PopInitializer()


	def process(self, primeThreadIdentifier):
		"""
		"""

		generationIndex = 0
		idleGenCounter = 0

		if LspRuntimeMonitor.popsData[primeThreadIdentifier] is None:
			LspRuntimeMonitor.popsData[primeThreadIdentifier] = {"min": [], "max": [], "mean": [], "std": []}

		while True:
			chromosomes = sorted(Chromosome.pool[primeThreadIdentifier]["content"].values())[:Population.popSizes[primeThreadIdentifier]]
			
			# check whether to stop or not
			if generationIndex == 2:
				break

			if generationIndex > 1 and chromosomes[0].cost != LspRuntimeMonitor.popsData[primeThreadIdentifier]["min"][-1]:
				idleGenCounter += 1

			if idleGenCounter == ParameterData.instance.nIdleGenerations:
				break


			# Stats
			LspRuntimeMonitor.popsData[primeThreadIdentifier]["min"].append(chromosomes[0].cost)

			# building population
			population = Population(primeThreadIdentifier, chromosomes)
			population.localSearch()

			# crossing over
			chromosomes = CrossOverOperator().process(population)
			population.chromosomes = chromosomes

			# applying mutation
			MutationOperator().process(population)

			LspRuntimeMonitor.output("Population --> " + str(population))

			generationIndex += 1
	

	def terminate(self, threadIdentifier):
		"""
		"""



	def solve(self):
		"""
		"""
		
		primeThreadIdentifiers = self.popInitializer.process()

		with concurrent.futures.ThreadPoolExecutor() as executor:
			print(list(executor.map(self.process, primeThreadIdentifiers)))

			
