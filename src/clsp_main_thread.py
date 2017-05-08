#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from population import *

#--------------------
# Class : ClspThread
# author : Tafsir GNA
# purpose : Describing the structure of an instance to the algorithm
#--------------------

class ClspThread(Thread):

	def __init__(self, threadId, queue, slaveThreadsManager, neighbours):
		Thread.__init__(self)
		self.threadId = threadId
		self.name = "Thread - " + str(threadId)
		self.queue = queue
		self.population = Population()
		self.thread_memory = []
		self.slaveThreadsManager = slaveThreadsManager
		self.neighbours = neighbours
		#print(self.queue)

	def run(self):

		self.initPopulation()
		
		self.population.thread_memory = self.thread_memory
		self.population.slaveThreadsManager = self.slaveThreadsManager

		self.population.startPopData = []
		self.population.startPopData.append(copy.deepcopy(self.population.chromosomes))
		self.population.startPopData.append(copy.deepcopy(self.population.listFitnessData))

		# After the initial population has been created, i launch the search process
		i = 0
		while len(self.thread_memory) <= 7:

			#print ("Thread : ", self.name, "Population : ", i, self.population.chromosomes, " and ", self.population.listFitnessData)

			if len(self.population.chromosomes) <= 1:
				#print("the thread ", self.name, " has exited!")
				break

			if i == 10:
				break 

			population = Population()
			population.initialize(self.population)
			self.population = population
			#print("yes", self.population)

			#print ("Current population : ", self.population.chromosomes, " and ", self.population.listFitnessData)

			i += 1
		

	def initPopulation(self):
		
		locker = threading.Lock()
		queueSize = len(self.queue)
		currentNode = copy.copy(self.queue[queueSize-1])
		del self.queue[queueSize-1]
		#print("Queue : ", self.queue)

		while True:

			if currentNode.isLeaf():

				# Get lock to synchronize threads
				locker.acquire()
				# i check that the size of the population don't exceed the maximum number of population considered
				if len(self.population.chromosomes) >= Population.NbMaxPopulation:
					if self.population.listFitnessData == []:
						#print("Hoo 1")
						self.population.getFitnessData()	
					locker.release()
					break	

				# Free lock to release 
				locker.release()

				self.slaveThreadsManager.compute(self.population, locker, list(currentNode.solution))

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

		print (self.name, " ", "Initial Population : ", self.population)


	def sendMigrants():
		pass

	def putNextItem(self, nextItem, nextPeriod, nextItemCounter, currentNode):

		period = Chromosome.problem.deadlineDemandPeriods[nextItem-1][nextPeriod-1]

		i = period
		childrenQueue = []

		while i >= 0:

			if currentNode.solution[i] == 0 : 

				solution = list(currentNode.solution)
				del solution[i]
				solution.insert(i, nextItem)

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
				del itemCounter[item - 1]
				itemCounter.insert(item - 1, counter)
				fitnessValue += int(Chromosome.problem.holdingGrid[item-1]) * (Chromosome.problem.deadlineDemandPeriods[item-1][counter-1] - i)

			i += 1

		return fitnessValue

	evaluate = classmethod(evaluate)