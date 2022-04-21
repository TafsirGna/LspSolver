from LspAlgorithms.GeneticAlgorithms.Gene import Gene
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
		self.lastPlacedItem = None

		self.itemsToOrder = [0 for _ in range(InputDataInstance.instance.nItems)]
		# then i append the number of periods where no items are to be ordered
		self.itemsToOrder.append((InputDataInstance.instance.nPeriods - InputDataInstance.instance.demandsArray.sum()))

	@classmethod
	def root(cls, inputDataInstance):
		"""
		"""
		
		chromosome = Chromosome()
		chromosome.dnaArray = [[] for _ in InputDataInstance.instance.demandsArrayZipped]

		# Wrapping the chromosome in the search node for population initialization purpose
		root = SearchNode(chromosome, (inputDataInstance.nPeriods - 1))

		return root

	def children(self):
		"""
		"""

		children = []

		if self.period < 0: # the node is a leaf node
			# print("Leaf --> ", Chromosome.classRenderDnaArray(self.chromosome.dnaArray), '---', self.chromosome.dnaArray, self.chromosome.cost)
			# print("---------------------------------------------------------------------------------")
			return children
		
		periodDemands = InputDataInstance.instance.itemDemandsPerPeriod[self.period]

		for item in periodDemands:
			self.itemsToOrder[item] += 1

		# print("Parent --> ", Chromosome.classRenderDnaArray(self.chromosome.dnaArray), '            ', self.chromosome.dnaArray, self.chromosome.cost)

		for item, itemCount in enumerate(self.itemsToOrder):

			itemsToOrder = None

			if itemCount > 0:

				node = SearchNode(Chromosome(), self.period - 1)
				node.lastPlacedItem = self.lastPlacedItem # if we guess a priori that nothing has been produced for this period

				dnaArray = copy.deepcopy(self.chromosome.dnaArray)
				cost = 0
				# print("ok Start --- ", dnaArray)

				if (item < InputDataInstance.instance.nItems):

					itemProdPosition = (len(InputDataInstance.instance.demandsArrayZipped[item]) - len(dnaArray[item])) - 1
					gene = Gene(item, self.period, itemProdPosition)
					gene.calculateStockingCost()
					gene.calculateCost()
					cost += gene.cost
					# print("ok --- ", item, self.period, itemProdPosition, gene.cost)
					dnaArray[item].insert(0, gene)

					node.lastPlacedItem = gene.item

					if self.lastPlacedItem != None:
						lastPlacedGene = (dnaArray[self.lastPlacedItem][0])
						lastPlacedGene.prevGene = item, itemProdPosition
						lastPlacedGene.calculateChangeOverCost()
						lastPlacedGene.calculateCost()
						cost += lastPlacedGene.changeOverCost

				# setting node's chomosome period
				itemsToOrder = copy.deepcopy(self.itemsToOrder)
				itemsToOrder[item] -= 1

				node.itemsToOrder = itemsToOrder
				
				node.chromosome.dnaArray = dnaArray
				node.chromosome.stringIdentifier = str(item + 1 if item < InputDataInstance.instance.nItems else 0) + self.chromosome.stringIdentifier
				# print(node.chromosome.stringIdentifier)
				node.chromosome.cost = (self.chromosome.cost + cost) 

				# print("ok End --- ", dnaArray)

				children.append(node)

		children.sort(reverse=True)

		return children

	def __repr__(self):
		return str(self.chromosome.stringIdentifier) + " | " + str(self.period) + " | " + str(self.itemsToOrder) + " | " + str(self.chromosome.dnaArray) + "\n"


	def __lt__(self, node):
		return self.chromosome.cost < node.chromosome.cost

	def __eq__(self, node):
		return self.chromosome.stringIdentifier == node.chromosome.stringIdentifier
