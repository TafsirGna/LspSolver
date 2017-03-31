#!/usr/bin/python
# -*-coding: utf-8 -*

from clsp_ga_library import *

class Chromosome(object):

	mutationRate = 0
	problem = 0
	ItemsCounters = []
	hashTable = {}

	# Builder 
	def __init__(self, solution=[], itemsRank = []):

		self._solution = []
		self._valueFitness = 0
		self._itemsRank = []
		self.itemsRankFlag = False
		self.manufactItemsPeriods = getManufactPeriodsGrid(Chromosome.problem.nbItems, Chromosome.problem.deadlineDemandPeriods) #Chromosome.problem.manufactItemsPeriods 

		if solution != []:
			self._solution = list(solution)
			self._getItemsRanks()
			self._valueFitness = 0

		if itemsRank != []:
			self._itemsRank = list(itemsRank)

	def __repr__(self):
		return " {} : {} ".format(self._solution,self._valueFitness)

	def __eq__(self, chromosome):
		return self._solution == chromosome.solution
	
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

		if (feasible is True):
			return True
		return False

	#--------------------
	# function : mutate
	# Class : Chromosome
	# purpose : Applying mutation to a given chromosome and returning the resulting one
	#--------------------

	def mutate(self):

		#print("M Start : ", self._solution)

		if (randint(0,100) < (Chromosome.mutationRate*100)): # then the chromsome has been selected for mutation 

			mutated = False
			# i make sure that the returned chromosome's been actually mutated
			while  mutated is False:

				randomIndice = randint(0,(Chromosome.problem.nbTimes-1))
				#print(" randomIndice : ", randomIndice)
				item1 = self._solution[randomIndice]

				# i make sure that the randomIndice variable never corresponds to a zero indice
				while item1 == 0:
					randomIndice = randint(0,(Chromosome.problem.nbTimes-1))
					# i get the item corresponding the gene to be flipped
					item1 = self._solution[randomIndice]

				# i make sure that the second item chosen to replace the first one won't be the same with the item 1.
				item2 = randint(1, Chromosome.problem.nbItems)
				while item2 == item1:
					item2 = randint(1, Chromosome.problem.nbItems)

				item2DemandPeriods = Chromosome.problem.deadlineDemandPeriods[item2-1]

				i = randomIndice
				itemsRank = self.itemsRank
				while i >= 0:
					if self._solution[i] == item2:

						if item2DemandPeriods[itemsRank[i]-1] >= randomIndice:
							#print(i, randomIndice)
							self._solution = switchGenes(self._solution, randomIndice, i)
							self._itemsRank = switchGenes(itemsRank, randomIndice, i)
							mutated = True
							break
					i-=1

		#print("F Start : ", self._solution)


	def _get_valueFitness(self):
		
		if self._valueFitness == 0:

			#print(self._solution)

			grid = Chromosome.problem.chanOverGrid
			#print(chromosome)

			# Calculation of all the change-over costs
			
			i = 1
			tmp = self._solution[0]
			while i < Chromosome.problem.nbTimes :

				n = self._solution[i]

				if (tmp == 0):
					i+=1
					tmp = n
				else:
					
					if (n != 0):
						if (n != tmp):
							self._valueFitness += int((grid[tmp-1])[n-1])
							tmp = n
					else:
						tmp = self._solution[i-1]

						j=i
						while j < Chromosome.problem.nbTimes and self._solution[j] == 0:
							j+=1
						i=j-1
					
					i+=1

			# Calculation of the sum of holding costs

			i=0
			while i < Chromosome.problem.nbItems:

				itemDemandPeriods = Chromosome.problem.deadlineDemandPeriods[i]

				itemManufactPeriods = getManufactPeriods(self._solution, i+1)

				j = 0
				nbitemDemandPeriods = len(itemDemandPeriods)
				while j < nbitemDemandPeriods:
					self._valueFitness += int(Chromosome.problem.holdingGrid[i])*(itemDemandPeriods[j]-itemManufactPeriods[j])
					j+=1

				i+=1

		return self._valueFitness

	def _get_solution(self):
		return self._solution

	def _set_solution(self, new_solution):
		self._solution = new_solution

	def _set_valueFitness(self, new_value):
		self._valueFitness = new_value


	def _getItemsRanks(self):

		#if self.itemsRankFlag is False:

		self._itemsRank = []
		gridCounters = list(Chromosome.ItemsCounters)
		#print("grid : ", gridCounters)

		i = 0 
		while i < Chromosome.problem.nbTimes:

			if self._solution[i] != 0:

				item = self._solution[i]
				counter = gridCounters[item-1]
				self._itemsRank.append(counter)

				# then, i increment the counter of this item
				del gridCounters[item-1]
				gridCounters.insert(item-1,(counter+1))

			else:
				self._itemsRank.append(0)

			i+=1

			#self.itemsRankFlag = True

		return self._itemsRank

	def _setItemsRanks(self, new_value):
		self._itemsRank = new_value

	# Definition of the properties
	solution = property(_get_solution,_set_solution)
	valueFitness = property(_get_valueFitness,_set_valueFitness)
	itemsRank = property(_getItemsRanks, _setItemsRanks)


	def advmutate(self):

		solution = list(self._solution)
		itemsRank = self.itemsRank

		i = 0
		while i < Chromosome.problem.nbTimes:

			if solution[i] != 0:

				item1 = solution[i]

				item2 = 1

				while item2 <= Chromosome.problem.nbItems :
					
					if item2 != item1:

						item2DemandPeriods = Chromosome.problem.deadlineDemandPeriods[item2-1]

						#print(" i : ", i," item2 : ", item2, " item2DemandPeriods : ", item2DemandPeriods)
						j = i
						while j >= 0:
							if solution[j] == item2:
								#print(" item's rank value : ", itemsRank[j], " j : ", j)
								if item2DemandPeriods[itemsRank[j]-1] >= i:
									solution = switchGenes(solution, j, i)
									itemsRank = switchGenes(itemsRank, j, i)
									break
							j-=1

						# i check if the resulting chromosome would have a better fitness than the current's fitness
						c = Chromosome(solution)
						#print(c.solution,c.valueFitness, self.valueFitness)
						if c.valueFitness < self.valueFitness:
							self._solution = c.solution
							self._itemsRank = c.itemsRank

						solution = list(self._solution)
						itemsRank = self.itemsRank

					item2 += 1

			i+=1

	
	def getFeasible(self):

		#print(" In Chromosome 1 : ", self._solution)

		if self.isFeasible() is False:

			#print(" grid : ", grid)

			# i make sure that the number of goods producted isn't superior to the number expected
			i = 0
			while i < Chromosome.problem.nbTimes:

				if self._solution[i] != 0:

					item = self._solution[i]
					#print(" ok : ", self._solution, self._itemsRank)
					rank = self._itemsRank[i]
					#print(i, item-1, rank-1, grid)
					value = self.manufactItemsPeriods[item-1][rank-1]

					if value == -1:
						itemDemandPeriods = self.manufactItemsPeriods[item-1]
						del itemDemandPeriods[rank-1]
						itemDemandPeriods.insert(rank-1, i)

						#print(" == -1 ", item, i, rank)

					else:

						#print(" != -1 ", item, i, rank)

						cost1 = self.getCostof(value, item, rank, self._solution, i)
						cost2 = self.getCostof(i, item, rank, self._solution, value)

						#print(" cost 1 : ", cost1, " cost2 : ", cost2)
						if cost2 < cost1 :
							itemDemandPeriods = self.manufactItemsPeriods[item-1]
							del itemDemandPeriods[rank-1]
							itemDemandPeriods.insert(rank-1, i)

							#print(" cost2 < cost1 : ", value, item)
							del self._solution[value]
							self._solution.insert(value, 0)

						else:
							del self._solution[i]
							self._solution.insert(i, 0)
				i+=1

			#print(self._solution, ", ", self._itemsRank)
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
						k = lbound
						while k <= Chromosome.problem.deadlineDemandPeriods[i][j]:
							if self._solution[k] == 0:
								zeroperiods.append(k)
							k+=1

						#print("zeroperiods : ", zeroperiods)
						nbZeroPeriods = len(zeroperiods)
						if nbZeroPeriods > 0:

							cost1 = self.getCostof(zeroperiods[0], i+1, j+1, self._solution)
							#print(" cost1 : ", cost1 )

							k = 1 
							indice = zeroperiods[0]
							while k < nbZeroPeriods:
								cost2 = self.getCostof(zeroperiods[k], i+1, j+1, self._solution)
								#print(" cost2 : ", cost2 , zeroperiods[k])
								if cost2 < cost1:
									#print(" cost2 < cost1 : ", cost1 , cost2 )
									indice = zeroperiods[k]
								k+=1

							del self._solution[indice]
							self._solution.insert(indice, i+1)

							itemDemandPeriods = self.manufactItemsPeriods[i]
							del itemDemandPeriods[j]
							itemDemandPeriods.insert(j, indice)

						else:
							
							# experimental code 

							# if there's no place to put this item, then i check all the other times in order to put this item there
							
							zeroperiods = []
							k = 0
							while k <= lbound:
								if self._solution[k] == 0:
									zeroperiods.append(k)
								k+=1

							nbZeroPeriods = len(zeroperiods)
							if nbZeroPeriods > 0:

								cost1 = self.getCostof(zeroperiods[0], i+1, j+1, self._solution)
								#print(" cost1 : ", cost1 )

								k = 1 
								indice = zeroperiods[0]
								while k < nbZeroPeriods:
									cost2 = self.getCostof(zeroperiods[k], i+1, j+1, self._solution)
									#print(" cost2 : ", cost2 , zeroperiods[k])
									if cost2 < cost1:
										#print(" cost2 < cost1 : ", cost1 , cost2 )
										indice = zeroperiods[k]
									k+=1

								del self._solution[indice]
								self._solution.insert(indice, i+1)

								itemDemandPeriods = self.manufactItemsPeriods[i]
								del itemDemandPeriods[j]
								itemDemandPeriods.insert(j, indice)

					j+=1
				i+=1

		hashSol = self.hashSolution()
		if hashSol not in Chromosome.hashTable:
			self._get_valueFitness()
			Chromosome.hashTable[hashSol] = self._valueFitness
		else:
			self.valueFitness = Chromosome.hashTable[hashSol]

		#self._itemsRank = self.getItemsRanks()
	
	def getCostof(self, indice, item, rank,solution, secondIndice=0):

		solution = list(solution)

		if secondIndice > indice:
			del solution[secondIndice]
			solution.insert(secondIndice,0)

		cost = 0
		# stocking cost 
		deadline = Chromosome.problem.deadlineDemandPeriods[item-1][rank-1]
		cost += (deadline - indice)* int(Chromosome.problem.holdingGrid[item-1])

		#print(" stock : ", cost)

		# change-over cost 
		if indice < Chromosome.problem.nbTimes-1:
			if solution[indice+1] != 0:
				cost += int(Chromosome.problem.chanOverGrid[item-1][solution[indice+1]-1])
			else:
				j = indice+1
				while j < Chromosome.problem.nbTimes:
					if solution[j] != 0:
						cost += int(Chromosome.problem.chanOverGrid[item-1][solution[j]-1])
						break
					j+=1
		return cost

	def hashSolution(self):

		hashSol = ""
		i = 0
		while i < Chromosome.problem.nbTimes:
			hashSol += str(self._solution[i])
			i+=1
		
		return hashSol
