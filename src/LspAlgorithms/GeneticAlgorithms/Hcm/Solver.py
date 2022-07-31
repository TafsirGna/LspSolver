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
			chromosomes = {element["value"] for element in Chromosome.pool["content"].values() if element["threadId"] == primeThreadIdentifier}
			chromosomes = sorted(chromosomes)[:Population.popSizes[primeThreadIdentifier]]
			
			# check whether to stop or not
			# if generationIndex == 10:
			# 	break

			if generationIndex > 1:
				idleGenCounter = idleGenCounter + 1 if chromosomes[0].cost == LspRuntimeMonitor.popsData[primeThreadIdentifier]["min"][-1] else 1

			if idleGenCounter == ParameterData.instance.nIdleGenerations:
				break

			# building population
			population = Population(primeThreadIdentifier, chromosomes)
			
			if idleGenCounter > 1:
				population.localSearch()

			# Stats
			LspRuntimeMonitor.popsData[primeThreadIdentifier]["min"].append(chromosomes[0].cost)
			print("Miiiiiiiiiiiinnnnnnnnnnnn : ", chromosomes[0].cost, idleGenCounter)

			# crossing over
			chromosomes = CrossOverOperator().process(population)
			population.chromosomes = chromosomes

			# applying mutation
			# MutationOperator().process(population)

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

			
