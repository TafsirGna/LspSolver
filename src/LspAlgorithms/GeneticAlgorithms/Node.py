from .Chromosome import Chromosome
import copy

class Node(object):

	def __init__(self):

		# self.chromosome = Chromosome()
		self._currentPeriod = Chromosome.problem.nbTimes - 1
		self.tab = []
		self.branches = []

		#for i in range(0, len(Chromosome.problem.deadlineDemandPeriods)-1):
		#	self.itemsCountTab.append(len(Chromosome.problem.deadlineDemandPeriods[i]))

	def initialize(self):
		
		self.chromosome = Chromosome()
		self._currentPeriod = Chromosome.problem.nbTimes - 1

		self.tab = copy.deepcopy(Chromosome.problem.deadlineDemandPeriods)
		self.tab.append(copy.deepcopy(Chromosome.problem.zerosRow))

		self.branches = []

	def __repr__(self):
		#return "Chromosome : " + str(self._solution) + ", " + str(self.fitnessValue) +  ", " + str(self._currentPeriod) + ", " + str(self.tab) + " : ranks - " + str(self.itemsRank) +" ;" 
		return "Chromosome : " + str(self.chromosome.solution) + " / "+ str(self.chromosome.itemsRank)+", " + str(self.chromosome.fitnessValue) +  ", " + str(self._currentPeriod)  + ", " + str(self.tab) + \
		" / " + str(self.branches) + " ;" 

	def isLeaf(self):
		
		if self._currentPeriod == -1:
			return True
		return False

	def formChild(self, branch_row):

		#print("branch_row : ", branch_row)
		child = []
		if len(branch_row) == 1:

			#print("ok 1 ")
			if branch_row[0][0] != 0:

				#print("ok 2 ")
				child = Node()
				child.tab = copy.deepcopy(self.tab)
				child.branches = copy.deepcopy(self.branches)
				child.branches.insert(0, [])

				# i build the chromosome of the child 
				child.chromosome.solution = copy.deepcopy(self.chromosome.solution)
				child.chromosome.solution.insert(0, branch_row[0][0])
				child.chromosome.itemsRank = copy.deepcopy(self.chromosome.itemsRank)
				child.chromosome.itemsRank.insert(0, len(self.tab[branch_row[0][0]-1]))
				child.chromosome.manufactItemsPeriods = copy.deepcopy(self.chromosome.manufactItemsPeriods)
				(child.chromosome.manufactItemsPeriods[branch_row[0][0]-1]).insert(0, self.currentPeriod)
				child.chromosome.fitnessValue = Node.getFitnessValue(self.chromosome.solution, self.chromosome.fitnessValue, branch_row[0][0]-1, len(self.tab[branch_row[0][0]-1]), self.currentPeriod)

				child.currentPeriod = self.currentPeriod - 1
				del child.tab[branch_row[0][0]-1][len(self.tab[branch_row[0][0]-1])-1]

			else:
				#print("ok 3 ")
			
				child = Node()
				child.tab = copy.deepcopy(self.tab)
				child.branches = copy.deepcopy(self.branches)
				child.branches.insert(0, [])

				# i build the chromosome of the child 
				child.chromosome.solution = copy.deepcopy(self.chromosome.solution)
				child.chromosome.solution.insert(0, 0)
				child.chromosome.itemsRank = copy.deepcopy(self.chromosome.itemsRank)
				child.chromosome.itemsRank.insert(0, 0)
				child.chromosome.manufactItemsPeriods = copy.deepcopy(self.chromosome.manufactItemsPeriods)
				(child.chromosome.manufactItemsPeriods[Chromosome.problem.nbItems]).insert(0, self.currentPeriod)
				child.chromosome.fitnessValue = self.chromosome.fitnessValue

				child.currentPeriod = self.currentPeriod - 1
				del child.tab[Chromosome.problem.nbItems][len(child.tab[Chromosome.problem.nbItems])-1]


		elif branch_row[0] == [0, 0] :

			#print("ok 4 ")
			if randint(1,2) == 1:
				
				#print("ok 5 ")
				child = Node()
				child.tab = copy.deepcopy(self.tab)
				child.branches = copy.deepcopy(self.branches)
				child.branches.insert(0, copy.deepcopy(branch_row))

				# i build the chromosome of the child 
				child.chromosome.solution = copy.deepcopy(self.chromosome.solution)
				child.chromosome.solution.insert(0, 0)
				child.chromosome.itemsRank = copy.deepcopy(self.chromosome.itemsRank)
				child.chromosome.itemsRank.insert(0, 0)
				child.chromosome.manufactItemsPeriods = copy.deepcopy(self.chromosome.manufactItemsPeriods)
				(child.chromosome.manufactItemsPeriods[Chromosome.problem.nbItems]).insert(0, self.currentPeriod)
				child.chromosome.fitnessValue = self.chromosome.fitnessValue

				(child.branches[0]).remove([0,0])

				child.currentPeriod = self.currentPeriod - 1
				del child.tab[Chromosome.problem.nbItems][len(child.tab[Chromosome.problem.nbItems])-1]

			else:
				
				#print("ok 6 ")
				child = Node()
				child.tab = copy.deepcopy(self.tab)
				child.branches = copy.deepcopy(self.branches)
				child.branches.insert(0, copy.deepcopy(branch_row))

				# i build the chromosome of the child 
				child.chromosome.solution = copy.deepcopy(self.chromosome.solution)
				child.chromosome.solution.insert(0, branch_row[1][0])
				child.chromosome.itemsRank = copy.deepcopy(self.chromosome.itemsRank)
				child.chromosome.itemsRank.insert(0, len(self.tab[branch_row[1][0]-1]))
				child.chromosome.manufactItemsPeriods = copy.deepcopy(self.chromosome.manufactItemsPeriods)
				(child.chromosome.manufactItemsPeriods[branch_row[1][0]-1]).insert(0, self.currentPeriod)
				child.chromosome.fitnessValue = Node.getFitnessValue(self.chromosome.solution, self.chromosome.fitnessValue, branch_row[1][0]-1, len(self.tab[branch_row[1][0]-1]), self.currentPeriod)

				for element in child.branches[0]:
					if element[0] == branch_row[1][0]:
						(child.branches[0]).remove(element)
				
				child.currentPeriod = self.currentPeriod - 1
				del child.tab[branch_row[1][0]-1][len(self.tab[branch_row[1][0]-1])-1]

		else:
			
			#print("ok 7 ")

			child = Node()
			child.tab = copy.deepcopy(self.tab)
			child.branches = copy.deepcopy(self.branches)
			child.branches.insert(0, copy.deepcopy(branch_row))

			# i build the chromosome of the child 
			child.chromosome.solution = copy.deepcopy(self.chromosome.solution)
			child.chromosome.solution.insert(0, branch_row[0][0])
			child.chromosome.itemsRank = copy.deepcopy(self.chromosome.itemsRank)
			child.chromosome.itemsRank.insert(0, len(self.tab[branch_row[0][0]-1]))
			child.chromosome.manufactItemsPeriods = copy.deepcopy(self.chromosome.manufactItemsPeriods)
			(child.chromosome.manufactItemsPeriods[branch_row[0][0]-1]).insert(0, self.currentPeriod)
			child.chromosome.fitnessValue = Node.getFitnessValue(self.chromosome.solution, self.chromosome.fitnessValue, branch_row[0][0]-1, len(self.tab[branch_row[0][0]-1]), self.currentPeriod)

			for element in child.branches[0]:
				if element[0] == branch_row[0][0]:
					(child.branches[0]).remove(element)
			
			child.currentPeriod = self.currentPeriod - 1
			del child.tab[branch_row[0][0]-1][len(self.tab[branch_row[0][0]-1])-1]

		return child
		

	def getChild(self):

		if self.currentPeriod > -1:

			branch_row = []

			for i in range(0, Chromosome.problem.nbItems):

				if self.tab[i] != [] and self.tab[i][len(self.tab[i])-1] >= self._currentPeriod:

					for element in Chromosome.problem.orderedPrecs[self.chromosome.solution[0]-1]:
						#print ("	in : ", Chromosome.problem.orderedPrecs[], )
						if element[0] == i + 1:
							branch_row.append([i+1, element[1]])
							break

			if self.tab[Chromosome.problem.nbItems] != []:
				branch_row.append([0, 0])

			branch_row = sorted(branch_row, key = getPrecsTabKey)
			#print("branch_row : ", branch_row)
			return self.formChild(branch_row)

		else:
			
			#print("STOOOOOOOOOOOOOOP")

			currentPeriod = self._currentPeriod + 1
			solution = copy.deepcopy(self.chromosome.solution)
			tab = copy.deepcopy(self.tab)
			branches = copy.deepcopy(self.branches)
			itemsRank = copy.deepcopy(self.chromosome.itemsRank)
			manufactItemsPeriods = copy.deepcopy(self.chromosome.manufactItemsPeriods)
			fitnessValue = self.chromosome.fitnessValue

			counterTab = [0] * (Chromosome.problem.nbItems + 1)
			while currentPeriod < Chromosome.problem.nbTimes and branches[0] == []:

				item = solution[0]
				#print("in while : item : ", item)
				if item != 0:
					counterTab[item-1] += 1
					deadline = Chromosome.problem.deadlineDemandPeriods[item-1][counterTab[item-1]-1]
					(tab[item-1]).append(deadline)
					(tab[item-1]).sort()

					fitnessValue -= int(Chromosome.problem.holdingGrid[item-1]) * (Chromosome.problem.deadlineDemandPeriods[item-1][itemsRank[0]-1] - currentPeriod)
					if currentPeriod != Chromosome.problem.nbTimes - 1:

						i = 1
						while i <= ((Chromosome.problem.nbTimes - 1) - currentPeriod):
							if solution[i] != 0:
								fitnessValue -= int(Chromosome.problem.chanOverGrid[item-1][solution[i]-1])
								break
							i += 1

					del manufactItemsPeriods[item-1][0]

				else:
					counterTab[Chromosome.problem.nbItems] += 1
					(tab[Chromosome.problem.nbItems]).append(0)
					(tab[Chromosome.problem.nbItems]).sort()

					del manufactItemsPeriods[Chromosome.problem.nbItems][0]

				del solution[0]
				del branches[0]
				del itemsRank[0]
				currentPeriod += 1
				#print("in while 2 : ", solution, itemsRank, tab)

			if currentPeriod == Chromosome.problem.nbTimes:
				return []

			item = solution[0]

			#print("in function : item : ", item)
			if item != 0:

				counterTab[item-1] += 1
				deadline = Chromosome.problem.deadlineDemandPeriods[item-1][counterTab[item-1]-1]
				(tab[item-1]).append(deadline)
				(tab[item-1]).sort()

				fitnessValue -= int(Chromosome.problem.holdingGrid[item-1]) * (Chromosome.problem.deadlineDemandPeriods[item-1][itemsRank[0]-1] - currentPeriod)
				if currentPeriod != Chromosome.problem.nbTimes - 1:

					i = 1
					while i <= ((Chromosome.problem.nbTimes - 1) - currentPeriod):
						if solution[i] != 0:
							fitnessValue -= int(Chromosome.problem.chanOverGrid[item-1][solution[i]-1])
							break
						i += 1

				del manufactItemsPeriods[item-1][0]

			else:
				counterTab[Chromosome.problem.nbItems] += 1
				(tab[Chromosome.problem.nbItems]).append(0)

				del manufactItemsPeriods[Chromosome.problem.nbItems][0]

			del solution[0]
			del itemsRank[0]

			#print("in function 2 : ", solution, itemsRank, tab)

			child = Node()
			child.tab = copy.deepcopy(tab)
			child.branches = copy.deepcopy(branches)

			# i build the chromosome of the child 
			child.chromosome.fitnessValue = Node.getFitnessValue(solution, fitnessValue, branches[0][0][0]-1, len(tab[branches[0][0][0]-1]), currentPeriod)
			solution.insert(0, branches[0][0][0])
			child.chromosome.solution = solution
			child.chromosome.itemsRank = itemsRank
			child.chromosome.manufactItemsPeriods = manufactItemsPeriods

			if branches[0][0][0] == 0:
				child.chromosome.itemsRank.insert(0, 0)
				(child.chromosome.manufactItemsPeriods[Chromosome.problem.nbItems]).insert(0, currentPeriod)
				del child.tab[len(child.tab)-1][len(child.tab[len(child.tab)-1])-1]
				del child.branches[0][0]
			else:
				child.chromosome.itemsRank.insert(0, len(tab[branches[0][0][0]-1]))
				(child.chromosome.manufactItemsPeriods[branches[0][0][0]-1]).insert(0, currentPeriod)
				del child.tab[child.branches[0][0][0]-1][len(self.tab[child.branches[0][0][0]-1])-1]
				del child.branches[0][0]

			#print("in solution : ", solution, tab, itemsRank, child.chromosome.fitnessValue)


			child.currentPeriod = currentPeriod - 1

			'''
			if child.chromosome.fitnessValue != Node.evaluate_bis(list(child.chromosome.solution)):
				print("BREAAAAAAAAAAAAAAAAAAAAAAAAAAAAAK!!!!!!!!!!!!!", Node.evaluate_bis(child.chromosome.solution))
				print(child)
				return []
			'''

			self = copy.deepcopy(child)

			return self.getChild()


	def getChildren(self):

		childrenQueue = []

		for i in range(0, Chromosome.problem.nbItems):

			if self.tab[i] != [] and self.tab[i][len(self.tab[i])-1] >= self._currentPeriod:

				# the child will inherit some values from the parent
				childNode = Node()
				childNode.tab = copy.deepcopy(self.tab)
				childNode.branches = copy.deepcopy(self.branches)
				childNode.branches.insert(0, [])

				# i build the chromosome of the child 
				childNode.chromosome.solution = copy.deepcopy(self.chromosome.solution)
				childNode.chromosome.solution.insert(0, i + 1)
				childNode.chromosome.itemsRank = copy.deepcopy(self.chromosome.itemsRank)
				childNode.chromosome.itemsRank.insert(0, len(self.tab[i]))
				childNode.chromosome.manufactItemsPeriods = copy.deepcopy(self.chromosome.manufactItemsPeriods)
				(childNode.chromosome.manufactItemsPeriods[i]).insert(0, self.currentPeriod)
				childNode.chromosome.fitnessValue = Node.getFitnessValue(self.chromosome.solution, self.chromosome.fitnessValue, i, len(self.tab[i]), self.currentPeriod)


				childNode.currentPeriod = self._currentPeriod - 1
				del childNode.tab[i][len(self.tab[i])-1]
				childrenQueue.append(copy.deepcopy(childNode))

		if self.tab[len(self.tab)-1] != []:

			# the child will inherit some values from the parent
			childNode = Node()
			childNode.tab = copy.deepcopy(self.tab)
			childNode.branches = copy.deepcopy(self.branches)
			childNode.branches.insert(0, [])

			# i build the chromosome of the child
			childNode.chromosome.solution = copy.deepcopy(self.chromosome.solution)
			childNode.chromosome.solution.insert(0, 0)
			childNode.chromosome.itemsRank = copy.deepcopy(self.chromosome.itemsRank)
			childNode.chromosome.itemsRank.insert(0, 0)
			childNode.chromosome.manufactItemsPeriods = copy.deepcopy(self.chromosome.manufactItemsPeriods)
			(childNode.chromosome.manufactItemsPeriods[Chromosome.problem.nbItems]).insert(0, self.currentPeriod)
			childNode.chromosome.fitnessValue = self.chromosome.fitnessValue

			childNode.currentPeriod = self._currentPeriod - 1
			del childNode.tab[len(self.tab)-1][len(childNode.tab[len(self.tab)-1])-1]
			childrenQueue.append(copy.deepcopy(childNode))

		if childrenQueue == []:

			childNode = copy.deepcopy(self)
			childNode.currentPeriod -= 1
			childrenQueue.append(copy.deepcopy(childNode))

		childrenQueue.sort()
		return list(reversed(childrenQueue))


	def getFitnessValue(cls, solution, fitnessValue, item, rank, currentPeriod):

		#print("in getFitnessValue : ", solution, fitnessValue, item + 1, rank, currentPeriod)
		if (item + 1) == 0:
			return fitnessValue

		fitnessValue += (Chromosome.problem.deadlineDemandPeriods[item][rank-1] - currentPeriod) * int(Chromosome.problem.holdingGrid[item])

		# then i add the transition cost from the newly produced item to the previous one
		if currentPeriod != Chromosome.problem.nbTimes - 1:

			i = 0
			while i < ((Chromosome.problem.nbTimes - 1) - currentPeriod):
				if solution[i] != 0:
					fitnessValue += int(Chromosome.problem.chanOverGrid[item][solution[i]-1])
					break
				i += 1

		return fitnessValue

	getFitnessValue = classmethod(getFitnessValue)

	
	# added for test, to be removed later
	def evaluate(cls, sol):
			
		solution = list(sol)

		fitnessValue = 0
		# Calculation of all the change-over costs
		itemsRank = [1] * Chromosome.problem.nbItems
		i = 0
		for gene in solution:
			#print("gene : ", gene, " cost : ", Chromosome.getCostof(i, gene, itemsRank[gene-1], solution))
			fitnessValue += Chromosome.getCostof(i, gene, itemsRank[gene-1], solution)
			if gene != 0:
				itemsRank[gene-1] += 1
			i += 1

		return fitnessValue
	evaluate = classmethod(evaluate)

	'''
	def evaluate_bis(cls, sol):
			
		if len(sol) != Chromosome.problem.nbTimes:
			for i in range(0, Chromosome.problem.nbTimes - len(sol)):
				sol.insert(0,0)

		solution = list(sol)

		fitnessValue = 0
		itemsRank = []
		# Calculation of all the change-over costs
		for j in range(0, Chromosome.problem.nbItems):
			itemsRank.append(len(Chromosome.problem.deadlineDemandPeriods[j]))

		i = 0
		for gene in solution:
			#print("gene : ", gene, " cost : ", Chromosome.getCostof(i, gene, itemsRank[gene-1], solution))
			fitnessValue += Chromosome.getCostof(i, gene, itemsRank[gene-1], solution)
			if gene != 0:
				itemsRank[gene-1] -= 1
			i += 1

		return fitnessValue
	evaluate_bis = classmethod(evaluate_bis)
	'''


	def _get_currentPeriod(self):
		return self._currentPeriod

	def _set_currentPeriod(self, new_value):
		self._currentPeriod = new_value

	def _get_solution(self):
		return self.chromosome.solution

	def _set_solution(self, new_value):
		# TODO
		pass
		#self.chromosome.solution = list(new_value)
	
	def __lt__(self, node):

		return self.chromosome.fitnessValue < node.chromosome.fitnessValue

	# Properties
	currentPeriod = property(_get_currentPeriod, _set_currentPeriod)
	solution = property(_get_solution, _set_solution)

