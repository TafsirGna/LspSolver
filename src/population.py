#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from clsp_ga_library import *
from chromosome import *

class Population:

	NbMaxPopulation = 0
	FITNESS_PADDING = 0
	crossOverRate = 0
	ga_memory = []
	startingPopulation = []
	stopFlag = []
	limitNbConsecutiveBadChromosomes = 0
	NbPopInitializerThreads = 1

	# builder 
	def __init__(self, previousPopulation = []):
		
		self.chromosomes = []
		self.max_fitness = 0
		self.min_fitness = pow(10,6)
		self.NbPopulation = 0
		self.listFitnessData = []
		self.sumAllFitnessValues = 0
		self.elite = []
		self.lacksDiversity = False

		# i explicit the case where there's no previous population before this one
		if previousPopulation == [] :

			listItems = []
			self.NbPopulation = 0

			item = 1
			period = Chromosome.problem.deadlineDemandPeriods[item-1][0]

			listThreads = []
			initializerThreadsLock = threading.Lock()
			i = 0
			while i <= period:

				# i initialize the node from which the search of each thread will start
				root = Node()
				root.currentItem = 1
				root.currentPeriod = 1

				j = 0
				while j < Chromosome.problem.nbTimes:
					if j == i:
						root.solution.append(1)
					else:
						root.solution.append(0)
					j += 1

				#print(root)

				# i initialize the thread and put it into a list of threads created for this purpose
				initializerThread = PopInitializerThread(i,copy.copy(root), self, initializerThreadsLock)
				listThreads.append(copy.copy(initializerThread))
				(listThreads[i]).start()

				i += 1

			
			# Wait for all threads to complete
			for thread in listThreads:
				thread.join()
			
			self.getFitnessData()
			
		else:

			# i select the two chromosomes that'll be mated to produce offsprings
			#print " population 1 : ", previousPopulation#, " starting with :", Population.startingPopulation

			# In the case where there's a lack of diversity, i introduce a bit of diversity by flipping a gene of one chromosome in the population
			
			if previousPopulation.NbPopulation == 0:
				del Population.stopFlag[0]
				Population.stopFlag.insert(0, True)
				return

			if previousPopulation.lacksDiversity:

				#print(" CONVERGENCE !!!")
				chromosome = copy.deepcopy(previousPopulation.chromosomes[0])
				
				# i store this local optima in the genetic algorithm's memory to remind it that it's already visit the solution
				if chromosome not in Population.ga_memory:
					Population.ga_memory.append(copy.deepcopy(chromosome))

				chromosome.advmutate()
				
				if chromosome != previousPopulation.chromosomes[0]:
					del previousPopulation.chromosomes[0]
					previousPopulation.chromosomes.insert(0, chromosome)
					#print (" different !")

				else:  

					#print(" from start to now!")
					#print " not different ! 1 ", Population.startingPopulation 
					i = 0
					while i < Population.startingPopulation.NbPopulation:

						if chromosome == Population.startingPopulation.chromosomes[i]:
							del Population.startingPopulation.chromosomes[i]

							# i decrease the number of the chromosomes of the population
							Population.startingPopulation.NbPopulation -= 1

							break
						i+=1

					#print " not different ! 2 ", Population.startingPopulation
					previousPopulation = copy.deepcopy(Population.startingPopulation)

				previousPopulation.getFitnessData() # i make calculations over the resulting population
				previousPopulation.getElite()

			#print(" Memory : ", Population.ga_memory)
				
			self.NbPopulation = previousPopulation.NbPopulation

			if previousPopulation.NbPopulation == 1:
				del Population.stopFlag[0]
				Population.stopFlag.insert(0, True)
				return

			#print " population 2 : ", previousPopulation #, " starting with :", Population.startingPopulation
			#print " Percentage : ", previousPopulation.listFitnessData

			# i perform the roulette-wheel method to select the parents
			chromosomes = []
			chromosomes.append(previousPopulation.elite) # i add the best chromosome of the previous population to the current population

			i = 1
			while i < previousPopulation.NbPopulation:

				rand_prob1 = randint(1,99)
				rand_prob2 = randint(1,99)

				#print(" rand 1 : ", rand_prob1, " rand_prob2 : ", rand_prob2)
				j = 0
				lbound = 0
				while j < previousPopulation.NbPopulation:
					if (rand_prob1 >= lbound and rand_prob1 <= previousPopulation.listFitnessData[j]):
						chromosome1 = previousPopulation.chromosomes[j]
					if (rand_prob2 >= lbound and rand_prob2 <= previousPopulation.listFitnessData[j]):
						chromosome2 = previousPopulation.chromosomes[j]
					lbound = previousPopulation.listFitnessData[j]
					j += 1

				#print("Parent 1 : ", chromosome1, "Parent 2 : ", chromosome2)

				chromosome3,chromosome4 = self.applyCrossOverto(chromosome1,chromosome2)

				#print("Child 3 : ", chromosome3, " Child 4 : ", chromosome4)

				# In the following lines, i intend to select the best two chromosomes out of both the parents and the generated offsprings
				tempList = []
				tempList.append(chromosome1)  
				tempList.append(chromosome2)
				tempList.append(chromosome3)
				tempList.append(chromosome4)

				chromosome3, chromosome4 = getBestChroms(tempList)

				#print(" Resulting Child 3 : ", chromosome3, " Resulting Child 4 : ", chromosome4)

				#if self.isFeasible(chromosome3) is False or self.isFeasible(chromosome4) is False:
				#	print("c3 : ", c3, " c4 : ", c4)

				if chromosome3 not in Population.ga_memory:
					chromosomes.append(chromosome3)
					i += 1

				if (i == self.NbPopulation):
					break

				if chromosome4 not in Population.ga_memory:
					chromosomes.append(chromosome4)
					i += 1

				if (i == self.NbPopulation):
					break

			#print("Population inter : ", chromosomes)
			#print(" ")

			self.chromosomes = []
			self.max_fitness = 0

			i = 0
			while i < self.NbPopulation:
				chromosome = chromosomes[i]
				chromosome.mutate()

				#if chromosome.fitnessValue == 0:
				#	print(" Chromosome : ", chromosome.solution, chromosome.itemsRank)

				if chromosome not in Population.ga_memory:
					self.chromosomes.append(chromosome)
				else:
					self.chromosomes.append(chromosomes[i])

				#if chromosome.fitnessValue == 375 and chromosome.solution != [0, 2, 2, 2, 3, 1, 0, 1]:
				#	print("1 : ", chromosome.solution, chromosome.fitnessValue )

				value = chromosome.fitnessValue
				if value > self.max_fitness:
					self.max_fitness = value

				# i want to store the best chromosome of the population
				if value < self.min_fitness:
					self.min_fitness = value
					self.elite = copy.deepcopy(chromosome)

				#print("Population {0} :".format(i), self.population[i], " Iteration : ", it)
				i+=1	

			#print " population 3 : ", self #, " starting with :", Population.startingPopulation
			#print " "
		# When the entire population has been formed, then i compute some statistic data on the given population
		self.getFitnessData()	

			#print("Population Suite {0} : ".format(it), self.population )
			#print(" ")

	#--------------------
	# function : applyCrossOverto
	# Class : GeneticAlgorithm
	# purpose : Applying cross-over to two chromosomes given as parameters and returning the resulting chromosomes
	#--------------------

	def applyCrossOverto(self, chromosome1, chromosome2):

		solution3 = []
		solution4 = []

		if (randint(0,100) < (Population.crossOverRate*100)):

			# i retrieve a table that stores the period each item has been manufactered for
			ranks1 = chromosome1.itemsRank
			ranks2 = chromosome2.itemsRank

			ranks3 = []
			ranks4 = []

			randomIndice = randint(1,Chromosome.problem.nbTimes-1)

			#print(" ")

			#print(" 1 - solution1 : ", chromosome1.solution, " ranks1 : ", chromosome1.itemsRank, " solution2 : ", chromosome2.solution, " ranks2 : ", chromosome2.itemsRank)
			#print(" randomIndice : ", randomIndice)
			#print(" ranks1 : ", ranks1, " ranks2 : ", ranks2)

			
			solution3 = chromosome1.solution[:randomIndice]
			solution4 = chromosome2.solution[:randomIndice]

			ranks3 = ranks1[:randomIndice]
			ranks4 = ranks2[:randomIndice]


			solution3 += chromosome2.solution[randomIndice:]
			solution4 += chromosome1.solution[randomIndice:]

			ranks3 += ranks2[randomIndice:]
			ranks4 += ranks1[randomIndice:]

			# Once, the two resulting chromosomes have been formed, i make each of them feasible with regards of the constraints

			#print(" randomIndice : ", randomIndice)
			#print(" 2 - solution3 : ", solution3, " ranks3 : ", ranks3, " solution4 : ", solution4, " ranks4 : ", ranks4)

			chromosome3 = Chromosome(solution3, ranks3)
			chromosome3.getFeasible()
			#chromosome3.advmutate()

			'''
			if chromosome3.fitnessValue == 0:
				print(" 1 - solution1 : ", chromosome1.solution, " ranks1 : ", chromosome1.itemsRank, " solution2 : ", chromosome2.solution, " ranks2 : ", chromosome2.itemsRank)
				print(" randomIndice : ", randomIndice)
				print(" 2 - solution3 : ", solution3, " ranks3 : ", ranks3)
				print(" result 3 :", chromosome3.solution)
			'''

			chromosome4 = Chromosome(solution4, ranks4)
			chromosome4.getFeasible()
			#chromosome4.advmutate()

			'''
			if chromosome4.fitnessValue == 0:
				print(" 1 - solution1 : ", chromosome1.solution, " ranks1 : ", chromosome1.itemsRank, " solution2 : ", chromosome2.solution, " ranks2 : ", chromosome2.itemsRank)
				print(" randomIndice : ", randomIndice)
				print(" solution4 : ", solution4, " ranks4 : ", ranks4)
				print(" result 4 :", chromosome4.solution)
			'''

			#print(" 2 - solution3 : ", chromosome3.solution, " ranks3 : ", ranks3, " solution4 : ", chromosome4.solution, " ranks4 : ", ranks4)

		else:
			chromosome3 = Chromosome(chromosome1.solution)
			chromosome4 = Chromosome(chromosome2.solution)

		return chromosome3,chromosome4

	def __repr__(self):
		
		#print("Nb : ", self.NbPopulation, self.chromosomes)
		result = ""
		i = 0
		while i < self.NbPopulation:

			c = self.chromosomes[i]
			result += str(c.solution) + " : " + str(c.fitnessValue) + ","

			i+=1

		return result

	def getFitnessData(self):

		self.sumAllFitnessValues = 0
		tmpSumFitness = 0 #variable used to quantify the lack of diversity in the population
		self.listFitnessData = []

		i = 0
		while i < self.NbPopulation:
			#print(" i : ", i)
			chromosome = self.chromosomes[i]
			temp = chromosome.fitnessValue

			value = (self.max_fitness-temp)
			tmpSumFitness += value

			value += Population.FITNESS_PADDING
			self.listFitnessData.append(value)
			self.sumAllFitnessValues += value

			i += 1

		#print(" Fitness Data 1 : ", self.listFitnessData)

		if tmpSumFitness == 0:
			self.lacksDiversity = True

		i = 0
		percentage = 0
		while i < self.NbPopulation:
			temp = self.listFitnessData[i]
			del self.listFitnessData[i]
			if self.sumAllFitnessValues == 0:
				percentage = 0
			else:
				percentage += (float(temp)/float(self.sumAllFitnessValues))*100
			#print (" FOO : temp : ", temp, " sumFitness : ", sumFitness, " percentage : ", percentage)
			self.listFitnessData.insert(i, percentage)
			i += 1

		#print(" Fitness Data 2 : ", self.listFitnessData)
		
	def getElite(self):
		
		self.min_fitness = pow(10,6)
		for chromosome in self.chromosomes:
			value = chromosome.fitnessValue
			if value < self.min_fitness:
				self.min_fitness = value
				self.elite = chromosome

	
	def searchEachPermutation(self, listPermutations, initializerThreadsLock):

		nbConsecutiveBadChromosomes = 0
		while True:

			j = 0
			nbPermutations = len(listPermutations)
			while j < nbPermutations:

				permutationJ = listPermutations[j] 
				#print(" - ", i, " permutation : ", permutationJ)

				# i create a chromosome and fill it with some zeros
				solution = []
				k = 0
				while k < Chromosome.problem.nbTimes:
					solution.append(0)
					k+=1

				qual_sol = True # boolean variable that determines if the chromosome being formed is good or not

				k = 0
				while k < Chromosome.problem.nbItems:

					itemK = permutationJ[k]
					itemKDemandPeriods = Chromosome.problem.deadlineDemandPeriods[itemK-1]

					l = 0
					size_itemKDemandPeriods = len(itemKDemandPeriods)
					while l < size_itemKDemandPeriods:

						periodL = itemKDemandPeriods[l]

						m = 0
						zeroperiods = []
						while m <= periodL:

							if solution[m] == 0 : 
								zeroperiods.append(m)

							m+=1

						nbZeroPeriods = len(zeroperiods)
						if nbZeroPeriods == 0:
							qual_sol = False
							break
						else:
							random_indice = randint(0, nbZeroPeriods-1)
							del solution[zeroperiods[random_indice]]
							solution.insert(zeroperiods[random_indice],itemK)

						l+=1

					k+=1

					if qual_sol is False:
						break

				j+=1

				c = Chromosome(solution)
				if qual_sol is True:

					nbConsecutiveBadChromosomes = 0

					c.getFeasible()
					c.advmutate() # i want to get the best chromosome out of this one by applying a slight mutation to this
					# TODO get back to advmutate()
					#c.mutate()

					# Get lock to synchronize threads
					initializerThreadsLock.acquire()

					if c not in self.chromosomes:
						self.chromosomes.append(c)
						self.NbPopulation += 1

					# Free lock to release next thread
					initializerThreadsLock.release()

					# i store the value of the highest value of the objective function
					value = c.fitnessValue
					if value > self.max_fitness:
						self.max_fitness = value

					# i want to store the best chromosome of the population
					if value < self.min_fitness:
						self.min_fitness = value
						self.elite = copy.deepcopy(c)

					# i check that the size of the population don't exceed the maximum number of population retained
					if self.NbPopulation >= Population.NbMaxPopulation:

						self.getFitnessData()	

						return

				else:
					# every time, we encounter a bad chromome with regards of our definition of bad chromosome, we increment the counter
					# and after a given number of bad consecutive chromosomes, the program know that any further good chromosomes cans be found
					nbConsecutiveBadChromosomes += 1

					if nbConsecutiveBadChromosomes == self.limitNbConsecutiveBadChromosomes:
						return

