#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from population import *

#--------------------
# Class : PopInitializerThread
# author : Tafsir GNA
# purpose : Describing the structure of an instance to the algorithm
#--------------------

class ClspThread(Thread):

	def __init__(self, threadId, root, slaveThreadsManager):
		Thread.__init__(self)
		self.threadId = threadId
		self.setName = "Thread - " + str(threadId)
		self.root = root
		self.population = Population()
		self.thread_memory = []
		self.slaveThreadsManager = slaveThreadsManager


	def run(self):

		self.initPopulation()

		
		self.population.thread_memory = self.thread_memory
		self.population.slaveThreadsManager = self.slaveThreadsManager
		self.population.startingPopulation = copy.copy(self.population)

		# After the initial population has been created, i launch the search process
		i = 0
		while len(self.thread_memory) < 7 :

			#print ("Population : ", i, self.population)

			if self.population.NbPopulation == 0 or self.population.NbPopulation == 1:
				print("the thread has exited !")
				return

			if i == 50:
				break 

			population = Population()
			population.initialize(copy.copy(self.population))
			self.population = copy.copy(population)
			#print ("yes", self.population)

			#print "Current population : ", self.population.chromosomes , self.population.NbPopulation

			i += 1
		

	def initPopulation(self):
		
		locker = threading.Lock()
		currentNode = copy.copy(self.root)
		queue = []
		#print(self.name)
		#nbInitialPopulation = 0

		while True:

			if currentNode.isLeaf():

				self.slaveThreadsManager.compute(self.population, locker, copy.copy(currentNode.solution))

				# Get lock to synchronize threads
				locker.acquire()	
				# i check that the size of the population don't exceed the maximum number of population retained
				if self.population.NbPopulation >= Population.NbMaxPopulation:
					break	

				# Free lock to release 
				locker.release()

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

					self.putNextItem(nextItem, nextPeriod, nextItemCounter, currentNode, queue)

			sizeQueue = len(queue)
			if sizeQueue == 0:
				break

			currentNode = copy.copy(queue[sizeQueue-1])
			del queue[sizeQueue-1]

		self.population.getFitnessData()
		print ("End ", self.population)


	#--------------------
	# function : handleTermination
	# Class : ClspThread
	# purpose : This prints the results of the search once the search has ended
	#--------------------
	def handleTermination(self):

		#print(self.ga_memory)
		self.bestSolution = self.ga_memory[0] # variable that holds the best solution found so far in the search

		for chromosome in self.ga_memory:
			if chromosome.fitnessValue < self.bestSolution.fitnessValue:
				self.bestSolution = chromosome

		print("The best solution found so far is : ", self.bestSolution.solution)
		#print(self.population)
		print("The fitness of this solution is : ", self.bestSolution.fitnessValue)

		#print(" Memory : ", self.ga_memory)
		#print(self.population)

	def sendMigrants():
		pass

	def putNextItem(self, nextItem, nextPeriod, nextItemCounter, currentNode, queue):

		#print ("putNextItem : solution : ", currentNode.solution)

		period = Chromosome.problem.deadlineDemandPeriods[nextItem-1][nextPeriod-1]

		#if self.threadId == 1:
		#	print("p", nextItem, nextPeriod, period)

		i = 0
		zeroperiods = []
		zeroperiodsCostTab = []
		while i <= period:


			if currentNode.solution[i] == 0 : 

				cost = Chromosome.getCostof(i, nextItem, nextPeriod, currentNode.solution)
				if zeroperiodsCostTab == [] or zeroperiods == []:

					zeroperiods.append(i)
					zeroperiodsCostTab.append(cost)

				else:
				# i sort the list of zeroperiods from the most convenient place to the least convenient one
					size = len(zeroperiodsCostTab)
					prevCost = 0
					j = 0
					while j < size:

						if cost >= prevCost and cost <= zeroperiodsCostTab[j]:

							zeroperiods = zeroperiods[:j] + [i] + zeroperiods[j:]
							zeroperiodsCostTab = zeroperiodsCostTab[:j] + [cost] + zeroperiodsCostTab[j:]
							break

						prevCost = zeroperiodsCostTab[j]

						j += 1

			i += 1

		#print ("putNextItem : zeroperiods : ", zeroperiods , ", zeroperiodsCostTab : ", zeroperiodsCostTab)
		nbZeroPeriods = len(zeroperiods)

		i = nbZeroPeriods - 1
		while i >= 0:

			#print (" zeroperiods i : " , zeroperiods[i])
			solution = list(currentNode.solution)
			del solution[zeroperiods[i]]
			solution.insert(zeroperiods[i],nextItem)

			nextNode = Node()
			nextNode.currentItem = nextItem
			nextNode.currentPeriod = nextPeriod
			nextNode.solution = solution
			nextNode.itemCounter = nextItemCounter

			#print ("childNode : ", nextNode)

			queue.append(copy.copy(nextNode))

			i -= 1
