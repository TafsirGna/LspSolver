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

        self.blankPeriods = [period for period in range(InputDataInstance.instance.nPeriods)]
        # self.prevBlankPeriod = None
        # self.lastPlacedItem = None

        if CrossOverNode.itemsToOrder is None:
            CrossOverNode.itemsToOrder = {item: [position for position in range(len(InputDataInstance.instance.demandsArrayZipped[item]))] for item in range(InputDataInstance.instance.nItems)} 
            CrossOverNode.itemsToOrder[-1] = [InputDataInstance.instance.nPeriods - InputDataInstance.instance.demandsArray.sum()]


    def prepSearch(self):
        """All the genes that have the same period on both chromosomes, are replicated on the result chromosome
        """

        self.chromosome.stringIdentifier = ['*'] * InputDataInstance.instance.nPeriods
        self.itemsToOrder = copy.deepcopy(CrossOverNode.itemsToOrder)
        # print("itemsToOrder before : ", self.itemsToOrder)

        # tracking all common produced items
        for item in range(InputDataInstance.instance.nItems):
            for position in range(len(InputDataInstance.instance.demandsArrayZipped[item])):
                period = (self.parentChromosomes[0].dnaArray[item][position]).period
                same = True
                for chromosome in self.parentChromosomes:
                    if (chromosome.dnaArray[item][position]).period != period:
                        same = False
                        break
                if same:
                    self.chromosome.dnaArray[item][position] = copy.deepcopy(self.parentChromosomes[0].dnaArray[item][position])
                    self.chromosome.stringIdentifier[period] = item + 1
                    self.blankPeriods.remove(period)
                    self.itemsToOrder[item].remove(position)


        # tracking all common zeros
        blankPeriods = copy.deepcopy(self.blankPeriods)
        for period in blankPeriods:
            item0 = self.parentChromosomes[0].stringIdentifier[period]
            if item0 != 0:
                continue
            
            same = True
            for chromosome in self.parentChromosomes:
                if chromosome.stringIdentifier[period] != item0:
                    same = False
            
            if same:
                self.chromosome.stringIdentifier[period] = item0 
                self.blankPeriods.remove(period)
                self.itemsToOrder[-1][0] -= 1



        print("Result id : ", self.parentChromosomes, "\n --- ",self.chromosome.stringIdentifier, self.blankPeriods, self.itemsToOrder, self.chromosome.dnaArray)


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
        
        # lastPlacedGene = (self.chromosome.dnaArray[self.lastPlacedItem[0]][self.lastPlacedItem[1]])
        # # print(" **************** last gene", self.lastPlacedItem, self.prevBlankPeriod, lastPlacedGene, self.chromosome.dnaArray)
        # lastPlacedGene.prevGene = (item0, position)
        # lastPlacedGene.calculateChangeOverCost()
        # lastPlacedGene.calculateCost()

        self.chromosome.dnaArray[item0][position] = gene
        # self.lastPlacedItem = (item0, position)
        # print("prou ", self.lastPlacedItem)


    def generateChild(self, stopEvent = None):
        """
        """

        if stopEvent is not None and stopEvent.is_set():
            yield None

        # print("koko", self.blankPeriods, "|", self.itemsToOrder)
        if len(self.blankPeriods) == 0:
            # self.chromosome = Chromosome.evaluateDnaArray(self.chromosome.dnaArray)
            yield self

        period = self.blankPeriods[0]
        itemsToOrderKeys = list(self.itemsToOrder.keys())
        random.shuffle(itemsToOrderKeys)
        for item in itemsToOrderKeys:
            itemDemands = self.itemsToOrder[item]
            node = None
            if item >= 0: 
                # print("koko-2", item, itemData)
                if len(itemDemands) > 0:
                    # upper limit
                    upperLimit = None
                    if itemDemands[0] == len(InputDataInstance.instance.demandsArrayZipped[item]) - 1:
                        upperLimit = InputDataInstance.instance.demandsArrayZipped[item][itemDemands[0]]
                    else:
                        if self.chromosome.dnaArray[item][itemDemands[0] + 1] is None:
                            upperLimit = InputDataInstance.instance.demandsArrayZipped[item][itemDemands[0]]
                        else:
                            upperLimit = (self.chromosome.dnaArray[item][itemDemands[0] + 1]).period - 1
                            upperLimit = upperLimit if upperLimit < InputDataInstance.instance.demandsArrayZipped[item][itemDemands[0]] else InputDataInstance.instance.demandsArrayZipped[item][itemDemands[0]]

                    # lower limit
                    lowerLimit = -1 if itemDemands[0] == 0 else (self.chromosome.dnaArray[item][itemDemands[0] - 1]).period
                    if lowerLimit < period and period <= upperLimit:
                        node = self.orderItem(item, period)

            else: # if zero
                if self.itemsToOrder[-1][0] > 0:
                    node = self.orderItem(item, period)

            if node is None:
                continue
            yield node

        yield None
            

    def orderItem(self, item, period):
        """
        """
        
        stringIdentifier = list(self.chromosome.stringIdentifier)
        stringIdentifier[period] = item + 1
        blankPeriods = copy.deepcopy(self.blankPeriods)
        blankPeriods = blankPeriods[1:]
        itemsToOrder = copy.deepcopy(self.itemsToOrder)

        node = CrossOverNode(self.parentChromosomes)
        node.chromosome.stringIdentifier = stringIdentifier

        # dna array
        if item >= 0:
            self.addGene(item, period, self.itemsToOrder[item][0])
            itemsToOrder[item] = itemsToOrder[item][1:]
        else:
            itemsToOrder[item][0] -= 1

        dnaArray = copy.deepcopy(self.chromosome.dnaArray)
        node.chromosome.dnaArray = dnaArray
        node.blankPeriods = blankPeriods
        # node.prevBlankPeriod = period
        node.itemsToOrder = itemsToOrder
        # node.lastPlacedItem = self.lastPlacedItem
        # print("kitoko", node.chromosome)

        return node
        
    def __repr__(self):
        return "{}".format(self.chromosome)

    def __lt__(self, node):
        return self.chromosome.cost < node.chromosome.cost

    def __eq__(self, node):
        return self.chromosome == node.chromosome