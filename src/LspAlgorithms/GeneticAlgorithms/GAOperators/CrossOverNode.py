import copy
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.Gene import Gene
from LspInputDataReading.LspInputDataInstance import InputDataInstance
import random

class CrossOverNode:
    """
    """

    itemsToOrder = None

    def __init__(self, parentChromosomes) -> None:
        """
        """
        
        self.parentChromosomes = parentChromosomes
        self.chromosome = Chromosome()

        self.blankPeriods = []
        self.prevBlankPeriod = None
        self.lastPlacedItem = None

        if CrossOverNode.itemsToOrder is None:
            CrossOverNode.itemsToOrder = [[len(itemDemands), len(itemDemands) - 1] for itemDemands in InputDataInstance.instance.demandsArrayZipped] + [[InputDataInstance.instance.nPeriods - InputDataInstance.instance.demandsArray.sum(), None]]


    def prepSearch(self):
        """all the genes that have the same period on both chromosomes, are replicated on the result chromosome
        """

        self.chromosome.stringIdentifier = '*' * InputDataInstance.instance.nPeriods
        self.itemsToOrder = copy.deepcopy(CrossOverNode.itemsToOrder)
        # print("itemsToOrder before : ", self.itemsToOrder)

        positionReckoning = True
        for period in reversed(range(InputDataInstance.instance.nPeriods)):
            item = (self.parentChromosomes[0]).stringIdentifier[period]
            sameItem = True
            for chromosome in self.parentChromosomes:
                if chromosome.stringIdentifier[period] != item:
                    sameItem = False
            if sameItem:
                self.chromosome.stringIdentifier = self.chromosome.stringIdentifier[:period] + str(item) + self.chromosome.stringIdentifier[period + 1:]
                if int(item) != 0:
                    item0 = int(item) - 1
                    self.itemsToOrder[item0][0] -= 1
                    if positionReckoning:
                        # Gene
                        self.addGene(item0, period, self.itemsToOrder[item0][1])
                        self.itemsToOrder[item0][1] -= 1
                else:
                    self.itemsToOrder[-1][0] -= 1      
            else:
                # self.blankPeriods.append(period)
                self.blankPeriods.insert(0, period)
                positionReckoning = False

        # print("Result id : ", self.parentChromosomes, "\n ---",self.chromosome.stringIdentifier, self.blankPeriods, self.itemsToOrder, self.chromosome.dnaArray)


    def children(self):
        """
        """

        children = []

        for child in self.generateChild():
            children.append(child)

        return children


    def addGene(self, item0, period, position):
        """
        """

        gene = Gene(item0, period, position)
        # print(item0, period, position)
        gene.calculateStockingCost()
        gene.calculateCost()
        if self.lastPlacedItem is not None:
            lastPlacedGene = (self.chromosome.dnaArray[self.lastPlacedItem[0]][self.lastPlacedItem[1]])
            lastPlacedGene.prevGene = (item0, position)
            lastPlacedGene.calculateChangeOverCost()
            lastPlacedGene.calculateCost()
            # print(" **************** last gene", lastPlacedGene, lastPlacedGene.cost)

        self.chromosome.dnaArray[item0][position] = gene
        self.lastPlacedItem = (item0, position)
        # print("fais moi tourner la tête", self.lastPlacedItem)



    def catchUpLeftOrders(self):
        """
        """

        period = self.blankPeriods[-1]
        # print("pepe : ", period, period + 1 , self.prevBlankPeriod, self.chromosome.stringIdentifier[period + 1:self.prevBlankPeriod])

        if self.prevBlankPeriod is not None:
            for index, itemValue in enumerate(reversed(self.chromosome.stringIdentifier[period + 1:self.prevBlankPeriod])):
                # print("titi : ", itemValue, index)
                periodValue = (self.prevBlankPeriod - 1) - index
                itemValue = int(itemValue)
                if itemValue != 0:
                    item0 = itemValue - 1
                    position = self.itemsToOrder[item0][1]
                    self.addGene(item0, periodValue, position)
                    self.itemsToOrder[item0][1] -= 1
                else:
                    self.itemsToOrder[-1][0] -= 1


    def generateChild(self):
        """
        """

        # print("koko", self.blankPeriods, "|", self.itemsToOrder)
        if len(self.blankPeriods) == 0:
            if self.prevBlankPeriod > 0:
                self.blankPeriods.insert(0, -1)
                self.catchUpLeftOrders() 
            yield None

        self.catchUpLeftOrders()

        period = self.blankPeriods[-1]
        for item, itemData in enumerate(self.itemsToOrder):
            node = None
            if item < InputDataInstance.instance.nItems: 
                # print("koko 2", item)
                if itemData[0] > 0 and InputDataInstance.instance.demandsArrayZipped[item][itemData[1]] >= period:
                    stringIdentifier = self.chromosome.stringIdentifier[:period] + str(item + 1) + self.chromosome.stringIdentifier[period + 1:]
                    blankPeriods = copy.deepcopy(self.blankPeriods)
                    blankPeriods = blankPeriods[:-1]
                    itemsToOrder = copy.deepcopy(self.itemsToOrder)
                    itemsToOrder[item][0] -= 1
                    itemsToOrder[item][1] -= 1

                    node = CrossOverNode(self.parentChromosomes)
                    node.chromosome.stringIdentifier = stringIdentifier
                    # dna array
                    # print("kitoko")
                    self.addGene(item, period, self.itemsToOrder[item][1])
                    dnaArray = copy.deepcopy(self.chromosome.dnaArray)
                    node.chromosome.dnaArray = dnaArray
                    node.blankPeriods = blankPeriods
                    node.prevBlankPeriod = period
                    node.itemsToOrder = itemsToOrder
                    node.lastPlacedItem = self.lastPlacedItem

            else: # if zero
                stringIdentifier = self.chromosome.stringIdentifier[:period] + str(0) + self.chromosome.stringIdentifier[period + 1:]
                blankPeriods = copy.deepcopy(self.blankPeriods)
                blankPeriods = blankPeriods[:-1]
                itemsToOrder = copy.deepcopy(self.itemsToOrder)
                itemsToOrder[-1][0] -= 1

                node = CrossOverNode(self.parentChromosomes)
                node.chromosome.stringIdentifier = stringIdentifier
                dnaArray = copy.deepcopy(self.chromosome.dnaArray)
                node.chromosome.dnaArray = dnaArray
                node.blankPeriods = blankPeriods
                node.prevBlankPeriod = period
                node.itemsToOrder = itemsToOrder
                node.lastPlacedItem = self.lastPlacedItem

            if node is None:
                continue
            yield node

        yield None
            

        
    def __repr__(self):
        return "{}".format(self.chromosome)

    def __lt__(self, node):
        return self.chromosome.cost < node.chromosome.cost

    def __eq__(self, node):
        return self.chromosome == node.chromosome