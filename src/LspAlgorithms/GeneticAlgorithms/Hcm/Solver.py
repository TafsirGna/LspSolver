#!/usr/bin/python3.5
# -*-coding: utf-8 -*

import concurrent.futures
import threading
import uuid
from LspAlgorithms.GeneticAlgorithms.PopulationEvaluator import PopulationEvaluator
from LspRuntimeMonitor import LspRuntimeMonitor
from ..PopInitialization.PopInitializer import PopInitializer


class GeneticAlgorithm:
	"""
	"""


	def __init__(self):
		"""
		"""

		self.popInitializer = PopInitializer()


	def process(self, population):
		"""
		"""

		threadUUID = uuid.uuid4()
		generationIndex = 0
		population.threadId = threadUUID
		popEvaluator = PopulationEvaluator()

		while popEvaluator.evaluate(population, generationIndex) != "TERMINATE":
			# if generationIndex == 10:
			# 	break

			population = population.evolve()

			LspRuntimeMonitor.output("Population --> " + str(population))
			
			generationIndex += 1


	def solve(self):
		"""
		"""

		populations = self.popInitializer.process()
		
		with concurrent.futures.ThreadPoolExecutor() as executor:
			print(list(executor.map(self.process, populations)))
			# for population in populations:
			# 	executor.submit(self.process, population)
