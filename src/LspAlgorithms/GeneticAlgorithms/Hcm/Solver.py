#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from collections import defaultdict
import concurrent.futures
# from LspAlgorithms.GeneticAlgorithms.GAOperators.LocalSearchEngine import LocalSearchEngine
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
		self.popChromosomes = defaultdict(lambda: set())


	def applyGA(self, primeThreadIdentifiers):
		"""
		"""

		self.generationIndex = 0
		self.idleGenCounters = dict({primeThreadIdentifier: 1 for primeThreadIdentifier in primeThreadIdentifiers})

		# Initializing this object's popChromosomes property
		for primeThreadIdentifier in primeThreadIdentifiers:
			self.popChromosomes[primeThreadIdentifier] = set((Chromosome.popByThread[primeThreadIdentifier]["content"]).values())

		while True:
			
			# check whether to stop or not
			if self.generationIndex == 30:
				break

			LspRuntimeMonitor.instance.newInstanceAdded = dict({primeThreadIdentifier: False for primeThreadIdentifier in primeThreadIdentifiers})

			with concurrent.futures.ThreadPoolExecutor() as executor:
				print(list(executor.map(self.processGenPop, primeThreadIdentifiers)))

			# check whether to stop the process or not
			if self.terminateProcess():
				break

			self.generationIndex += 1


	def processGenPop(self, primeThreadIdentifier):
		"""
		"""

		if self.idleGenCounters[primeThreadIdentifier] >= ParameterData.instance.nIdleGenerations:
			return

		# building population
		population = Population(primeThreadIdentifier, self.popChromosomes[primeThreadIdentifier])

		if self.generationIndex == 0:
			population.boostChampion()

		if self.generationIndex > 0:
			self.idleGenCounters[primeThreadIdentifier] = self.idleGenCounters[primeThreadIdentifier] + 1 if population.best.cost == LspRuntimeMonitor.instance.popsData[primeThreadIdentifier]["min"][-1] else 1

		# Stats
		LspRuntimeMonitor.instance.popsData[primeThreadIdentifier]["min"].append(population.best.cost)

		# crossing over
		CrossOverOperator().process(population)

		# applying mutation
		# MutationOperator().process(population)

		# if self.idleGenCounters[primeThreadIdentifier] > 1:
		# 	population.localSearch()

		# print("Miiiiiiiiiiiinnnnnnnnnnnn : ", population.chromosomes[0].cost, self.idleGenCounters[primeThreadIdentifier])

		self.popChromosomes[primeThreadIdentifier] = set(population.chromosomes)

		LspRuntimeMonitor.instance.output("Population --> " + str(population.chromosomes))


	def terminateProcess(self):
		"""
		"""

		# Second approach: Stop when no new instance
		added = False
		for newInst in LspRuntimeMonitor.instance.newInstanceAdded.values():
			if newInst:
				added = True 
				break
		
		if not added:
			return True

		# First approach: Stop when no new better instance
		# Determine if it's to be terminated or not
		# the process only stop when n generations have passed whithout any improvement to the quality of the best chromosome in the population
		for idleGenCounter in self.idleGenCounters.values():
			if idleGenCounter < ParameterData.instance.nIdleGenerations:
				return False
		return True

		

	def solve(self):
		"""
		"""
		
		# create the initial population
		primeThreadIdentifiers = self.popInitializer.process()

		# apply genetic algorithms to this initial population
		self.applyGA(primeThreadIdentifiers)
