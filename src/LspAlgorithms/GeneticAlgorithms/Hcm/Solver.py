#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from collections import defaultdict
import concurrent.futures
from queue import Queue
import threading
import uuid
from LspAlgorithms.GeneticAlgorithms.LocalSearch.LocalSearchEngine import LocalSearchEngine
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
		self.daemonThreads = defaultdict(lambda: None)
		self.dThreadPipelines = defaultdict(lambda: {"input": Queue(), "output": Queue()})
		self.popEvaluator = PopulationEvaluator()


	def daemonTask(self, mainThreadUUID):
		"""
		"""

		dThreadPipelines = self.dThreadPipelines[mainThreadUUID]

		while True:
			if not dThreadPipelines["input"].empty():
				chromosome = dThreadPipelines["input"].get()
				result = (LocalSearchEngine().process(chromosome, "positive_mutation"))
				dThreadPipelines["output"].put(result)


	def process(self, population):
		"""
		"""

		generationIndex = 0
		
		#
		dThreadPipelines = self.dThreadPipelines[population.lineageIdentifier]
		self.daemonThreads[population.lineageIdentifier] = threading.Thread(target=self.daemonTask, args=(population.lineageIdentifier,), daemon=True)
		# (self.daemonThreads[threadUUID]).start()
		
		population.dThreadOutputPipeline = dThreadPipelines["output"] 

		while self.popEvaluator.evaluate(population, dThreadPipelines["input"], generationIndex) != "TERMINATE":
			# if generationIndex == 1:
			# 	break

			population = population.evolve()

			LspRuntimeMonitor.output("Population --> " + str(population))
			
			generationIndex += 1

	# (self.daemonThreads[threadUUID]).

	def solve(self):
		"""
		"""

		populations = self.popInitializer.process()
		
		with concurrent.futures.ThreadPoolExecutor() as executor:
			print(list(executor.map(self.process, populations)))
