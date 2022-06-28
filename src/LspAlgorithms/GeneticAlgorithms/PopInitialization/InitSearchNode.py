from LspAlgorithms.GeneticAlgorithms.Gene import Gene
from LspInputDataReading.LspInputDataInstance import InputDataInstance
from ..Chromosome import Chromosome
import copy
import uuid

class SearchNode(object):
	"""
	"""

	itemsToOrder = None

	def __init__(self, chromosome, period) -> None:
		"""
		"""
		
		self.chromosome = chromosome
		self.period = period
		self.lastPlacedItem = None

		if SearchNode.itemsToOrder is None:
			SearchNode.itemsToOrder = {i: 0 for i in range(InputDataInstance.instance.nItems)}
			# then i append the number of periods where no items are to be ordered
			SearchNode.itemsToOrder[-1] = (InputDataInstance.instance.nPeriods - InputDataInstance.instance.demandsArray.sum())	

		self.itemsToOrder = copy.deepcopy(SearchNode.itemsToOrder)

		self.uuid = uuid.uuid4()



	@classmethod
	def root(cls):
		"""
		"""
		
		chromosome = Chromosome()
		chromosome.dnaArray = [[] for _ in InputDataInstance.instance.demandsArrayZipped]

		# Wrapping the chromosome in the search node for population initialization purpose
		root = SearchNode(chromosome, (InputDataInstance.instance.nPeriods - 1))

		return root


	def children(self):
		"""
		"""
		children = []

		if self.period < 0:
			return children

		for child in self.generateChild():
			children.append(child)

		return children


	def setItemsToOrder(self):
		"""
		"""

		periodDemands = InputDataInstance.instance.itemDemandsPerPeriod[self.period]

		for item in periodDemands:
			self.itemsToOrder[item] += 1

	
	def orderItem(self, item):
		"""
		"""

		node = SearchNode(Chromosome(), self.period - 1)
		node.lastPlacedItem = self.lastPlacedItem # if we guess a priori that nothing has been produced for this period

		dnaArray = copy.deepcopy(self.chromosome.dnaArray)
		additionalCost = 0
		# print("before Start --- ", dnaArray)

		if (item >= 0):

			itemProdPosition = (len(InputDataInstance.instance.demandsArrayZipped[item]) - len(dnaArray[item])) - 1
			gene = Gene(item, self.period, itemProdPosition)
			gene.calculateStockingCost()
			gene.calculateCost()
			additionalCost += gene.cost
			# print("ok --- ", item, self.period, itemProdPosition, gene.cost)

			node.lastPlacedItem = gene.item

			# print("test 1 : ", gene)
			if self.lastPlacedItem != None:
				lastPlacedGene = (dnaArray[self.lastPlacedItem][0])
				lastPlacedGene.prevGene = (item, itemProdPosition)
				lastPlacedGene.calculateChangeOverCost()
				lastPlacedGene.calculateCost()
				additionalCost += lastPlacedGene.changeOverCost
				# print("test 2 : ", lastPlacedGene)

			dnaArray[item].insert(0, gene)

		# setting node's chomosome period
		itemsToOrder = copy.deepcopy(self.itemsToOrder)
		itemsToOrder[item] -= 1

		node.itemsToOrder = itemsToOrder
		
		node.chromosome.dnaArray = dnaArray
		stringIdentifier = copy.deepcopy(self.chromosome.stringIdentifier)
		stringIdentifier.insert(0, item + 1) 
		node.chromosome.stringIdentifier = stringIdentifier
		node.chromosome.cost = self.chromosome.cost + additionalCost

		# print("end Start --- ", dnaArray)
		return node


	def generateChild(self):
		"""
		"""

		if self.period < 0:
			yield None

		self.setItemsToOrder()

		for item, itemCount in self.itemsToOrder.items():
			if itemCount > 0:
				node = self.orderItem(item)
				yield node


	def __repr__(self):
		return str(self.chromosome.stringIdentifier) + " | " + str(self.period) + " | " + str(self.itemsToOrder) + " | " + str(self.chromosome.dnaArray) + "\n"


	def __lt__(self, node):
		return self.chromosome.cost < node.chromosome.cost

	def __eq__(self, node):
		return self.chromosome.stringIdentifier == node.chromosome.stringIdentifier

	def __hash__(self) -> int:
		return hash(self.uuid)
