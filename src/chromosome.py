#!/usr/bin/python3.5
# -*-coding: utf-8 -*

from clsp_ga_library import *

class Chromosome(object):

	mutationRate = 0
	problem = 0
	hashTable = {}

	# Builder 
	def __init__(self):

		# Variables
		self._solution = []
		self._itemsRank = []
		self._fitnessValue = 0
		self.itemsRankFlag = False
		self._hashSolution = ""
		self.manufactItemsPeriods = getManufactPeriodsGrid(Chromosome.problem.nbItems, Chromosome.problem.deadlineDemandPeriods) #Chromosome.problem.manufactItemsPeriods 

	def init1(self, solution, fitnessValue = 0):
		self._solution = list(solution)
		self._get_hashSolution()

		if fitnessValue == 0:
			if self.hashSolution not in Chromosome.hashTable:
				self._fitnessValue = Node.evaluate(self._solution)
			else:
				hashTableData = Chromosome.hashTable[self.hashSolution]
				self._fitnessValue = hashTableData[0]
		else:
			self._fitnessValue = fitnessValue

		self._get_itemsRanks()

	def init2(self, solution, itemsRank):
		self._solution = list(solution)
		self._itemsRank = list(itemsRank)

		self.getFeasible()

		if self.hashSolution not in Chromosome.hashTable:
			self._fitnessValue = Node.evaluate(self._solution)
		else:
			hashTableData = Chromosome.hashTable[self.hashSolution]
			self._fitnessValue = hashTableData[0]

		# TODO
		self._get_itemsRanks()

	def __lt__(self, chromosome):
		return self._fitnessValue < chromosome.fitnessValue

	# Getters

	def _get_fitnessValue(self):
		return self._fitnessValue

	def _get_solution(self):
		return self._solution

	def _get_itemsRanks(self):

		#if self.itemsRankFlag is False:

		if self.hashSolution not in Chromosome.hashTable:

			if self.itemsRankFlag is False:

				self._itemsRank = []
				gridCounters = [1] * Chromosome.problem.nbItems
				#print("grid : ", gridCounters)

				i = 0 
				while i < Chromosome.problem.nbTimes:

					if self._solution[i] != 0:

						item = self._solution[i]
						counter = gridCounters[item-1]
						self._itemsRank.append(counter)

						# then, i increment the counter of this item
						gridCounters[item-1] = (counter+1)

					else:
						self._itemsRank.append(0)

					i+=1

				self.itemsRankFlag = True

				hashTableData = []
				hashTableData.append(self.fitnessValue)
				hashTableData.append(self._itemsRank)
				Chromosome.hashTable[self.hashSolution] = list(hashTableData)

		else:

			hashTableData = Chromosome.hashTable[self.hashSolution]
			self._itemsRank = hashTableData[1]

		return self._itemsRank

	def _get_hashSolution(self):

		if self._hashSolution == "":

			i = 0
			while i < Chromosome.problem.nbTimes:
				self._hashSolution += str(self._solution[i])
				i+=1
			
		return self._hashSolution


	# Setters

	def _set_hashSolution(self, new_value):
		self._hashSolution = new_value

	def _set_itemsRanks(self, new_value):
		self._itemsRank = new_value

	def _set_solution(self, new_solution):
		self._solution = new_solution

	def _set_fitnessValue(self, new_value):
		self._fitnessValue = new_value

	def __repr__(self):
		return " {} : {} ".format(self._solution,self.fitnessValue)

	def __eq__(self, chromosome):
		return self._solution == chromosome.solution

	def __ne__(self, chromosome):
		return self._solution != chromosome.solution
	
	# Genetic operators and other function

	def isFeasible(self):

		# i check first that there's not shortage or backlogging
		i = 0
		feasible = False
		while i < Chromosome.problem.nbItems:

			itemDemandPeriods = Chromosome.problem.deadlineDemandPeriods[i]

			itemManufactPeriods = getManufactPeriods(self._solution,i+1)

			if (len(itemManufactPeriods) != len(itemDemandPeriods)):
				return False
			else:
				j = 0
				nbitemManufactPeriods = len(itemManufactPeriods)
				while j < nbitemManufactPeriods:

					if (itemManufactPeriods[j] > itemDemandPeriods[j]):
						return False

					j+=1

				feasible = True

			i+=1

		if feasible:
			#print("Feasible True")
			return True
		#print("Feasible False")
		return False

	#--------------------
	# function : mutate
	# Class : Chromosome
	# purpose : Applying mutation to a given chromosome and returning the resulting one
	#--------------------

	def mutate(self):

		#print("M Start : ", self._solution)
		saved_solution = self._solution
		saved_fitnessValue = self._fitnessValue

		if (randint(0,100) < (Chromosome.mutationRate*100)): # then the chromsome has been selected for mutation 

			mutated = False

			while mutated is False:

				randomIndice = randint(0,(Chromosome.problem.nbTimes-1))

				item1 = self._solution[randomIndice]

				# i make sure that the randomIndice variable never corresponds to a zero indice
				while item1 == 0:
					randomIndice = randint(0,(Chromosome.problem.nbTimes-1))
					# i get the item corresponding the gene to be flipped
					item1 = self._solution[randomIndice]

				#print(" randomIndice : ", randomIndice)

				visitedItems = []

				i = randomIndice-1
				itemsRank = self.itemsRank
				while i >= 0:
					if self._solution[i] != item1 and self._solution[i] != 0:

						item2 = self._solution[i]
						#print(" item2 : ", item2)

						if item2 not in visitedItems:

							visitedItems.append(item2)

							item2DemandPeriod = Chromosome.problem.deadlineDemandPeriods[item2-1][itemsRank[i]-1]

							if item2DemandPeriod >= randomIndice:
								#print(i, randomIndice)
								solution = switchGenes(self._solution, randomIndice, i)
								c = Chromosome()
								c.init1(solution)
								self._solution = c.solution
								self._fitnessValue = c.fitnessValue
								self._hashSolution = c.hashSolution
								self._itemsRank = c.itemsRank
								self.manufactItemsPeriods = list(c.manufactItemsPeriods)
								mutated = True
								break
					i-=1

				# if the first approach doesn't work ,then i apply another one in order to leave the current chromosome actually mutated

				if mutated is False:

					visitedItems = []

					i = randomIndice + 1
					while i < Chromosome.problem.nbTimes:

						if self._solution[i] != item1 and self._solution[i] != 0:

							item2 = self._solution[i]

							if item2 not in visitedItems:

								item1DemandPeriod = Chromosome.problem.deadlineDemandPeriods[item1-1][itemsRank[randomIndice]-1]

								if item1DemandPeriod >= i:
									#print(i, randomIndice)
									solution = switchGenes(self._solution, randomIndice, i)
									c = Chromosome()
									c.init1(solution)
									self._solution = c.solution
									self._fitnessValue = c.fitnessValue
									self._hashSolution = c.hashSolution
									self._itemsRank = c.itemsRank
									self.manufactItemsPeriods = list(c.manufactItemsPeriods)
									mutated = True
									break					

						i += 1
			

		#print("F Start : ", self._solution)

	# TODO Revamp advmutate function as function mutate is

	def advmutate(self):

		solution1 = list(self._solution)
		itemsRank1 = self.itemsRank
		resultingChromosomes = []

		i = 0
		while i < Chromosome.problem.nbTimes:

			if solution1[i] != 0:

				item1 = solution1[i]
				item2 = 0

				item1DemandPeriod = Chromosome.problem.deadlineDemandPeriods[item1-1][itemsRank1[i]-1]
				j = item1DemandPeriod
				solution2 = []
				while j >= 0:

					if solution1[j] != 0 and solution1[j] != item1:

						item2 = solution1[j]
						item2DemandPeriods = Chromosome.problem.deadlineDemandPeriods[item2-1]
						#print(" item's rank value : ", itemsRank[j], " j : ", j)
						if item2DemandPeriods[itemsRank1[j]-1] >= i and item1DemandPeriod >= j :
							solution2 = switchGenes(solution1, j, i)
							# TODO
							itemsRank2 = switchGenes(itemsRank1, j, i)									
							
							c = Chromosome()
							c.init1(solution2)
							if c.fitnessValue < self.fitnessValue:
								self._solution = c.solution
								self._itemsRank = c.itemsRank
								self._fitnessValue = c.fitnessValue
								self._hashSolution = c.hashSolution
					
					'''
					if solution1[j] == 0:
						solution2 = switchGenes(solution1, j, i)
						# TODO
						itemsRank2 = switchGenes(itemsRank1, j, i)

						c = Chromosome()
						c.init1(solution2)
						if c.fitnessValue < self.fitnessValue:
							self._solution = c.solution
							self._itemsRank = c.itemsRank
							self._fitnessValue = c.fitnessValue
							self._hashSolution = c.hashSolution
					'''

					j-=1

			i+=1

	def getFeasible(self):

		#print(" In Chromosome 1 : ", self._solution)
		#print(self._solution)

		#if self.isFeasible() is False:

		#print(" grid : ", grid)
		copy_solution = list(self._solution)

		# i make sure that the number of goods producted isn't superior to the number expected
		i = 0
		while i < Chromosome.problem.nbTimes:

			if self._solution[i] != 0:

				item = self._solution[i]
				#print(" ok : ", self._solution, self._itemsRank)
				#print(" item picked : ", item)
				rank = self._itemsRank[i]
				#print(i, item-1, rank-1, self.manufactItemsPeriods)
				value = self.manufactItemsPeriods[item-1][rank-1]

				if value == -1:
					itemDemandPeriods = self.manufactItemsPeriods[item-1]
					itemDemandPeriods[rank-1] = i
					#print(" It isn't yet in the tab")
					#print(" == -1 ", item, i, rank)

				else:

					#print(" != -1 ", item, i, rank)
					#print(" It is already in the tab")
					cost1 = Chromosome.getCostof(value, item, rank, copy_solution, i)
					cost2 = Chromosome.getCostof(i, item, rank, copy_solution, value)

					#print(" cost 1 : ", cost1, " cost2 : ", cost2)
					if cost2 < cost1 :
						itemDemandPeriods = self.manufactItemsPeriods[item-1]
						itemDemandPeriods[rank-1] = i

						#print(" cost2 < cost1 : ", value, item)
						self._solution[value] = 0

					else:
						self._solution[i] = 0
			i+=1

		#print(" in middle getFeasible : ", self._solution, ", ", self._itemsRank)
		#print()
		# i make sure that the number of items producted isn't inferior to the number expected
		i = 0
		while i < Chromosome.problem.nbItems:

			j = 0
			nbmanufactItemsPeriods = len(self.manufactItemsPeriods[i])
			while j < nbmanufactItemsPeriods:

				if self.manufactItemsPeriods[i][j] == -1:
					if j == 0:
						lbound = 0
					else:
						lbound = self.manufactItemsPeriods[i][j-1]
					
					zeroperiods = []
					k = lbound+1
					while k <= Chromosome.problem.deadlineDemandPeriods[i][j]:
						if self._solution[k] == 0:
							zeroperiods.append(k)
						k+=1

					#print("zeroperiods : ", zeroperiods)
					nbZeroPeriods = len(zeroperiods)

					if nbZeroPeriods > 0:

						cost1 = Chromosome.getCostof(zeroperiods[0], i+1, j+1, copy_solution)
						#print(" cost1 : ", cost1 )

						k = 1 
						indice = zeroperiods[0]
						while k < nbZeroPeriods:
							cost2 = Chromosome.getCostof(zeroperiods[k], i+1, j+1, copy_solution)
							#print(" cost2 : ", cost2 , zeroperiods[k])
							if cost2 < cost1:
								#print(" cost2 < cost1 : ", cost1 , cost2 )
								indice = zeroperiods[k]
							k+=1

						self._solution[indice] = i+1

						itemDemandPeriods = self.manufactItemsPeriods[i]
						itemDemandPeriods[j] = indice

					else:
						
						# experimental code 

						# if there's no place to put this item, then i check all the other times in order to put this item there
						
						lbound = 0
						p = 1
						for deadline in Chromosome.problem.deadlineDemandPeriods[i]:

							zeroperiods = []
							k = lbound
							while k <= deadline:
								if self._solution[k] == 0:
									zeroperiods.append(k)
								k += 1
							lbound = deadline + 1

							nbZeroPeriods = len(zeroperiods)
							if nbZeroPeriods > 0:

								cost1 = Chromosome.getCostof(zeroperiods[0], i+1, p, copy_solution)
								#print(" cost1 : ", cost1 )

								k = 1 
								indice = zeroperiods[0]
								while k < nbZeroPeriods:
									cost2 = Chromosome.getCostof(zeroperiods[k], i+1, p, copy_solution)
									#print(" cost2 : ", cost2 , zeroperiods[k])
									if cost2 < cost1:
										#print(" cost2 < cost1 : ", cost1 , cost2 )
										indice = zeroperiods[k]
									k+=1

								self._solution[indice] = i+1

								itemDemandPeriods = self.manufactItemsPeriods[i]
								itemDemandPeriods[j] = indice

								break
							p += 1


				j+=1
			i+=1

	def getCostof(cls, indice, item, rank,solution, secondIndice = -1):

		solution = list(solution)

		if secondIndice != -1:
			solution[secondIndice] = 0

		cost = 0
		# stocking cost 
		deadline = cls.problem.deadlineDemandPeriods[item-1][rank-1]
		cost += (deadline - indice)* int(Chromosome.problem.holdingGrid[item-1])

		#print(" cost 1 : ", cost)

		# change-over cost 
		nItem, nIndice = nextPeriodItemOf(indice, solution)
		#print(" nItem : ", nItem, " nIndice : ", nIndice)
		if nItem != 0:
			cost += int(Chromosome.problem.chanOverGrid[item-1][nItem-1])

		#print(" cost 2 : ", cost)

		pItem, pIndice = previousPeriodItemOf(indice, solution)
		#print(" pItem : ", pItem, " pIndice : ", pIndice, " solution : ", solution)
		if pItem != 0:
			cost += int(Chromosome.problem.chanOverGrid[pItem-1][item-1])

		#print(" cost 3 : ", cost)

		return cost

	# Class' methods
	getCostof = classmethod(getCostof)

	# Properties
	solution = property(_get_solution,_set_solution)
	fitnessValue = property(_get_fitnessValue,_set_fitnessValue)
	itemsRank = property(_get_itemsRanks, _set_itemsRanks)
	hashSolution = property(_get_hashSolution, _set_hashSolution) 


