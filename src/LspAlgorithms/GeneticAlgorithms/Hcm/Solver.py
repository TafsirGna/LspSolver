#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from threading import Thread
import threading
from LspAlgorithms.GeneticAlgorithms.PopulationEvaluator import PopulationEvaluator
from ParameterSearch.ParameterData import ParameterData
from ..PopInitialization.PopInitializer import PopInitializer


class GeneticAlgorithm:
	"""
	"""


	def __init__(self, inputDataInstance):
		"""
		"""

		self.inputDataInstance = inputDataInstance
		self.popInitializer = PopInitializer(self.inputDataInstance)
		self.elites = []
		self.generationIndex = 0
		self.eliteLock = threading.Lock()


	def setElites(self, population):
		"""
		"""
		population.setElites()

		nElites = int(float(len(population.chromosomes)) * ParameterData.instance.elitePercentage) if len(self.elites) == 0 else len(self.elites)
		nElites = (1 if nElites < 1 else nElites)

		# making up the new elite group
		elites = self.elites + population.elites
		elites.sort()
		
		with self.eliteLock:
			self.elites = elites[:nElites]

		print("Elites --> ", self.elites)



	def process(self, threadIndex, population):
		"""
		"""
		generationIndex = 0
		popEvaluator = PopulationEvaluator()

		while popEvaluator.evaluate(population) != "TERMINATE":
			# if generationIndex == 1:
			# 	break

			# self.setElites(population)

			population = population.evolve()
			print("Population --> ", population)
			
			generationIndex += 1



	def solve(self):
		"""
		"""

		populations = self.popInitializer.process()
		
		threads = []
		for i in range(ParameterData.instance.nPrimaryThreads):
			thread_T = Thread(target=self.process, args=(i, populations[i]))
			thread_T.start()
			threads.append(thread_T)

		[thread_T.join() for thread_T in threads]

		# result = (min(self.elites)).cost
		# print("Result : ", result)
