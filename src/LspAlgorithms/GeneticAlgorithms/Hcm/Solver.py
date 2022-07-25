#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from collections import defaultdict
import concurrent.futures
import multiprocessing
from queue import Queue
import threading
import uuid
from LspAlgorithms.GeneticAlgorithms.GAOperators.LocalSearchEngine import LocalSearchEngine
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
		# Creating a deamon thread to perform local search
		self.popEvaluator = PopulationEvaluator()


	def process(self, population):
		"""
		"""

		generationIndex = 0

		while self.popEvaluator.evaluate(population, generationIndex) != "TERMINATE":
			# if generationIndex == 3:
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

			