class Node(object):

	def __init__(self):

		self._solution = []
		self._currentPeriod = 0
		self.fitnessValue = 0
		self.tab = []

		# i make calculations over the number of zero that gonna be in a string of a chromosome.
		nbZero = Chromosome.problem.nbTimes
		for deadlines in Chromosome.problem.deadlineDemandPeriods:
			nbZero -= len(deadlines)
		tabZero = [0] * nbZero
		self.tab += copy.deepcopy(Chromosome.problem.deadlineDemandPeriods)
		self.tab.append(tabZero)

	def __repr__(self):
		return "Chromosome : " + str(self._solution) + ", " + str(self.fitnessValue) +  ", " + str(self._currentPeriod) + ", " + str(self.tab) + ";" 
		#" Current Item : " + str(self.currentItem) + " Current Period : " + str(self.currentPeriod) + " Item Counter : " + str(self.itemCounter) + " Fitness value : " + 

	def isLeaf(self):
		
		if self._currentPeriod == Chromosome.problem.nbTimes:
			return True
		return False

	def isGood(self):
		
		for deadlines in self.tab:
			if deadlines != []:
				return False
		return True
		

	def getChildren(self):

		# first, i check if the node that i have to get the children from, is available for.
		ok = True
		i = 0
		while i < len(self.tab) - 1:
			deadlines = self.tab[i]
			if deadlines != [] and deadlines[0] <= self.currentPeriod - 1:
				ok = False
				break
			i += 1
		#print ("log getChildren : ", nextNode, " : ", ok) 
		if not ok : 
			return []

		nextPeriod = self._currentPeriod + 1
		#print("nextPeriod : ", nextPeriod, len(self.tab))
		childrenQueue = []

		# i take into account the fact that the value of a gene can be zero
		if self.tab[len(self.tab)-1] != []:

			#print("yes")
			solution = list(self.solution)
			solution[nextPeriod - 1] = 0
			nextNode = copy.deepcopy(self)
			nextNode.currentPeriod = nextPeriod
			nextNode.solution = solution
			tempTab = copy.deepcopy(self.tab)
			del tempTab[Chromosome.problem.nbItems][0]
			nextNode.tab = copy.deepcopy(tempTab)

			# Before putting this nodes in the queue, i check that there's still places for the other products
			#print ("log getChildren 1 : ", nextNode)
			childrenQueue.append(copy.deepcopy(nextNode))
			#print ("log getChildren 2 : ", childrenQueue, nextNode.tab, " : ", nextNode.currentPeriod) 
		#print("cool")
		i = 0
		while i < len(self.tab) - 1:
			#print ("log getChildren 1 : ", self.tab[i], " : ", i)
			if self.tab[i] != []:
				#print ("i : ", i , self.tab[i], self.tab[i][0])
				solution = list(self.solution)
				solution[nextPeriod - 1] = i + 1

				nextNode = copy.deepcopy(self)
				nextNode.currentPeriod = nextPeriod
				nextNode.solution = solution
				tempTab = copy.deepcopy(self.tab)
				del tempTab[i][0]
				nextNode.tab = copy.deepcopy(tempTab)

				#print("nextNode : ", nextNode)
				# Before putting this nodes in the queue, i check that there's still places for the other products
				#print ("log getChildren 1 : ", nextNode) 
				childrenQueue.append(copy.deepcopy(nextNode))
				
			i += 1

		#print("childrenQueue : ", list(reversed(childrenQueue)), "---")
		childrenQueue.sort()
		return list(reversed(childrenQueue))
		#return list(childrenQueue)
		#print(self.queue, "---")
	

	def _get_currentPeriod(self):
		return self._currentPeriod

	def _set_currentPeriod(self, new_value):
		self._currentPeriod = new_value

	def _get_solution(self):
		return self._solution

	def _set_solution(self, new_value):
		self._solution = list(new_value)
		self.fitnessValue = Node.evaluate(self._solution) 

	def __lt__(self, node):
		return self.fitnessValue < node.fitnessValue

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

	# Properties
	currentPeriod = property(_get_currentPeriod, _set_currentPeriod)
	solution = property(_get_solution, _set_solution)