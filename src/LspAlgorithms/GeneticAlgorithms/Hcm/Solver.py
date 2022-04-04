#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from ParameterSearch.ParameterData import ParameterData
from .MainThread import *
import math
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
	# pickeRandChromGens = 3

	# Builder
	def __init__(self, inputDataInstance):
		"""
		"""

		self.inputDataInstance = inputDataInstance
		self.popInitializer = PopInitializer()
		self.elites = []


	def solve(self):
		"""
		"""

		# Making up the initial population
		population = self.popInitializer.process(self.inputDataInstance)
		self.elites = population.elites

		# i = 0
		while not(self.stopConditionMet(population)):
			# if i == 1:
			# 	break

			population = population.evolve()
			# print(population)

			# making up the new elite group
			elites = self.elites + population.elites
			elites.sort(key= lambda chromosome: chromosome.cost)
			
			nElites = int(float(len(population.chromosomes)) * ParameterData.instance.elitePercentage)
			nElites = (1 if nElites < 1 else nElites)
			self.elites = elites[:nElites]
			
			# i += 1

	
	def stopConditionMet(self, population):
		"""
		"""
		return population.converged()





	# def printResults(self):

	# 	#print(self.ga_memory)
	# 	for thread in self.listMainThreads:
	# 		if not isinstance(thread.result, int):
	# 			chromosome = thread.result
	# 			#print()

	# 	for thread in self.listMainThreads:
	# 		if not isinstance(thread.result, int) and thread.result.fitnessValue < chromosome.fitnessValue:
	# 		#if thread.result.fitnessValue < chromosome.fitnessValue:
	# 			chromosome = thread.result
	# 		#print(" PRINTING : ", thread.result)

		
	# 	print("The best solution found so far is : ", chromosome.solution)
	# 	#print(self.population)
	# 	print("The fitness of this solution is : ", chromosome.fitnessValue)

	# 	# i print on the screen the number of generations, the program got through before quiting
	# 	sumNbGenerations = 0
	# 	for thread in self.listMainThreads:
	# 		sumNbGenerations += thread.NbGenerations

	# 	print("The average number of generations produced is : ", math.ceil(sumNbGenerations / (GeneticAlgorithm.nbMainThreads)))
