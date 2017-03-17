#!/usr/bin/python
# -*-coding: utf-8 -*

from clsp_ga_library import *

class Chromosome:

	mutationRate = 0
	problem = 0

	# Builder 
	def __init__(self, solution):
		self.solution = list(solution)
		self._valueFitness = 0 
		self.manufactGrid = []

	def __repr__(self):
		return " Solution : {}, valueFitness : {}".format(self.solution,self._valueFitness)

	def __eq__(self, chromosome):
		return self.solution == chromosome.solution

	def getFeasible(self):

		if self.isFeasible() is False:
			#print("F Start : ", chromosome)
			# i make sure that the number of goods producted isn't superior to the number expected
			i = 0
			while i < Chromosome.problem.nbItems:

				itemDemandPeriods = getDemandPeriods(Chromosome.problem.demandsGrid[i])

				j = 0
				nb = 0
				while j <= itemDemandPeriods[len(itemDemandPeriods)-1]:

					if self.solution[j] == i+1 :

						nb += 1
						if nb > len(itemDemandPeriods):

							del self.solution[j]
							self.solution.insert(j,0)

						else:
							if j > itemDemandPeriods[nb-1]:
								del self.solution[j]
								self.solution.insert(j,0)

					j+=1

				i+=1

			#print(chromosome)
			
			# i make sure that the number of items producted isn't inferior to the number expected
			i = 0
			while i < Chromosome.problem.nbItems:

				itemDemandPeriods =  getDemandPeriods(Chromosome.problem.demandsGrid[i])

				#print("item : ", i+1)

				nb = 0
				j = 0
				while nb < len(itemDemandPeriods) and j < len(self.solution):

					contain = False
					zeroperiods = []
					#print(" item nb : ", itemDemandPeriods[nb], " , ", nb)
					while j <= itemDemandPeriods[nb]:

						if self.solution[j] == 0:
							zeroperiods.append(j)

						if self.solution[j] == i+1 :
							#print("Yes : ", j)
							nb += 1	
							contain = True
							j += 1
							break

						j += 1

					#print("nb : ", nb, " j : ", j, " bool : ", contain, " zeroperiods : ", zeroperiods)

					if contain is False:
						if len(zeroperiods) > 0:
							del self.solution[zeroperiods[0]]
							self.solution.insert(zeroperiods[0], i+1)
							nb += 1
							j = zeroperiods[0]+1

				#print("Inter : ", chromosome)

				i+=1
	
	
	def isFeasible(self):

		# i check first that there's not shortage or backlogging
		i = 0
		feasible = False
		while i < Chromosome.problem.nbItems:

			demandProductPeriods = getDemandPeriods(Chromosome.problem.demandsGrid[i])

			manufactProductPeriods = getManufactPeriods(self.solution,i+1)

			if (len(manufactProductPeriods) != len(demandProductPeriods)):
				return False
			else:
				j = 0
				while j < len(manufactProductPeriods):

					if (manufactProductPeriods[j] > demandProductPeriods[j]):
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

				randomIndice = randint(0,(len(self.solution)-1))
				item1 = self.solution[randomIndice]

				# i make sure that the randomIndice variable never corresponds to a zero indice
				while item1 == 0:
					randomIndice = randint(0,(len(self.solution)-1))
					# i get the item corresponding the gene to be flipped
					item1 = self.solution[randomIndice]

				item1DemandPeriods = getDemandPeriods(Chromosome.problem.demandsGrid[item1-1])

				i = 0
				nbItem1 = 0
				while i <= randomIndice:
					if self.solution[i] == item1:
						nbItem1 += 1
					i+=1

				deadlineItem1 = item1DemandPeriods[nbItem1-1]

				# i make sure that the second item chosen to replace the first one won't be the same with the item 1.
				item2 = randint(1, Chromosome.problem.nbItems)
				while item2 == item1:
					item2 = randint(1, Chromosome.problem.nbItems)

				item2ManufactPeriods = getManufactPeriods(self.solution, item2)

				item2DemandPeriods = getDemandPeriods(Chromosome.problem.demandsGrid[item2-1])

				#print(" item1 : ", item1, " item2 : ", item2, " randomIndice : ", randomIndice)
				#print(item2DemandPeriods)
				i = 0
				while i < len(item2DemandPeriods):
					if item2DemandPeriods[i] >= randomIndice and deadlineItem1 > item2ManufactPeriods[i]:
						self.solution = switchGenes(self.solution, randomIndice, item2ManufactPeriods[i])
						mutated = True
						break
					i += 1


	def _get_valueFitness(self):

		if self._valueFitness == 0:
			grid = Chromosome.problem.chanOverGrid
			#print(chromosome)

			# Calculation of all the change-over costs
			
			i = 1
			tmp = self.solution[0]
			while i < len(self.solution) :

				n = self.solution[i]

				if (tmp == 0):
					i+=1
					tmp = n
				else:
					
					if (n != 0):
						if (n != tmp):
							self._valueFitness += int((grid[tmp-1])[n-1])
							tmp = n
					else:
						tmp = self.solution[i-1]

						j=i
						while j < len(self.solution) and self.solution[j] == 0:
							j+=1
						i=j-1
					
					i+=1

			# Calculation of the sum of holding costs

			i=0
			while i < Chromosome.problem.nbItems:

				itemDemands = Chromosome.problem.demandsGrid[i]

				itemDemandPeriods = getDemandPeriods(itemDemands)

				itemManufactPeriods = getManufactPeriods(self.solution, i+1)

				j = 0
				while j < len(itemDemandPeriods):
					self._valueFitness += int(Chromosome.problem.holdingGrid[i])*(itemDemandPeriods[j]-itemManufactPeriods[j])
					j+=1

				i+=1


		return self._valueFitness

	def _set_valueFitness(self, valueFitness):
		self._valueFitness = valueFitness

	# Definition of the properties
	valueFitness = property(_get_valueFitness,_set_valueFitness)