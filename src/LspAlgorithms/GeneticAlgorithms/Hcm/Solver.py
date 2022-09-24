#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from collections import defaultdict
import concurrent.futures
import multiprocessing
from queue import Queue
import threading
import uuid
from LspAlgorithms.GeneticAlgorithms.GAOperators.LocalSearchEngine import LocalSearchEngine
from LspAlgorithms.GeneticAlgorithms.LspRuntimeMonitor import LspRuntimeMonitor
from ..PopInitialization.PopInitializer import PopInitializer
from ..PopInitialization.Population import Population
from ..PopInitialization.Chromosome import Chromosome
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


	def applyGA(self, primeThreadIdentifiers):
		"""
		"""

		self.generationIndex = 0
		self.idleGenCounters = dict({primeThreadIdentifier: 1 for primeThreadIdentifier in primeThreadIdentifiers})

		while True:
			
			# check whether to stop or not
			# if self.generationIndex == 10:
			# 	break

			with concurrent.futures.ThreadPoolExecutor() as executor:
				print(list(executor.map(self.processGenPop, primeThreadIdentifiers)))

			print("ok 1")
			LspRuntimeMonitor.instance.output("Population --> " + str(Chromosome.pool["content"]))
			print("ok 2")

			# Determine if it's to be terminated or not
			terminate = True

			for idleGenCounter in self.idleGenCounters.values():
				if idleGenCounter < ParameterData.instance.nIdleGenerations:
					terminate = False
					break

			if terminate:
				break

			self.generationIndex += 1


	def processGenPop(self, primeThreadIdentifier):
		"""
		"""

		if self.idleGenCounters[primeThreadIdentifier] == ParameterData.instance.nIdleGenerations:
			return

		# building population
		population = Population(primeThreadIdentifier)

		if self.generationIndex > 1:
			self.idleGenCounters[primeThreadIdentifier] = self.idleGenCounters[primeThreadIdentifier] + 1 if population.chromosomes[0].cost == LspRuntimeMonitor.instance.popsData[primeThreadIdentifier]["min"][-1] else 1

		if self.idleGenCounters[primeThreadIdentifier] == ParameterData.instance.nIdleGenerations:
			return
		
		if self.idleGenCounters[primeThreadIdentifier] > 1:
			population.localSearch()

		# Stats
		LspRuntimeMonitor.instance.popsData[primeThreadIdentifier]["min"].append(population.chromosomes[0].cost)
		print("Miiiiiiiiiiiinnnnnnnnnnnn : ", population.chromosomes[0].cost, self.idleGenCounters[primeThreadIdentifier])

		# crossing over
		chromosomes = CrossOverOperator().process(population)
		population.chromosomes = chromosomes

		# applying mutation
		# MutationOperator().process(population)


	def terminate(self, threadIdentifier):
		"""
		"""
		pass


	def solve(self):
		"""
		"""
		
		primeThreadIdentifiers = self.popInitializer.process()

		self.applyGA(primeThreadIdentifiers)

			