class AdvMutateNode(object):

	"""docstring for AdvMutateNode"""
	def __init__(self, chromosome):
		super(AdvMutateNode, self).__init__()
		#self.arg = arg

		self.chromosome = copy.deepcopy(chromosome)
		#self.path = []

	def isLeaf(self):
		if self.currentItem == 0:
			return True
		return False

	def getChild(self):

		i = Chromosome.problem.nbTimes - 1
		while i >= 0:

			if self.chromosome.solution[i] != 0:

				deadlineItem = Chromosome.problem.deadlineDemandPeriods[self.chromosome.solution[i]-1][self.chromosome.itemsRank[i]-1]

				j = deadlineItem
				while j > i:

					if self.chromosome.solution[j] != self.chromosome.solution[i]:

						c = Chromosome()
						c.solution = switchGenes(self.chromosome.solution, i, j)
						c.itemsRank = switchGenes(self.chromosome.itemsRank, i, j)

						'''
						# TODO : To revamp
						c.manufactItemsPeriods = copy.deepcopy(self.chromosome.manufactItemsPeriods)
						c.itemsRank = copy.deepcopy(self.chromosome.itemsRank)
						
						del c.manufactItemsPeriods[self.chromosome.solution[i]-1][self.chromosome.itemsRank[i]-1]
						(c.manufactItemsPeriods[self.chromosome.solution[i]-1]).append(j)
						(c.manufactItemsPeriods[self.chromosome.solution[i]-1]).sort()

						del c.manufactItemsPeriods[self.chromosome.solution[j]-1][self.chromosome.itemsRank[j]-1]
						(c.manufactItemsPeriods[self.chromosome.solution[j]-1]).append(i)
						(c.manufactItemsPeriods[self.chromosome.solution[j]-1]).sort()

						indice = 1
						for period in c.manufactItemsPeriods[self.chromosome.solution[i]-1]:
							c.itemsRank[period] = indice
							indice += 1

						if self.chromosome.solution[j] != 0:

							indice = 1
							for period in c.manufactItemsPeriods[self.chromosome.solution[j]-1]:
								c.itemsRank[period] = indice
								indice += 1

						else:
							c.itemsRank[i] = 0
						'''

						c.fitnessValue = AdvMutateNode.evalSwitchedChrom(self.chromosome.solution, self.chromosome.fitnessValue, self.chromosome.itemsRank, i, j)
						if c.fitnessValue < self.chromosome.fitnessValue:
							return AdvMutateNode(c)

					j -= 1

			i -= 1 
		
		return []

	def evalSwitchedChrom(cls, solution, fitnessValue, itemsRank, indice1, indice2):

		#print("ok")
		# i set the value of the period of "indice" to 0
		# i decrease the overall cost of the cost of the first item to be switched
		fitnessValue -= Chromosome.getCostof(indice1, solution[indice1], itemsRank[indice1], solution)
		prevItem1, prevIndice1 = getPrevItem(solution, indice1)
		nextItem1, nextIndice1 = getNextItem(solution, Chromosome.problem.nbTimes, indice1)

		#print("deadlineItem : ", Chromosome.problem.deadlineDemandPeriods[solution[indice1]-1][itemsRank[indice1]-1], Chromosome.getCostof(indice1, solution[indice1], itemsRank[indice1], solution))
		prevItem2, prevIndice2 = getPrevItem(solution, indice2)
		nextItem2, nextIndice2 = getNextItem(solution, Chromosome.problem.nbTimes, indice2)

		#print("eval 1 : ", fitnessValue)
		# and increase it of the cost of the new gene value
		if solution[indice2] != 0:
			fitnessValue += (Chromosome.problem.deadlineDemandPeriods[solution[indice2]-1][itemsRank[indice2]-1] - indice1) * int(Chromosome.problem.holdingGrid[solution[indice2]-1])
			fitnessValue += int(Chromosome.problem.chanOverGrid[prevItem1-1][solution[indice2]-1])

		if nextItem1 != 0 and nextIndice1 != 0:
			fitnessValue -= int(Chromosome.problem.chanOverGrid[solution[indice1]-1][nextItem1-1])
			if solution[indice2] != 0:
				fitnessValue += int(Chromosome.problem.chanOverGrid[solution[indice2]-1][nextItem1-1])
			else:
				fitnessValue += int(Chromosome.problem.chanOverGrid[prevItem1-1][nextItem1-1])

		#print("eval 2 : ", fitnessValue)
		# i do the same for the second item to be swiched
		if nextItem1 == solution[indice2] and nextIndice1 == indice2:

			fitnessValue -= (Chromosome.problem.deadlineDemandPeriods[solution[indice2]-1][itemsRank[indice2]-1] - indice2) * int(Chromosome.problem.holdingGrid[solution[indice2]-1])

			# and increase it of the cost of the new gene value
			fitnessValue += (Chromosome.problem.deadlineDemandPeriods[solution[indice1]-1][itemsRank[indice1]-1] - indice2) * int(Chromosome.problem.holdingGrid[solution[indice1]-1])
			fitnessValue += int(Chromosome.problem.chanOverGrid[solution[indice2]-1][solution[indice1]-1])

		else:

			fitnessValue -= Chromosome.getCostof(indice2, solution[indice2], itemsRank[indice2], solution)
			fitnessValue += (Chromosome.problem.deadlineDemandPeriods[solution[indice1]-1][itemsRank[indice1]-1] - indice2) * int(Chromosome.problem.holdingGrid[solution[indice1]-1])
			#print("eval 3 : ", fitnessValue)
			if solution[indice2] == 0:

				empty = True
				for i in range(indice1 + 1, indice2):
					if solution[i] != 0:
						empty = False

				if empty:
					fitnessValue += int(Chromosome.problem.chanOverGrid[prevItem1-1][solution[indice1]-1])
				else:
					#print("not empty : ", int(Chromosome.problem.chanOverGrid[prevItem2-1][solution[indice1]-1]), nextItem1, solution[indice1])
					fitnessValue += int(Chromosome.problem.chanOverGrid[prevItem2-1][solution[indice1]-1])

			else:
				fitnessValue += int(Chromosome.problem.chanOverGrid[prevItem2-1][solution[indice1]-1])
			#print("eval 3 : ", fitnessValue)

		if nextItem2 != 0 and nextIndice2 != 0:
			#print("yo : ", int(Chromosome.problem.chanOverGrid[solution[indice2]-1][nextItem2-1]))
			if solution[indice2] == 0:

				empty = True
				for i in range(indice1 + 1, indice2):
					if solution[i] != 0:
						empty = False

				if empty:
					fitnessValue -= int(Chromosome.problem.chanOverGrid[prevItem1-1][nextItem2-1])
				else:
					fitnessValue -= int(Chromosome.problem.chanOverGrid[prevItem2-1][nextItem2-1])

			else:
				fitnessValue -= int(Chromosome.problem.chanOverGrid[solution[indice2]-1][nextItem2-1])
			#print("eval 4 : ", fitnessValue)
			fitnessValue += int(Chromosome.problem.chanOverGrid[solution[indice1]-1][nextItem2-1])
			#print("eval 5 : ", fitnessValue)
		#fitnessValue -= Chromosome.getCostof(nextIndice, nextItem, itemsRank[nextIndice], solution)
		#print ("nI : ", nextItem, itemsRank[nextIndice] , Chromosome.problem.deadlineDemandPeriods[nextItem-1][1])#[itemsRank[nextIndice]])

		#print(indice1, indice2, prevItem, prevIndice, nextItem, nextIndice)
		return fitnessValue


	def __repr__(self):
		return str(self.chromosome) #+ " / " + str(self.tab) + " / " + str(self.path)

	evalSwitchedChrom = classmethod(evalSwitchedChrom)