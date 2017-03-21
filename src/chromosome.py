#!/usr/bin/python
# -*-coding: utf-8 -*

from clsp_ga_library import *

class Chromosome(object):

	mutationRate = 0
	problem = 0
	ManufactItemsPeriods = []
	ItemsCounters = []

	# Builder 
	def __init__(self, solution=[], itemsRank = []):

		self._solution = []
		self._valueFitness = 0
		self.itemsRank = []

		
		if solution != []:
			self._solution = list(solution)
			self._valueFitness = 0
			self.itemsRank = self.getItemsRanks()

		if itemsRank != []:
			self.itemsRank = list(itemsRank)

	def __repr__(self):
		return " {} : {} ".format(self._solution,self._valueFitness)

	def __eq__(self, chromosome):
		return self._solution == chromosome.solution

	def getFeasible(self):

		if self.isFeasible() is False:
			#print("F Start : ", chromosome)
			# i make sure that the number of goods producted isn't superior to the number expected
			i = 0
			while i < Chromosome.problem.nbItems:

				itemDemandPeriods = Chromosome.problem.deadlineDemandPeriods[i]

				j = 0
				nb = 0
				while j <= itemDemandPeriods[len(itemDemandPeriods)-1]:

					if self._solution[j] == i+1 :

						nb += 1
						if nb > len(itemDemandPeriods):

							del self._solution[j]
							self._solution.insert(j,0)

						else:
							if j > itemDemandPeriods[nb-1]:
								del self._solution[j]
								self._solution.insert(j,0)

					j+=1

				i+=1

			#print(chromosome)
			
			# i make sure that the number of items producted isn't inferior to the number expected
			i = 0
			while i < Chromosome.problem.nbItems:

				itemDemandPeriods = Chromosome.problem.deadlineDemandPeriods[i]

				#print("item : ", i+1)

				nb = 0
				j = 0
				while nb < len(itemDemandPeriods) and j < len(self._solution):

					contain = False
					zeroperiods = []
					#print(" item nb : ", itemDemandPeriods[nb], " , ", nb)
					while j <= itemDemandPeriods[nb]:

						if self._solution[j] == 0:
							zeroperiods.append(j)

						if self._solution[j] == i+1 :
							#print("Yes : ", j)
							nb += 1	
							contain = True
							j += 1
							break

						j += 1

					#print("nb : ", nb, " j : ", j, " bool : ", contain, " zeroperiods : ", zeroperiods)

					if contain is False:
						if len(zeroperiods) > 0:
							del self._solution[zeroperiods[0]]
							self._solution.insert(zeroperiods[0], i+1)
							nb += 1
							j = zeroperiods[0]+1

				#print("Inter : ", chromosome)

				i+=1

		self._get_valueFitness()
	
	
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
				while j < len(itemManufactPeriods):

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

		#print("M Start : ", chromosome)

		if (randint(0,100) < (Chromosome.mutationRate*100)):

			mutated = False
			# i make sure that the returned chromosome's been actually mutated
			while mutated is False:

				randomIndice = randint(0,(len(self._solution)-1))
				item1 = self._solution[randomIndice]

				# i make sure that the randomIndice variable never corresponds to a zero indice
				while item1 == 0:
					randomIndice = randint(0,(len(self._solution)-1))
					# i get the item corresponding the gene to be flipped
					item1 = self._solution[randomIndice]

				item1DemandPeriods = Chromosome.problem.deadlineDemandPeriods[item1-1]

				i = 0
				nbItem1 = 0
				while i <= randomIndice:
					if self._solution[i] == item1:
						nbItem1 += 1
					i+=1

				deadlineItem1 = item1DemandPeriods[nbItem1-1]

				# i make sure that the second item chosen to replace the first one won't be the same with the item 1.
				item2 = randint(1, Chromosome.problem.nbItems)
				while item2 == item1:
					item2 = randint(1, Chromosome.problem.nbItems)

				item2ManufactPeriods = getManufactPeriods(self._solution, item2)

				item2DemandPeriods = Chromosome.problem.deadlineDemandPeriods[item2-1]

				#print(" item1 : ", item1, " item2 : ", item2, " randomIndice : ", randomIndice)
				#print(item2DemandPeriods)
				i = 0
				while i < len(item2DemandPeriods):
					if item2DemandPeriods[i] >= randomIndice and deadlineItem1 > item2ManufactPeriods[i]:
						self._solution = switchGenes(self._solution, randomIndice, item2ManufactPeriods[i])
						mutated = True
						break
					i += 1


	def _get_valueFitness(self):
		
		if self._valueFitness == 0:

			grid = Chromosome.problem.chanOverGrid
			#print(chromosome)

			# Calculation of all the change-over costs
			
			i = 1
			tmp = self._solution[0]
			while i < len(self._solution) :

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
						while j < len(self._solution) and self._solution[j] == 0:
							j+=1
						i=j-1
					
					i+=1

			# Calculation of the sum of holding costs

			i=0
			while i < Chromosome.problem.nbItems:

				itemDemandPeriods = Chromosome.problem.deadlineDemandPeriods[i]

				itemManufactPeriods = getManufactPeriods(self._solution, i+1)

				j = 0
				while j < len(itemDemandPeriods):
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


	def getItemsRanks(self):

		ranks = []
		gridCounters = list(Chromosome.ItemsCounters)
		#print("grid : ", gridCounters)

		i = 0 
		while i < len(self._solution):

			if self._solution[i] != 0:

				item = self._solution[i]
				counter = gridCounters[item-1]
				ranks.append(counter)

				# then, i increment the counter of this item
				del gridCounters[item-1]
				gridCounters.insert(item-1,(counter+1))

			else:
				ranks.append(0)
			i+=1

		return ranks

	# Definition of the properties
	solution = property(_get_solution,_set_solution)
	valueFitness = property(_get_valueFitness,_set_valueFitness)

	'''
	def advMutate(self):
		pass

	def getFeasible(self, solution, ranks):

		grid = list(Chromosome.ManufactItemsPeriods)

		# i make sure that the number of goods producted isn't superior to the number expected
		i = 0
		while i < len(solution):

			if solution[i] != 0:
				item = solution[i]
				rank = ranks[i]
				value = grid[item-1][rank-1]

				if value == -1:
					itemDemandPeriods = grid[item-1]
					del itemDemandPeriods[rank-1]
					itemDemandPeriods.insert(rank-1, i)
				else:
					cost1 = self.getCostof(value, item, rank, solution)
					cost2 = self.getCostof(i, item, rank, solution)
					if cost2 < cost1 :
						itemDemandPeriods = grid[item-1]
						del itemDemandPeriods[rank-1]
						itemDemandPeriods.insert(rank-1, i)

						del solution[value]
						solution.insert(value, item)

					else:
						del solution[i]
						solution.insert(i, 0)
			i+=1

		# i make sure that the number of items producted isn't inferior to the number expected
		i = 0
		while i < Chromosome.problem.nbItems:

			j = 0
			while j < len(grid[i]):

				if grid[i][j] == -1:
					if j == 0:
						lbound = 0
					else:
						lbound = grid[i][j-1]

					zeroperiods = []
					k = lbound
					while k < Chromosome.problem.deadlineDemandPeriods[i][j]:
						if solution[k] == 0:
							zeroperiods.append(k)
						k+=1

					if len(zeroperiods) > 0:
						del solution[zeroperiods[len(zeroperiods)-1]]
						solution.insert(zeroperiods[len(zeroperiods)-1], i+1)

						itemDemandPeriods = grid[i]
						del itemDemandPeriods[j]
						itemDemandPeriods.insert(j, zeroperiods[len(zeroperiods)-1])
				j+=1
			i+=1

		return solution

	def getCostof(self, indice, item, rank,solution):
		cost = 0
		# stocking cost 
		deadline = Chromosome.problem.deadlineDemandPeriods[item-1][rank-1]
		cost += (deadline - indice)* int(Chromosome.problem.holdingGrid[item-1])

		#print(" stock : ", cost)

		# change-over cost 
		if indice < len(solution)-1:
			if solution[indice+1] != 0:
				cost += int(Chromosome.problem.chanOverGrid[item-1][solution[indice+1]-1])
			else:
				j = indice+1
				while j < len(solution):
					if solution[j] != 0:
						cost += int(Chromosome.problem.chanOverGrid[item-1][solution[j]-1])
						break
					j+=1
		return cost
	'''