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

		while popEvaluator.evaluate(population) != "TERMINATE":
			# if generationIndex == 1:
			# 	break

			# self.setElites(population)

			population = population.evolve()

			LspRuntimeMonitor.output("Population --> " + str(population))

			# print("Uniiiiiiiiiiiiiques : ", population.uniques, "\n")
			
			generationIndex += 1



	def solve(self):
		"""
		"""

		populations = self.popInitializer.process()
		
		with concurrent.futures.ThreadPoolExecutor() as executor:
			for population in populations:
				executor.submit(self.process, population)
