#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from population import *
from clsp_slave_thread import *

#--------------------
# Class : ClspThread
# author : Tafsir GNA
# purpose : Describing the structure of an instance to the algorithm
#--------------------

class ClspThread(Thread):

	listMainThreads = 0
	NumberOfMigrants = 0
	NbGenToStop = 0

	def __init__(self, threadId, queue):

		Thread.__init__(self)
		self.threadId = threadId
		self.name = "Thread - " + str(threadId)
		self.queue = queue
		self.locker = threading.Lock()
		self.NbGenerations = 0

		self.immigrants = []

		self.slaveThreadsManager = SlaveThreadsManager(self) # i initialize a list that's intended to contain all the population's initialization threads 

		self.population = Population()
		self.population.slaveThreadsManager = self.slaveThreadsManager

	def run(self):
		
		self.slaveThreadsManager.initPop()
		#print (self.name, " ", "Initial Population : ", self.population)
		self.population.getImproved()
		self.population.getFitnessData()

		#print (self.name, " ", "Initial Population : ", self.population)

		# i send the best chromosomes of the population to its neighbors
		self.sendMigrants()

		if self.population.chromosomes == []:
			return

		# After the initial population has been created, i launch the search process
		i = 0
		nbIdleGen = 0
		while True:

			self.locker.acquire()
			if self.immigrants != []:
				for chromosome in self.immigrants:
					self.population.replace(chromosome)
				self.population.listFitnessData = []
				self.population.getFitnessData()
			self.immigrants = []
			self.locker.release()

			#print (self.name, " ", "Initial Population : " + str(i), self.population, " + ", self.population.listFitnessData)
			#print (" ")

			population = Population()
			population.initialize(self.population)

			if population.lacksDiversity:

				chromosome = copy.deepcopy(population.chromosomes[0])
			
				# i store this local optima in the genetic algorithm's memory to remind me that it's already been visited before
				Population.gaMemoryLocker.acquire()

				if chromosome not in Population.ga_memory:
					Population.ga_memory.append(copy.deepcopy(chromosome))
					
				Population.gaMemoryLocker.release()

				chromosome.advmutate()
				
				if chromosome == population.chromosomes[0]:

					print (self.name, " ", "Solution : ", chromosome)
					break

				else:

					population.chromosomes[0] = copy.deepcopy(chromosome)
					population.listFitnessData = []
					population.getFitnessData()
					self.sendMigrants()
			else:

				if (population.chromosomes[0]).fitnessValue >= (self.population.chromosomes[0]).fitnessValue:
					nbIdleGen += 1
				else:
					nbIdleGen == 0

				if nbIdleGen >= ClspThread.NbGenToStop:
					Population.gaMemoryLocker.acquire()
					if len(Population.ga_memory) >= 1:
						Population.gaMemoryLocker.release()
						break
					Population.gaMemoryLocker.release()

			self.population = population
			#if i == 7:
			#	break

			i += 1

		self.NbGenerations = i

	def initSearch(self, queue):
		
		queueSize = len(queue)
		currentNode = copy.deepcopy(queue[queueSize-1])
		del queue[queueSize-1]
		#print("Queue : ", self.queue)

		while True:

			if currentNode.isLeaf():

				c = Chromosome()
				c.init1(list(currentNode.solution), currentNode.fitnessValue)
				#c.advmutate()

				self.population.locker.acquire()
				if len(self.population.chromosomes) >= Population.NbMaxPopulation:
					self.population.locker.release()
					break
				if c not in self.population.chromosomes:
					self.population.chromosomes.append(copy.deepcopy(c))
				self.population.locker.release()

			else:

				#print ("current Node : ", currentNode)

				l = currentNode.getChildren()
				#print("Children : ", l)
				queue += l

			#print("inter : ", self.queue)
			queueSize = len(queue)
			if queueSize == 0:
				#if self.population.listFitnessData == []:
				#	self.population.getFitnessData()
				break
	
			currentNode = copy.copy(queue[queueSize-1])
			del queue[queueSize-1]


		#print (self.name, " ", "Initial Population : ", self.population)

	def sendMigrants(self):

		#self.locker

		if self.population.chromosomes != []:

			chromosomes = []
			i = 0
			while i < ClspThread.NumberOfMigrants:
				chromosomes.append(copy.deepcopy(self.population.chromosomes[i]))
				i += 1

			for thread in ClspThread.listMainThreads:
				if thread.getName() != self.name:
					thread.receiveMigrants(chromosomes)

	def receiveMigrants(self, chromosomes):
		self.locker.acquire()
		self.immigrants += chromosomes
		self.locker.release()