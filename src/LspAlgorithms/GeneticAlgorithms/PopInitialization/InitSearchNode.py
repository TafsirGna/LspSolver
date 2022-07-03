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
		self.lastPlacedGene = None

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
		node.lastPlacedGene = self.lastPlacedGene # if we guess a priori that nothing has been produced for this period

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

			node.lastPlacedGene = gene

			# print("test 1 : ", gene)
			if self.lastPlacedGene is not None:
				lastPlacedGene = (dnaArray[self.lastPlacedGene.item][0])
				lastPlacedGene.prevGene = (item, itemProdPosition)
				lastPlacedGene.calculateChangeOverCost()
				lastPlacedGene.calculateCost()
				additionalCost += lastPlacedGene.changeOverCost

				gene.nextGene = self.lastPlacedGene
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

		items = self.rateItemsToOrder()

		for item in items:
			node = self.orderItem(item)
			yield node


	def rateItemsToOrder(self):
		"""
		"""

		items = [item for item in self.itemsToOrder if item != -1 and self.itemsToOrder[item] > 0]

		itemsCost = sorted([ \
						( \
							item, \
							InputDataInstance.instance.stockingCostsArray[item] * (InputDataInstance.instance.demandsArrayZipped[item][(len(InputDataInstance.instance.demandsArrayZipped[item]) - len(self.chromosome.dnaArray[item])) - 1] -  self.period) \
							+ (0 if self.lastPlacedGene is None else InputDataInstance.instance.changeOverCostsArray[item][self.lastPlacedGene.item])
						) \
						for item in items \
		], key=lambda pair: pair[1])

		items = [pair[0] for pair in itemsCost]

		if self.itemsToOrder[-1] > 0:
			items.append(-1)

		return items


	def __repr__(self):
		return str(self.chromosome.stringIdentifier) + " | " + str(self.period) + " | " + str(self.itemsToOrder) + " | " + str(self.chromosome.dnaArray) + "\n"


	def __lt__(self, node):
		return self.chromosome.cost < node.chromosome.cost

	def __eq__(self, node):
		return self.chromosome.stringIdentifier == node.chromosome.stringIdentifier

	def __hash__(self) -> int:
		return hash(self.uuid)