class Node:

	def __init__(self):

		self.solution = []
		self.currentItem = 0
		self.currentPeriod = 0

	def __repr__(self):
		return " Chromosome : " + str(self.solution) + " Current Item : " + str(self.currentItem) + " Current Period : " + str(self.currentPeriod)

	def isLeaf(self):
		
		if self.currentItem == Chromosome.problem.nbItems and self.currentPeriod == len(Chromosome.problem.deadlineDemandPeriods[self.currentItem-1]):
			return True
		return False
		
	
#--------------------
# Class : PopInitializerThread
# author : Tafsir GNA
# purpose : Describing the structure of an instance to the algorithm
#--------------------

class PopInitializerThread(Thread):

	def __init__(self, threadId, root, population, initializerThreadsLock):
		Thread.__init__(self)
		self.threadId = threadId
		self.root = root
		self.initializerThreadsLock = initializerThreadsLock
		self.population = population

	def run(self):
		
		currentNode = copy.copy(self.root)
		queue = []

		while True:

			if self.population.NbPopulation >= Population.NbMaxPopulation:
				return

			if currentNode.isLeaf():

				c = Chromosome(list(currentNode.solution))
				c.getFeasible()
				c.advmutate()

				#print("Leaf : ", c)

				# Get lock to synchronize threads
				self.initializerThreadsLock.acquire()

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
					self.population.elite = copy.deepcopy(c)

				# i check that the size of the population don't exceed the maximum number of population retained
				if self.population.NbPopulation >= Population.NbMaxPopulation:
					# Free lock to release next thread
					self.initializerThreadsLock.release()	
					return

				# Free lock to release next thread
				self.initializerThreadsLock.release()				

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
				break

			currentNode = copy.copy(queue[sizeQueue-1])
			del queue[sizeQueue-1]
			