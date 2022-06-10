import copy
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.Gene import Gene
from LspInputDataReading.LspInputDataInstance import InputDataInstance
import random
import numpy as np
from ParameterSearch.ParameterData import ParameterData

class CrossOverNode:
    """
    """

    def __init__(self, parents, period, index) -> None:
        """
        """
        
        self.parents = parents
        self.chromosome = Chromosome()
        self.period = period
        self.index = index
        self.primary_parent, self.secondary_parent = (parents[0], parents[1])  if self.index == 0 else (parents[1], parents[0])
        
        self.itemsToOrder = {item: len(InputDataInstance.instance.demandsArrayZipped[item]) for item in range(InputDataInstance.instance.nItems)} 
        self.itemsToOrder[-1] = InputDataInstance.instance.nPeriods - InputDataInstance.instance.demandsArray.sum()

        self.chromosome.stringIdentifier = self.primary_parent.stringIdentifier
        self.prepSearchSettings()


    def children(self):
        """
        """

        children = []

        for child in self.generateChild():
            children.append(child)

        return children


    def prepSearchSettings(self):
        """
        """

        # print('itemsToOrder : ', self.chromosome.dnaArray)

        # setting cost too
        self.chromosome.cost = 0

        # and setting the itemsToOrder property
        gene = None
        for index, item in enumerate(reversed(self.primary_parent.stringIdentifier[self.period + 1:])):
            self.itemsToOrder[item - 1] -= 1
            # print(" item ", item)
            if item > 0:
                gene = (Chromosome.geneAtPeriod(self.primary_parent, InputDataInstance.instance.nPeriods - (1 + index)))
                self.chromosome.dnaArray[gene.item][gene.position] = copy.deepcopy(gene)
                self.chromosome.cost += gene.cost

        self.chromosome.cost -= gene.changeOverCost

        # update stringIdentifier
        stringIdentifier = list(self.chromosome.stringIdentifier)
        stringIdentifier[:self.period + 1] = ['*'] * (self.period + 1)
        self.chromosome.stringIdentifier = stringIdentifier

        # print("creating node : ", self.chromosome.stringIdentifier)


    def addGene(self, item0, period, position):
        """
        """

        gene = Gene(item0, period, position)
        # print(item0, period, position, self.chromosome.dnaArray)
        gene.calculateStockingCost()
        gene.calculateCost()

        lastGene = Chromosome.nextProdGene(period, self.chromosome.dnaArray, self.chromosome.stringIdentifier)
        # print("last gene 1 : ", lastGene, (gene.item, gene.position))
        lastGene.prevGene = (gene.item, gene.position)
        lastGene.calculateChangeOverCost()
        lastGene.calculateCost()
        # print("last gene 2 : ", lastGene)

        self.chromosome.dnaArray[item0][position] = gene
        self.chromosome.cost += (gene.cost + lastGene.changeOverCost)


    def generateChild(self):
        """
        """

        if self.period <= -1:
            yield self


        # print("child generation", self.chromosome, self.period, self.itemsToOrder, self.chromosome.dnaArray)
        child = None
        itemsToOrderKeys = list(self.itemsToOrder.keys())

        # handling the parent
        parentGene = Chromosome.geneAtPeriod(self.secondary_parent, self.period)
        if parentGene is None: # period's item is 0
            if self.itemsToOrder[-1] > 0:
                yield self.orderItem(-1, self.period)
        else:
            if self.itemsToOrder[parentGene.item] > 0 and parentGene.position <= (self.itemsToOrder[parentGene.item] - 1):
                # print("..........................................................................")
                yield self.orderItem(parentGene.item, self.period)

                itemsToOrderKeys.remove(parentGene.item)

        random.seed()
        random.shuffle(itemsToOrderKeys)
        for item in itemsToOrderKeys:

            child = None

            if item >= 0: 
                if self.itemsToOrder[item] > 0 and InputDataInstance.instance.demandsArrayZipped[item][self.itemsToOrder[item] - 1] >= self.period:
                    child = self.orderItem(item, self.period)

            else: # if zero
                if self.itemsToOrder[-1] > 0:
                    child = self.orderItem(item, self.period)

            if child is None:
                continue

            # print("child generated", child.chromosome, child.period, child.itemsToOrder, child.chromosome.dnaArray)
            yield child

        yield child
                

    def orderItem(self, item, period):
        """
        """
        
        child = CrossOverNode(self.parents, self.period - 1, self.index)

        stringIdentifier = list(self.chromosome.stringIdentifier)
        stringIdentifier[period] = item + 1
        itemsToOrder = copy.deepcopy(self.itemsToOrder)

        # print("-- ", stringIdentifier, self.period)

        child.chromosome.stringIdentifier = stringIdentifier
        dnaArray = copy.deepcopy(self.chromosome.dnaArray)
        child.chromosome.dnaArray = dnaArray
        child.chromosome.cost = self.chromosome.cost

        # dna array
        if item >= 0:
            child.addGene(item, period, itemsToOrder[item] - 1)
        itemsToOrder[item] -= 1

        child.itemsToOrder = itemsToOrder

        return child
        

    def __repr__(self):
        return "{}".format(self.chromosome)

    def __lt__(self, node):
        return self.chromosome.cost < node.chromosome.cost

    def __eq__(self, node):
        return self.chromosome == node.chromosome