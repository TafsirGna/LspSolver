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
	nbSlavesThread = 0

	def __init__(self, threadId, queue):

		Thread.__init__(self)
		self.threadId = threadId
		self.name = "Thread - " + str(threadId)
		self.queue = queue

		self.thread_memory = []
		self.migrants = []
		self.slaveThreadsManager = SlaveThreadsManager(self, ClspThread.nbSlavesThread) # i initialize a list that's intended to contain all the population's initialization threads 

		self.population = Population()
		self.population.slaveThreadsManager = self.slaveThreadsManager

	def run(self):
		
		self.slaveThreadsManager.start()
		print (self.name, " ", "Initial Population : ", self.population)

		'''
		self.population.getImproved()
		self.population.getFitnessData()

		print (self.name, " ", "Initial Population : ", self.population)
		
		self.population.thread_memory = self.thread_memory
		self.population.startPopData = []
		self.population.startPopData.append(copy.deepcopy(self.population.chromosomes))
		self.population.startPopData.append(copy.deepcopy(self.population.listFitnessData))

		# i send the best chromosomes of the population to its neighbors
		self.sendMigrants()

		nbGenB4Stop = 0
		storedFitnessMean = 0

		# After the initial population has been created, i launch the search process
		i = 1
		indiceMigration = 0
		while len(self.thread_memory) <= 7:

			if self.migrants != []:
				for chromosome in self.migrants:
					self.population.replace(chromosome)
				self.population.listFitnessData = []
				self.population.getFitnessData()

			#print ("Thread : ", self.name, "Population : ", i, self.population.chromosomes, " and ", self.population.listFitnessData)
			#print("population : ", self.population.fitnessMean)

			if len(self.population.chromosomes) <= 1:
				#print("the thread ", self.name, " has exited!")
				break

			if i == 10:
				break 

			population = Population()
			retVal = population.initialize(indiceMigration, self.population)

			if retVal == 1: # this signals it's time for migration
				#print("Yo")
				self.sendMigrants()

			self.population = population

			#print ("Current population : ", self.population.chromosomes, " and ", self.population.listFitnessData)

			i += 1
		'''

	def initSearch(self, queue):
		
		queueSize = len(queue)
		currentNode = copy.deepcopy(queue[queueSize-1])
		del queue[queueSize-1]
		#print("Queue : ", self.queue)

		while True:

			if currentNode.isLeaf():

				c = Chromosome(list(currentNode.solution))
				c.advmutate()

				self.locker.acquire()
				self.locker.release()
				'''
				self.mainThread.meshThreadsManager.locker.acquire()
				if not self.mainThread.meshThreadsManager.contains(self._chromosome.solution):
					self.mainThread.meshThreadsManager.putInRank(self)
					self.mainThread.meshThreadsManager.locker.release()
					self.doneEvent.set()
					break
				self.mainThread.meshThreadsManager.locker.release()	
				'''
				break			

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
		self.migrants += chromosomes


	def putNextItem(self, nextItem, nextPeriod, nextItemCounter, currentNode, queue):

		period = Chromosome.problem.deadlineDemandPeriods[nextItem-1][nextPeriod-1]

		i = period
		childrenQueue = []

		while i >= 0:

			if currentNode.solution[i] == 0 : 

				solution = list(currentNode.solution)
				solution[i] = nextItem

				nextNode = Node()
				nextNode.currentItem = nextItem
				nextNode.currentPeriod = nextPeriod
				nextNode.solution = solution
				nextNode.itemCounter = nextItemCounter
				nextNode.fitnessValue = Node.evaluate(nextNode.solution)

				nbChildren = len(childrenQueue)

				#print("Child Node : ", nextNode)

				if (childrenQueue == []):

					childrenQueue.append(nextNode)
					#print(threadQueue)
			
				elif nbChildren == 1 and (childrenQueue[0]).fitnessValue == 0:

					childrenQueue.append(nextNode)
					#print(threadQueue)

				else:
					# i sort the list of zeroperiods from the most convenient place to the least convenient one
					prevValue = 0
					j = 0
					found = False
					while j < nbChildren:

						if nextNode.fitnessValue >= prevValue and nextNode.fitnessValue <= (childrenQueue[j]).fitnessValue:
							found = True
							childrenQueue = childrenQueue[:j] + [nextNode] + childrenQueue[j:]
							break

						prevValue = (childrenQueue[j]).fitnessValue

						j += 1

					if found is False:
						childrenQueue.append(nextNode)

			i -= 1

		#print("childrenQueue : ", list(reversed(childrenQueue)), "---")
		queue += list(reversed(childrenQueue))
		#print(self.queue, "---")