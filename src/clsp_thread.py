#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from population import *

#--------------------
# Class : PopInitializerThread
# author : Tafsir GNA
# purpose : Describing the structure of an instance to the algorithm
#--------------------

class ClspThread(Thread):

	def __init__(self, threadId, root):
		Thread.__init__(self)
		self.threadId = threadId
		self.setName = "Thread - " + str(threadId)
		self.root = root
		self.population = Population()
		self.thread_memory = []
		self.locker = 0

	def run(self):

		self.initPopulation()
		self.population.thread_memory = self.thread_memory

		self.startingPopulation = copy.copy(self.population)
		self.population.startingPopulation = self.startingPopulation

		# After the initial population has been created, i launch the search process
		i = 0
		while len(self.thread_memory) < 3 :

			#print ("Population : ", i, self.population)

			if self.population.NbPopulation == 0 or self.population.NbPopulation == 1:
				print("the thread has exited !")
				return

			if i == 100:
				break 

			population = Population()
			population.initialize(copy.copy(self.population), self.locker)
			self.population = copy.copy(population)

			#print "Current population : ", self.population.chromosomes , self.population.NbPopulation

			i += 1

		
	def initPopulation(self):
		
		currentNode = copy.copy(self.root)
		queue = []
		#print(self.name)

		while True:

			if currentNode.isLeaf():

				c = Chromosome(list(currentNode.solution))
				#c.getFeasible()
				c.advmutate()

				#print("Leaf : ", c)

				# Get lock to synchronize threads
				#self.initializerThreadsLock.acquire()

				if c not in self.population.chromosomes:
					self.population.chromosomes.append(c)
					self.population.NbPopulation += 1

				# i store the value of the highest value of the objective function
				value = c.fitnessValue
				if value > self.population.max_fitness:
					self.population.max_fitness = value

				# i want to store the best chromosome of the population
				if value < self.population.min_fitness:
					self.population.min_fitness = value
					self.population.elite = copy.copy(c)

				# i check that the size of the population don't exceed the maximum number of population retained
				if self.population.NbPopulation >= Population.NbMaxPopulation:

					# Free lock to release next thread
					#self.initializerThreadsLock.release()	
					self.population.getFitnessData()
					#print ("End ", self.population)
					return

				# Free lock to release next thread
				#self.initializerThreadsLock.release()				

			else:

				#print ("current Node : ", currentNode)

				nextItem = 0
				nextPeriod = 0

				# i produce the successors of this current node
				if currentNode.currentPeriod < len(Chromosome.problem.deadlineDemandPeriods[currentNode.currentItem-1]):

					nextItem = currentNode.currentItem
					nextPeriod = currentNode.currentPeriod + 1

				elif currentNode.currentItem < Chromosome.problem.nbItems:

					nextItem = currentNode.currentItem + 1
					nextPeriod = 1

				if nextItem != 0:

					period = Chromosome.problem.deadlineDemandPeriods[nextItem-1][nextPeriod-1]

					#if self.threadId == 1:
					#	print("p", nextItem, nextPeriod, period)

					i = 0
					zeroperiods = []
					while i <= period:

						if currentNode.solution[i] == 0 : 
							zeroperiods.append(i)

						i += 1

					nbZeroPeriods = len(zeroperiods)

					i = 0
					while i < nbZeroPeriods:

						solution = list(currentNode.solution)
						del solution[zeroperiods[i]]
						solution.insert(zeroperiods[i],nextItem)

						nextNode = Node()
						nextNode.currentItem = nextItem
						nextNode.currentPeriod = nextPeriod
						nextNode.solution = solution

						#print ("childNode : ", nextNode)

						queue.append(copy.copy(nextNode))

						i += 1

			sizeQueue = len(queue)
			if sizeQueue == 0:
				self.population.getFitnessData()
				#print ("End ", self.population)
				return

			currentNode = copy.copy(queue[sizeQueue-1])
			del queue[sizeQueue-1]


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
