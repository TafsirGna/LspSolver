from LspInputDataReading.LspInputDataInstance import InputDataInstance
from ..Chromosome import Chromosome
import copy

class SearchNode(object):
	"""
	"""

	def __init__(self, chromosome, period) -> None:
		"""
		"""
		
		self.chromosome = chromosome
		self.period = period
		self.itemsToOrder = [0 for i in range(InputDataInstance.instance.nItems)]
		self.lastPlacedItem = None

		# then i append the number of periods where no items are to be ordered
		self.itemsToOrder.append((InputDataInstance.instance.nPeriods - InputDataInstance.instance.demandsArray.sum()))

	@classmethod
	def root(cls, inputDataInstance):
		"""
		"""
		
		chromosome = Chromosome([0 for i in range(InputDataInstance.instance.nPeriods)])
		chromosome.cost = 0

		# Wrapping the chromosome in the search node for population initialization purpose
		root = cls(chromosome, (inputDataInstance.nPeriods - 1))

		return root

	def children(self):
		"""
		"""

		if self.period < 0: # the node is a leaf node
			return []

		children = []
		
		periodDemands = InputDataInstance.instance.demandsArray[:,self.period]
		# print('pepe ', periodDemands)

		for index, item in enumerate(periodDemands):
			if item == 1:
				self.itemsToOrder[index] += 1

		# print("Parent --> ", self.chromosome)

		for index, item in enumerate(self.itemsToOrder):

			itemsToOrder = None

			if item > 0:

				dnaArrayZipped = [[j for j in row] for row in self.chromosome.dnaArrayZipped]

				#Calculating the node's chromosome cost
				# first change over costs
				changeOverCost = 0
				if self.lastPlacedItem and index < InputDataInstance.instance.nItems :
					changeOverCost += InputDataInstance.instance.chanOverArray[index, self.lastPlacedItem - 1]

				# next stocking costs and others
				stockingCost = 0
				if index < InputDataInstance.instance.nItems:

					# dnaArrayZipped[index].append(self.period)
					dnaArrayZipped[index].insert(0, self.period)
					indexItem = (len(InputDataInstance.instance.demandsArrayZipped[index]) - len(self.chromosome.dnaArrayZipped[index])) - 1
					stockingCost = (InputDataInstance.instance.demandsArrayZipped[index][indexItem] - self.period) * InputDataInstance.instance.stockingCostsArray[index]
					# print('-------------', stockingCost)


				# setting node's chomosome period
				itemsToOrder = [i for i in self.itemsToOrder]
				itemsToOrder[index] -= 1

				node = SearchNode(Chromosome(), self.period - 1)
				node.itemsToOrder = itemsToOrder

				# setting lastPlacedItem property
				if (index == InputDataInstance.instance.nItems):
					node.lastPlacedItem = self.lastPlacedItem
				else:
					node.lastPlacedItem = index + 1

				node.chromosome.cost = (self.chromosome.cost + changeOverCost + stockingCost) # adding the changeOver cost and the stocking cost 
				node.chromosome.dnaArrayZipped = dnaArrayZipped

				children.append(node)

		children.sort(reverse=True)

		return children

	def __repr__(self):
		return str(self.chromosome.unzipDnaArray()) + " | " + str(self.period) + " | " + str(self.itemsToOrder) + " | " + str(self.chromosome.dnaArrayZipped) + "\n"


	def __lt__(self, node):
		return self.chromosome.cost < node.chromosome.cost

	def __eq__(self, node):
		return self.chromosome.dnaArrayZipped < node.chromosome.dnaArrayZipped
