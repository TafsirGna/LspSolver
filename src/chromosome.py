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
		self._itemsRank = []
		self._valueFitness = 0
		self.itemsRankFlag = False
		self._hashSolution = ""
		self.manufactItemsPeriods = getManufactPeriodsGrid(Chromosome.problem.nbItems, Chromosome.problem.deadlineDemandPeriods) #Chromosome.problem.manufactItemsPeriods 

		if solution != []:
			self._solution = list(solution)
			self._get_hashSolution()
			self._getItemsRanks()

			if self.isFeasible():
				self._get_valueFitness()

		if itemsRank != []:
			self._itemsRank = list(itemsRank)

	def __repr__(self):
		return " {} : {} ".format(self._solution,self.valueFitness)

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
			if mutated is False:

				randomIndice = randint(0,(Chromosome.problem.nbTimes-1))
				#print(" randomIndice : ", randomIndice)
				item1 = self._solution[randomIndice]

				# i make sure that the randomIndice variable never corresponds to a zero indice
				while item1 == 0:
					randomIndice = randint(0,(Chromosome.problem.nbTimes-1))
					# i get the item corresponding the gene to be flipped
					item1 = self._solution[randomIndice]

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
								formerSolution = self._solution
								self._solution = switchGenes(self._solution, randomIndice, i)
								self.updateHashSolution(self._hashSolution, randomIndice, i)
								self.updateFitnessValue(formerSolution, randomIndice, i)
								self._itemsRank = switchGenes(itemsRank, randomIndice, i)
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
									formerSolution = self._solution
									self._solution = switchGenes(self._solution, randomIndice, i)
									self.updateHashSolution(self._hashSolution, randomIndice, i)
									self.updateFitnessValue(formerSolution, randomIndice, i)
									self._itemsRank = switchGenes(itemsRank, randomIndice, i)
									mutated = True
									break					

						i += 1


		#print("F Start : ", self._solution)


	def _get_valueFitness(self):
		
		#val1 = self._valueFitness
		#print(self._solution)

		if self._valueFitness == 0:

			if self.hashSolution not in Chromosome.hashTable:
				
				grid = Chromosome.problem.chanOverGrid

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

				#print(" intermediary cost : ", self._valueFitness)
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

				Chromosome.hashTable[self.hashSolution] = self._valueFitness

			else:
				self._valueFitness = Chromosome.hashTable[self.hashSolution]

		return self._valueFitness

	def _get_solution(self):
		return self._solution

	def _set_solution(self, new_solution):
		self._solution = new_solution

		if self.isFeasible():
			self._get_valueFitness()

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

	def _get_hashSolution(self):

		if self._hashSolution == "":

			i = 0
			while i < Chromosome.problem.nbTimes:
				self._hashSolution += str(self._solution[i])
				i+=1
			
		return self._hashSolution

	def _set_hashSolution(self, new_value):
		self._hashSolution = new_value

	# Definition of the properties
	solution = property(_get_solution,_set_solution)
	valueFitness = property(_get_valueFitness,_set_valueFitness)
	itemsRank = property(_getItemsRanks, _setItemsRanks)
	hashSolution = property(_get_hashSolution, _set_hashSolution) 


	def advmutate(self):

		solution1 = list(self._solution)
		itemsRank1 = self.itemsRank

		i = 0
		while i < Chromosome.problem.nbTimes:

			if solution1[i] != 0:

				item1 = solution1[i]

				item2 = 1

				while item2 <= Chromosome.problem.nbItems :
					
					if item2 != item1:

						item2DemandPeriods = Chromosome.problem.deadlineDemandPeriods[item2-1]

						#print(" i : ", i," item2 : ", item2, " item2DemandPeriods : ", item2DemandPeriods)
						j = i
						solution2 = []
						while j >= 0:
							if solution1[j] == item2:
								#print(" item's rank value : ", itemsRank[j], " j : ", j)
								if item2DemandPeriods[itemsRank1[j]-1] >= i:
									solution2 = switchGenes(solution1, j, i)
									itemsRank2 = switchGenes(itemsRank1, j, i)									
									break
							j-=1

						# i check if the resulting chromosome would have a better fitness than the current's fitness
						if solution2 != []:

							c = Chromosome(solution2)
							#print(c.solution,c.valueFitness, self.valueFitness)
							if c.valueFitness < self.valueFitness:
								self._solution = c.solution
								self._itemsRank = c.itemsRank
								self._valueFitness = c.valueFitness
								self._hashSolution = c.hashSolution

					item2 += 1

			i+=1

	
	def getFeasible(self):

		#print(" In Chromosome 1 : ", self._solution)
		#print(self._solution)

		if self.isFeasible() is False:

			#print(" grid : ", grid)

			# i make sure that the number of goods producted isn't superior to the number expected
			i = 0
			while i < Chromosome.problem.nbTimes:

				if self._solution[i] != 0:

					item = self._solution[i]
					#print(" ok : ", self._solution, self._itemsRank)
					rank = self._itemsRank[i]
					#print(i, item-1, rank-1)
					value = self.manufactItemsPeriods[item-1][rank-1]

					if value == -1:
						itemDemandPeriods = self.manufactItemsPeriods[item-1]
						del itemDemandPeriods[rank-1]
						itemDemandPeriods.insert(rank-1, i)

						#print(" == -1 ", item, i, rank)

					else:

						#print(" != -1 ", item, i, rank)

						cost1 = Chromosome.getCostof(value, item, rank, self._solution, i)
						cost2 = Chromosome.getCostof(i, item, rank, self._solution, value)

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

							cost1 = Chromosome.getCostof(zeroperiods[0], i+1, j+1, self._solution)
							#print(" cost1 : ", cost1 )

							k = 1 
							indice = zeroperiods[0]
							while k < nbZeroPeriods:
								cost2 = Chromosome.getCostof(zeroperiods[k], i+1, j+1, self._solution)
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

									cost1 = Chromosome.getCostof(zeroperiods[0], i+1, p, self._solution)
									#print(" cost1 : ", cost1 )

									k = 1 
									indice = zeroperiods[0]
									while k < nbZeroPeriods:
										cost2 = Chromosome.getCostof(zeroperiods[k], i+1, p, self._solution)
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

									break
								p += 1


					j+=1
				i+=1

		#print("at the end of getFeasible : ", self._solution)
		self._get_valueFitness()

		#self._itemsRank = self.getItemsRanks()

	def getCostof(cls, indice, item, rank,solution, secondIndice = -1):

		solution = list(solution)

		if secondIndice != -1:
			del solution[secondIndice]
			solution.insert(secondIndice,0)

		cost = 0
		# stocking cost 
		deadline = cls.problem.deadlineDemandPeriods[item-1][rank-1]
		cost += (deadline - indice)* int(Chromosome.problem.holdingGrid[item-1])

		#print(" cost 1 : ", cost)

		# change-over cost 
		if indice < cls.problem.nbTimes-1:
			if solution[indice+1] != 0:
				cost += int(Chromosome.problem.chanOverGrid[item-1][solution[indice+1]-1])
			else:
				j = indice+1
				while j < cls.problem.nbTimes:
					if solution[j] != 0:
						cost += int(Chromosome.problem.chanOverGrid[item-1][solution[j]-1])
						break
					j+=1

		#print(" cost 2 : ", cost)

		if indice > 0:
			if solution[indice-1] != 0:
				cost += int(cls.problem.chanOverGrid[solution[indice-1]-1][item-1])
			else:
				j = indice-1
				while j >= 0:
					if solution[j] != 0:
						cost += int(Chromosome.problem.chanOverGrid[solution[j]-1][item-1])
						break
					j-=1

		#print(" cost 3 : ", cost)

		return cost

	getCostof = classmethod(getCostof)

	def updateFitnessValue(self, solution, indice1, indice2):

		# i chop from this chromosome fitness value, the changeover costs of the moved items

		if self.hashSolution not in Chromosome.hashTable:

			item1 = solution[indice1]
			item2 = solution[indice2]
			
			#print("indice 2 : ", indice2, " solution : ", solution)
			nItem1, nIndice1 = nextPeriodItemOf(indice1, solution)
			#print(" indice 1 : ", indice1, " nIndice 1 : ", nIndice1 )
			nItem2, nIndice2 = nextPeriodItemOf(indice2, solution)
			#print(" indice 2 : ", indice2, " nIndice 2 : ", nIndice2 )
			pItem1, pIndice1 = previousPeriodItemOf(indice1, solution)
			#print(" indice 1 : ", indice1, " pIndice 1 : ", pIndice1 )
			pItem2, pIndice2 = previousPeriodItemOf(indice2, solution)
			#print(" indice 2 : ", indice2, " pIndice 2 : ", pIndice2 )

			if nIndice1 == indice2 or pIndice2 == indice1:

				#print("i1 : ", item1, " i2 : ", item2)
				self._valueFitness -= int(Chromosome.problem.chanOverGrid[item1-1][item2-1])
				self._valueFitness += int(Chromosome.problem.chanOverGrid[item2-1][item1-1])

				if pIndice1 != 0:
					self._valueFitness -= int(Chromosome.problem.chanOverGrid[pItem1-1][item1-1])
					self._valueFitness += int(Chromosome.problem.chanOverGrid[pItem1-1][item2-1])

				if nIndice2 != 0:
					self._valueFitness -= int(Chromosome.problem.chanOverGrid[item2-1][nItem2-1])
					self._valueFitness += int(Chromosome.problem.chanOverGrid[item1-1][nItem2-1])

			elif nIndice2 == indice1 or pIndice1 == indice2:

				self._valueFitness -= int(Chromosome.problem.chanOverGrid[item2-1][item1-1])
				self._valueFitness += int(Chromosome.problem.chanOverGrid[item1-1][item2-1])

				if pIndice2 != 0:
					self._valueFitness -= int(Chromosome.problem.chanOverGrid[pItem2-1][item2-1])
					self._valueFitness += int(Chromosome.problem.chanOverGrid[pItem2-1][item1-1])

				if nIndice1 != 0:
					#print(item1, nIndice1)
					self._valueFitness -= int(Chromosome.problem.chanOverGrid[item1-1][nItem1-1])
					self._valueFitness += int(Chromosome.problem.chanOverGrid[item2-1][nItem1-1])

			else:

				# i chop from the fitness value the changeover costs of the previous solution 
				if nItem1 != 0:
					self._valueFitness -= int(Chromosome.problem.chanOverGrid[item1-1][nItem1-1])
					self._valueFitness += int(Chromosome.problem.chanOverGrid[item2-1][nItem1-1])

				if pItem1 != 0:
					self._valueFitness -= int(Chromosome.problem.chanOverGrid[pItem1-1][item1-1])
					self._valueFitness += int(Chromosome.problem.chanOverGrid[pItem1-1][item2-1])

				if nItem2 != 0:
					self._valueFitness -= int(Chromosome.problem.chanOverGrid[item2-1][nItem2-1])
					self._valueFitness += int(Chromosome.problem.chanOverGrid[item1-1][nItem2-1])

				if pItem2 != 0:
					self._valueFitness -= int(Chromosome.problem.chanOverGrid[pItem2-1][item2-1])
					self._valueFitness += int(Chromosome.problem.chanOverGrid[pItem2-1][item1-1])


			#Once, i've handled the changeover costs, i tackle the stocking costs' issue
			if indice2 > indice1:
				self._valueFitness += int(Chromosome.problem.holdingGrid[item2-1]) * (indice2-indice1)
				self._valueFitness -= int(Chromosome.problem.holdingGrid[item1-1]) * (indice2-indice1)
			else:
				self._valueFitness -= int(Chromosome.problem.holdingGrid[item2-1]) * (indice1-indice2)
				self._valueFitness += int(Chromosome.problem.holdingGrid[item1-1]) * (indice1-indice2)

		else:
			self._valueFitness = Chromosome.hashTable[self.hashSolution]


	def updateHashSolution(self, solution, indice1, indice2):

		item1 = solution[indice1]
		item2 = solution[indice2]

		self._hashSolution = solution[:(indice1)] + str(item2) + solution[(indice1+1):]
		self._hashSolution = self._hashSolution[:(indice2)] + str(item1) + self._hashSolution[(indice2+1):]

