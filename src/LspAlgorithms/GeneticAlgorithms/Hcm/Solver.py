#!/usr/bin/python3.5
# -*-coding: utf-8 -*

import random
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspInputDataReading.LspInputDataInstance import InputDataInstance
from ParameterSearch.ParameterData import ParameterData
from ..PopInitialization.PopInitializer import PopInitializer


class GeneticAlgorithm:
	"""
	"""

	#	Class' variables
	# FITNESS_PADDING = 1
	# NumberOfMigrants = 1
	# MigrationRate = 0 # this variable holds the number of generations needed before a migration occurs during the search
	# nbMainThreads = 2
	# nbSlavesThread = 2
	# nbTrials = 3

	# Builder
	def __init__(self, inputDataInstance):
		"""
		"""

		self.inputDataInstance = inputDataInstance
		self.popInitializer = PopInitializer()
		self.elites = []
		self.generationIndex = 0


	def solve(self):
		"""
		"""

		# Making up the initial population
		population = self.popInitializer.process(self.inputDataInstance)
		population.setElites()
		self.elites = population.elites

		while not(self.stopConditionMet(population)):
			# if self.generationIndex == 1:
			# 	break

			index_I = random.randint(0, (len(population.chromosomes) - 1))
			chromosome = population.chromosomes[index_I]
			# print("////////////////////", chromosome)
			population.chromosomes[index_I] = Chromosome.localSearch(chromosome.dnaArrayZipped, InputDataInstance.instance)

			population = population.evolve()
			print(population)

			# making up the new elite group
			elites = self.elites + population.elites
			elites.sort(key= lambda chromosome: chromosome.cost)
			
			nElites = int(float(len(population.chromosomes)) * ParameterData.instance.elitePercentage)
			nElites = (1 if nElites < 1 else nElites)
			self.elites = elites[:nElites]
			
			self.generationIndex += 1

	
	def stopConditionMet(self, population):
		"""
		"""
		return population.converged()