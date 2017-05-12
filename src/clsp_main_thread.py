#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from population import *

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
		self.population = Population()
		self.thread_memory = []
		self.migrants = []

	def run(self):

		self.initPopulation()

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
		

	def initPopulation(self):
		
		queueSize = len(self.queue)
		currentNode = copy.copy(self.queue[queueSize-1])
		del self.queue[queueSize-1]
		#print("Queue : ", self.queue)

		while True:

			if currentNode.isLeaf():

				#print ("Leaf : ", currentNode.solution)
				# Get lock to synchronize threads
				self.population.locker.acquire()

				# i check that the size of the population don't exceed the maximum number of population considered
				if len(self.population.chromosomes) >= Population.NbMaxPopulation:
					if self.population.listFitnessData == []:
						self.population.getFitnessData()	
					self.population.locker.release()
					break	

				# Free lock to release 
				self.population.locker.release()

				Population.slaveThreadsManager.locker.acquire()
				Population.slaveThreadsManager.handle(self.population, list(currentNode.solution))
				Population.slaveThreadsManager.locker.release()

			else:

				#print ("current Node : ", currentNode)

				nextItem = 0
				nextPeriod = 0
				nextItemCounter = 0

				# i produce the successors of this current node
				if currentNode.currentPeriod < len(Chromosome.problem.deadlineDemandPeriods[currentNode.currentItem-1]):

					nextItem = currentNode.currentItem
					nextPeriod = currentNode.currentPeriod + 1
					nextItemCounter = currentNode.itemCounter

				elif currentNode.itemCounter < Chromosome.problem.nbItems:

					nextItem = currentNode.currentItem + 1
					if nextItem == Chromosome.problem.nbItems + 1:
						nextItem = 1
					nextPeriod = 1
					nextItemCounter = currentNode.itemCounter + 1

				if nextItem != 0:

					self.putNextItem(nextItem, nextPeriod, nextItemCounter, currentNode)
					#print(self.queue)

			#print("inter : ", self.queue)
			queueSize = len(self.queue)
			if queueSize == 0:
				if self.population.listFitnessData == []:
					self.population.getFitnessData()
				break
	
			currentNode = copy.copy(self.queue[queueSize-1])
			del self.queue[queueSize-1]

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

	def putNextItem(self, nextItem, nextPeriod, nextItemCounter, currentNode):

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
				nextNode.fitnessValue = ClspThread.evaluate(nextNode.solution)

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
		self.queue += list(reversed(childrenQueue))
		#print(self.queue, "---")

	
	def evaluate(cls, sol):
			
		solution = list(sol)

		fitnessValue = 0
		grid = Chromosome.problem.chanOverGrid

		# Calculation of all the change-over costs
		
		i = 1
		tmp = solution[0]
		while i < Chromosome.problem.nbTimes :

			n = solution[i]

			if (tmp == 0):
				i+=1
				tmp = n
			else:
				
				if (n != 0):
					if (n != tmp):
						fitnessValue += int((grid[tmp-1])[n-1])
						tmp = n
				else:
					tmp = solution[i-1]

					j=i
					while j < Chromosome.problem.nbTimes and solution[j] == 0:
						j+=1
					i=j-1
				
				i+=1

		#print(" intermediary cost : ", self._fitnessValue)
		# Calculation of the sum of holding costs

		itemCounter = [0] * Chromosome.problem.nbItems

		i = 0
		while i < Chromosome.problem.nbTimes:

			item = solution[i]

			if item != 0:

				counter = itemCounter[item - 1] + 1
				itemCounter[item - 1] = counter
				fitnessValue += int(Chromosome.problem.holdingGrid[item-1]) * (Chromosome.problem.deadlineDemandPeriods[item-1][counter-1] - i)

			i += 1

		return fitnessValue

	evaluate = classmethod(evaluate)