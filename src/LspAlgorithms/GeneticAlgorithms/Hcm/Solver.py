#!/usr/bin/python3.5
# -*-coding: utf-8 -*

import random
from threading import Thread
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspInputDataReading.LspInputDataInstance import InputDataInstance
from ParameterSearch.ParameterData import ParameterData
from ..PopInitialization.PopInitializer import PopInitializer


class GeneticAlgorithm:
	"""
	"""

	#	Class' variables
	# nbMainThreads = 2
	# nbSlavesThread = 2
	# nbTrials = 3

	# Builder
	def __init__(self, inputDataInstance):
		"""
		"""

		self.inputDataInstance = inputDataInstance
		self.popInitializer = PopInitializer(self.inputDataInstance)
		self.elites = []
		self.generationIndex = 0


	def process(self, threadIndex, population):
		"""
		"""

		# Making up the initial population
		# population.setElites()
		# self.elites = population.elites

		while not(self.stopConditionMet(population)):
			# if self.generationIndex == 1:
			# 	break

			index_I = random.randint(0, (len(population.chromosomes) - 1))
			chromosome = population.chromosomes[index_I]
			population.chromosomes[index_I] = Chromosome.localSearch(chromosome.dnaArrayZipped, InputDataInstance.instance)

			population = population.evolve()
			print(population)

			# making up the new elite group
			# elites = self.elites + population.elites
			# elites.sort()
			
			# nElites = int(float(len(population.chromosomes)) * ParameterData.instance.elitePercentage)
			# nElites = (1 if nElites < 1 else nElites)
			# self.elites = elites[:nElites]
			
			self.generationIndex += 1

			

	def solve(self):
		"""
		"""

		populations = self.popInitializer.process()
		
		threads = []
		for i in range(ParameterData.instance.nPrimaryThreads):
			thread_T = Thread(target=self.process, args=(i, populations[i]))
			thread_T.start()
			thread_T.join()
			threads.append(thread_T)

	
	def stopConditionMet(self, population):
		"""
		"""
		return population.converged()