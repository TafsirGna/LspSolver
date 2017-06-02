#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from clsp_ga_library import *
from population import *

#--------------------
# Class : SlaveThreadsManager
# author : Tafsir GNA
# purpose : Describing a the structure of a manager of slave threads that compute chromosomes for main threads and return the results
#--------------------

class SlaveThreadsManager:

	"""docstring for SlaveThreadsManager"""

	def __init__(self, mainThread, nbSlaveThreads):

		super(SlaveThreadsManager, self).__init__()
		self.listSlaveThreads = []
		self.nbSlaveThreads = nbSlaveThreads

		i = 0
		while i < nbSlaveThreads:
			
			slaveThread = SlaveThread(i, mainThread)
			slaveThread.queue = copy.deepcopy(mainThread.queue)

			if i != 0:
				slaveThread.mateDoneEvent = (self.listSlaveThreads[i-1]).doneEvent

			self.listSlaveThreads.append(slaveThread)

			i += 1

	def start(self):

		# i create the initial population
		self.initPop()

		pass

	def initPop(self):
		
		for thread in self.listSlaveThreads:

			thread.action = 0
			thread.start()
			thread.join()

		(self.listSlaveThreads[self.nbSlaveThreads-1]).doneEvent.wait()

		'''
		# i share out between all the threads including the main one the nodes in the queue
		queue = copy.deepcopy(self.mainThread.queue)
		self.mainThread.queue = []

		queueSize = len(queue)
		nodePerSlave = math.ceil(queueSize / self.nbSlaveThreads)
		#print(queueSize, " : ", nodePerSlave)
		
		i = 0
		slaveQueue = []
		counter = 0
		for node in queue:
			slaveQueue.append(node)
			i += 1
			if i == nodePerSlave:
				(self.listSlaveThreads[counter]).queue = copy.deepcopy(slaveQueue)
				slaveQueue = []
				counter += 1
				#print("ok")

		if slaveQueue != []:
			(self.listSlaveThreads[counter]).queue = copy.deepcopy(slaveQueue)
			#print("ok")

		for thread in self.listSlaveThreads:
			thread.action = 0 # i want to make the initial population
			thread.doneEvent.clear()
			
		for thread in self.listSlaveThreads:
			thread.run()
		
		(self.listSlaveThreads[self.nbSlaveThreads-1]).doneEvent.wait()
		'''

	def improvePop(self, chromosomes):

		popSize = len(chromosomes)
		nodePerSlave = math.ceil(popSize / self.nbSlaveThreads)

		i = 0
		slaveQueue = []
		counter = 0
		for chromosome in chromosomes:
			slaveQueue.append(chromosome)
			i += 1
			if i == nodePerSlave:
				(self.listSlaveThreads[counter]).queue = copy.deepcopy(slaveQueue)
				slaveQueue = []
				counter += 1

		if slaveQueue != []:
			(self.listSlaveThreads[counter]).queue = copy.deepcopy(slaveQueue)

		for thread in self.listSlaveThreads:
			thread.action = 1 # i want to improve the quality of the initial population
			thread.doneEvent.clear()
			
		for thread in self.listSlaveThreads:
			thread.run()
		
		(self.listSlaveThreads[self.nbSlaveThreads-1]).doneEvent.wait()

	def crossoverPop(self, population):

		for thread in self.listSlaveThreads:
			thread.action = 2 # i want to perform cross over between chromosomes of the current population
			thread.population = population
			thread.doneEvent.clear()
			
		for thread in self.listSlaveThreads:
			thread.run()
		
		(self.listSlaveThreads[self.nbSlaveThreads-1]).doneEvent.wait()		


class SlaveThread(Thread):

	def __init__(self, threadId, mainThread):

		Thread.__init__(self)
		self.queue = []
		self.threadId = threadId
		self.mainThread = mainThread
		self.action = -1
		self.doneEvent = Event()
		self.mateDoneEvent = 0
		self.population = 0

	def run(self):
		
		if self.action == 0 and self.queue != []: # if i want to initialize the first population

			self.mainThread.initSearch(self.queue)

		elif self.action == 1 and self.queue != []: # i want to improve the quality of the initial population

			for chromosome in self.queue:
				chromosome.advmutate()
				self.mainThread.population.replace(chromosome)

		elif self.action == 2 and self.queue != []:
			self.population.crossPopulation()

		if self.threadId != 0:
			self.mateDoneEvent.wait()
		self.doneEvent.set()