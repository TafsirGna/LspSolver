#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from multiprocessing import Event
from threading import *
from ..Chromosome import *

#--------------------
# Class : SlaveThreadsManager
# author : Tafsir GNA
# purpose : Describing a the structure of a manager of slave threads that compute chromosomes for main threads and return the results
#--------------------

class SlaveThreadsManager:

	"""docstring for SlaveThreadsManager"""
	nbSlavesThread = 0

	def __init__(self, mainThread):

		super(SlaveThreadsManager, self).__init__()
		self.listSlaveThreads = []
		self.mainThread = mainThread
		self.currentSlaveThreadId = 0

		i = 0
		while i < SlaveThreadsManager.nbSlavesThread:
			
			slaveThread = SlaveThread(i, mainThread)
			#slaveThread.queue = copy.deepcopy(mainThread.queue)

			if i != 0:
				slaveThread.mateDoneEvent = (self.listSlaveThreads[i-1]).doneEvent

			self.listSlaveThreads.append(slaveThread)

			i += 1

	def initSlaveThread(self, queue):
		
		(self.listSlaveThreads[self.currentSlaveThreadId]).action = 0
		(self.listSlaveThreads[self.currentSlaveThreadId]).queue = queue
		(self.listSlaveThreads[self.currentSlaveThreadId]).start()
		self.currentSlaveThreadId += 1

	def crossoverPop(self):
		for thread in self.listSlaveThreads:
			thread.action = 2 # i want to perform cross over between chromosomes of the current population
			thread.doneEvent.clear()
			
		for thread in self.listSlaveThreads:
			thread.run()
		
		(self.listSlaveThreads[SlaveThreadsManager.nbSlavesThread-1]).doneEvent.wait()		


class SlaveThread(Thread):

	def __init__(self, threadId, mainThread):

		Thread.__init__(self)
		self.queue = []
		self.threadId = threadId
		self.mainThread = mainThread
		self.action = -1
		self.doneEvent = Event()
		self.mateDoneEvent = 0

	def run(self):
		
		if self.action == 0 and self.queue != []: # if i want to initialize the first population

			#print("slave : ", self.queue)
			self.mainThread.initSearch(self.queue, "slave")
			self.queue = []
	
		elif self.action == 2:
			self.mainThread.crossPopulation()

		if self.threadId != 0:
			self.mateDoneEvent.wait()
		self.doneEvent.set()

		'''
		elif self.action == 1 and self.queue != []: # i want to improve the quality of the initial population

			for chromosome in self.queue:
				chromosome.advmutate()
				self.mainThread.replace(chromosome)

			#self.mainThread.population.chromosomes.sort()
			self.queue = []
		'''