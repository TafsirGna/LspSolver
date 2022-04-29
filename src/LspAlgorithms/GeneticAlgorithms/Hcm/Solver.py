#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from threading import Thread
import threading
import uuid
from LspAlgorithms.GeneticAlgorithms.PopulationEvaluator import PopulationEvaluator
from LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData
from ..PopInitialization.PopInitializer import PopInitializer


class GeneticAlgorithm:
	"""
	"""


	def __init__(self):
		"""
		"""

		self.popInitializer = PopInitializer()
		self.generationIndex = 0
		self.eliteLock = threading.Lock()



	def process(self, population):
		"""
		"""
		threadUUID = uuid.uuid4()
		generationIndex = 0
		popEvaluator = PopulationEvaluator()
		population.threadId = threadUUID

		while popEvaluator.evaluate(population) != "TERMINATE":
			# if generationIndex == 1:
			# 	break

			# self.setElites(population)

			population = population.evolve()

			LspRuntimeMonitor.output("Population --> " + str(population))
			
			generationIndex += 1



	def solve(self):
		"""
		"""

		populations = self.popInitializer.process()
		
		threads = []
		# for i in range(ParameterData.instance.nPrimaryThreads):
		for population in populations:
			thread_T = Thread(target=self.process, args=(population,))
			thread_T.start()
			threads.append(thread_T)

		[thread_T.join() for thread_T in threads]

		# print("Result : ", result)
