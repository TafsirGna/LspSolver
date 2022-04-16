import copy
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.Gene import Gene
from LspInputDataReading.LspInputDataInstance import InputDataInstance

class CrossOverNode:
    """
    """

    def __init__(self, parentChromosomes, period = None) -> None:
        """
        """
        self.parentChromosomes = parentChromosomes
        self.period = period if period != None else InputDataInstance.instance.nPeriods - 1

        self.chromosome = Chromosome()
        self.chromosome.dnaArray = [[None for _ in indices] for indices in InputDataInstance.instance.demandsArrayZipped]
        self.chromosome.cost = 0

        self.lastPlacedItem = None

        self.itemsToOrder = [[None for _ in indices] for indices in InputDataInstance.instance.demandsArrayZipped]
		# then i append the number of periods where no items are to be ordered
        self.itemsToOrder.append([0])
        self.itemsToOrder[InputDataInstance.instance.nItems].append([0 for _ in self.parentChromosomes])
        # self.itemsToOrder.append([(InputDataInstance.instance.nPeriods - InputDataInstance.instance.demandsArray.sum())])


    def children(self):
        """
        """
        print("Parents ", self.parentChromosomes, self.period)

        children = []

        if self.period < 0: 
            return children

        print("item to order 1 °°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°", self.itemsToOrder)

        for index, chromosome in enumerate(self.parentChromosomes):
            gene = chromosome.geneAtPeriod(self.period)
            if gene is not None:
                if self.itemsToOrder[gene.item][gene.position] == None:
                    self.itemsToOrder[gene.item][gene.position] = 1
            else:
                max1 = max(self.itemsToOrder[InputDataInstance.instance.nItems][1])
                self.itemsToOrder[InputDataInstance.instance.nItems][1][index] += 1
                max2 = max(self.itemsToOrder[InputDataInstance.instance.nItems][1])
                if max2 == max1 + 1:
                    self.itemsToOrder[InputDataInstance.instance.nItems][0] += 1

        print("item to order 2 °°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°", self.itemsToOrder)


        for item in range(InputDataInstance.instance.nItems):

            itemStates = self.itemsToOrder[item]
            for position, itemState in enumerate(itemStates):

                itemsToOrder = None
                if itemState == 1:

                    node = CrossOverNode(self.parentChromosomes, self.period - 1)

                    dnaArray = [[copy.deepcopy(gene) for gene in row] for row in self.chromosome.dnaArray]
                    cost = 0

                    gene = Gene(item, self.period, position)
                    gene.calculateStockingCost()
                    gene.calculateCost()
                    cost += gene.cost
                    # print("ok --- ", item, self.period, itemProdPosition, gene.cost)
                    dnaArray[item][position] = gene

                    node.lastPlacedItem = (gene.item, gene.position)

                    if self.lastPlacedItem != None:
                        lastPlacedGene = (dnaArray[self.lastPlacedItem[0]][self.lastPlacedItem[1]])
                        lastPlacedGene.prevGene = item, position
                        lastPlacedGene.calculateChangeOverCost()
                        lastPlacedGene.calculateCost()
                        cost += lastPlacedGene.changeOverCost


                    # setting node's chomosome period
                    # itemsToOrder = [[value for value in row] for row in self.itemsToOrder]
                    itemsToOrder = copy.deepcopy(self.itemsToOrder)
                    itemsToOrder[item][position] = 0
                    node.itemsToOrder = itemsToOrder

                    node.itemsToOrder = itemsToOrder
                    
                    node.chromosome.dnaArray = dnaArray
                    node.chromosome.cost = (self.chromosome.cost + cost) 

                    print("childreeeeeeeeeeeeeeeeen ", node.chromosome, node.itemsToOrder)

                    children.append(node)


        if self.itemsToOrder[InputDataInstance.instance.nItems][0] > 0:

            node = CrossOverNode(self.parentChromosomes, self.period - 1)
            node.chromosome.dnaArray = [[copy.deepcopy(gene) for gene in row] for row in self.chromosome.dnaArray]
            node.chromosome.cost = self.chromosome.cost
            node.lastPlacedItem = self.lastPlacedItem

            # itemsToOrder = [[value for value in row] for row in self.itemsToOrder]
            # itemsToOrder[InputDataInstance.instance.nItems][0] -= 1
            itemsToOrder = copy.deepcopy(self.itemsToOrder)
            itemsToOrder[InputDataInstance.instance.nItems][0] -= 1
            node.itemsToOrder = itemsToOrder
            
            children.append(node)

        # children.sort(reverse=True)

        print("Children ", children)

        return children

    def __repr__(self):
        return "{}".format(self.chromosome)

    def __lt__(self, node):
        return self.chromosome.cost < node.chromosome.cost

    def __eq__(self, node):
        return self.chromosome.dnaArray == node.chromosome.dnaArray