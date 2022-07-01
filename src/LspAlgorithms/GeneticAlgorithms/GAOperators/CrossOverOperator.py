from collections import defaultdict
import random
import threading
# from LspAlgorithms.GeneticAlgorithms.GAOperators.CrossOverNode import CrossOverNode
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspInputDataReading.LspInputDataInstance import InputDataInstance
import concurrent.futures
import copy
from LspAlgorithms.GeneticAlgorithms.Gene import Gene

class CrossOverOperator:
    """
    """

    def __init__(self, parentChromosomes) -> None:
        """
        """

        self.parentChromosomes = parentChromosomes
        self.offsprings = {0: Chromosome(), 1: Chromosome()}

        self.offspringsItemsToOrder = {0: None, 1: None}
        self.offspringsItemsToOrder[0] = {item: len(InputDataInstance.instance.demandsArrayZipped[item]) for item in range(InputDataInstance.instance.nItems)} 
        self.offspringsItemsToOrder[0][-1] = InputDataInstance.instance.nPeriods - InputDataInstance.instance.demandsArray.sum()

        self.offspringsItemsToOrder[1] = {item: len(InputDataInstance.instance.demandsArrayZipped[item]) for item in range(InputDataInstance.instance.nItems)} 
        self.offspringsItemsToOrder[1][-1] = InputDataInstance.instance.nPeriods - InputDataInstance.instance.demandsArray.sum()

        # self.primeParent = self.parentChromosomes[0] if self.parentChromosomes[0] < self.parentChromosomes[1] else self.parentChromosomes[1]

        self._stopSearchEvents = {0: threading.Event(), 1: threading.Event()}


    def process(self, offspring_result = 2):
        """
        """

        if offspring_result not in [1, 2]:
            # TODO: throw an error
            return None, None


        if self.parentChromosomes[0] == self.parentChromosomes[1]:
            return self.parentChromosomes[0], self.parentChromosomes[1]

        # print("Crossover : ", self.parentChromosomes, self.parentChromosomes[0].dnaArray, self.parentChromosomes[1].dnaArray)

        # before launching the recursive search
        gapLength = int(InputDataInstance.instance.nPeriods / 3)
        # random.seed()
        self.crossOverPeriod = random.randint(gapLength + 1, InputDataInstance.instance.nPeriods - (gapLength + 1))

        # checking the crossover memory for previous occurences of this context
        # memoryResult1 = CrossOverNode.crossOverMemory["db"][((self.parentChromosomes[0]).stringIdentifier, (self.parentChromosomes[1]).stringIdentifier, crossOverPeriod)]
        # if  memoryResult1 is not None:
        #     return memoryResult1

        # memoryResult2 = CrossOverNode.crossOverMemory["db"][((self.parentChromosomes[1]).stringIdentifier, (self.parentChromosomes[0]).stringIdentifier, crossOverPeriod)]
        # if memoryResult2 is not None:
        #     return memoryResult2

        # Initializing offsprings' stringIdentifier property
        self.offsprings[0].stringIdentifier = ["*"] * InputDataInstance.instance.nPeriods
        self.offsprings[1].stringIdentifier = ["*"] * InputDataInstance.instance.nPeriods

        # looping
        print("crossOverPeriod : ", self.crossOverPeriod)

        # self.crossOverPeriod = 4
        self.offspringLastPlacedGene = {0: None, 1: None}

        for period in reversed(range(self.crossOverPeriod, InputDataInstance.instance.nPeriods)):

            # First offspring
            self.replicateGene(offspringIndex = 0, parentIndex = 0, period = period)

            # Second offspring
            self.replicateGene(offspringIndex = 1, parentIndex = 1, period = period)


        self.forcastProducedItems()

        # Search offsprings
        self.searchOffspring(0)
        self.searchOffspring(1)


        self.offsprings[0].stringIdentifier = tuple(self.offsprings[0].stringIdentifier)
        self.offsprings[1].stringIdentifier = tuple(self.offsprings[1].stringIdentifier)

        if self.offsprings[0].dnaArray != Chromosome.createFromIdentifier(self.offsprings[0].stringIdentifier).dnaArray:
            print(" Watch out 0", self.offsprings[0].dnaArray, self.offsprings[0].cost)

        if self.offsprings[1].dnaArray != Chromosome.createFromIdentifier(self.offsprings[1].stringIdentifier).dnaArray:
            print(" Watch out 1", self.offsprings[1].dnaArray)

        print("Cross Over result : ", [self.parentChromosomes, self.offsprings])

        # storing this result in the crossover memory before returning 
        # with CrossOverNode.crossOverMemory["lock"]:
        #     CrossOverNode.crossOverMemory["db"][((self.parentChromosomes[0]).stringIdentifier, (self.parentChromosomes[1]).stringIdentifier, crossOverPeriod)] = tuple(self.offsprings.values())

        return tuple(self.offsprings.values())



    def forcastProducedItems(self):
        """
        """

        # just after the crossover tipping period, some tasks need to be done such as
        # if period == self.crossOverPeriod - 1:

        if self.offspringLastPlacedGene[0] is not None:
            self.offsprings[0].cost -= self.offspringLastPlacedGene[0].changeOverCost
        if self.offspringLastPlacedGene[1] is not None:
            self.offsprings[1].cost -= self.offspringLastPlacedGene[1].changeOverCost

        for period in reversed(range(self.crossOverPeriod)):

            if self.offspringsItemsToOrder[0][self.parentChromosomes[1].stringIdentifier[period] - 1] > 0:
                self.replicateGene(offspringIndex = 0, parentIndex = 1, period = period)

            if self.offspringsItemsToOrder[1][self.parentChromosomes[0].stringIdentifier[period] - 1] > 0:
                self.replicateGene(offspringIndex = 1, parentIndex = 0, period = period)
        

    def searchOffspring(self, offspringIndex):
        """
        """
        
        period = self.crossOverPeriod - 1

        self.scoreOffspringPeriodItem(offspringIndex, period)


    def scoreOffspringPeriodItem(self, offspringIndex, period):
        """
        """

        # if offspringIndex == 1:
        #     print("roro : ", self.offsprings[1], period)

        if period == -1:
            cost = Chromosome.evalAndFixDnaArray(self.offsprings[offspringIndex])
            self.offsprings[offspringIndex].cost = cost
            self._stopSearchEvents[offspringIndex].set()
            return None
        
        if self.offsprings[offspringIndex].stringIdentifier[period] == "*":
            # items = [(item, (InputDataInstance.instance.stockingCostsArray[item] * (InputDataInstance.instance.demandsArrayZipped[item][self.offspringsItemsToOrder[offspringIndex][item] - 1] - period)) + (InputDataInstance.instance.changeOverCostsArray[item][self.offspringLastPlacedGene[offspringIndex].item])) for item in self.offspringsItemsToOrder[offspringIndex] if item >= 0 and self.offspringsItemsToOrder[offspringIndex][item] > 0 and InputDataInstance.instance.demandsArrayZipped[item][self.offspringsItemsToOrder[offspringIndex][item] - 1] >= period]
            # print('sorted : ', sorted(items, key= lambda item: item[1]), items, self.offspringsItemsToOrder[0])
            items = [item for item in self.offspringsItemsToOrder[offspringIndex] if item >= 0 and self.offspringsItemsToOrder[offspringIndex][item] > 0 and InputDataInstance.instance.demandsArrayZipped[item][self.offspringsItemsToOrder[offspringIndex][item] - 1] >= period]
            if self.offspringsItemsToOrder[offspringIndex][-1] > 0:
                items.insert(0, -1)

            for item in reversed(items):
                self.orderItem(offspringIndex = offspringIndex, item = item, period = period)
                period -= 1
                self.scoreOffspringPeriodItem(offspringIndex, period)
                if self._stopSearchEvents[offspringIndex].is_set():
                    return None
        else:
            period -= 1
            self.scoreOffspringPeriodItem(offspringIndex, period)
            if self._stopSearchEvents[offspringIndex].is_set():
                    return None


    def checkGeneReplicability(self, offspringIndex, parentIndex, period):
        """
        """

        if self.parentChromosomes[parentIndex].stringIdentifier[period] == 0:
            return True, None
        else:
            parentGene = (Chromosome.geneAtPeriod(self.parentChromosomes[parentIndex], period))
            if parentGene.position == self.offspringsItemsToOrder[offspringIndex][parentGene.item] - 1:
                return True, parentGene

        return False, None


    def replicateGene(self, offspringIndex, parentIndex, period):
        """
        """

        parentItem = self.parentChromosomes[parentIndex].stringIdentifier[period]
        replicate, parentGene = self.checkGeneReplicability(offspringIndex, parentIndex, period)
        
        if replicate:

            self.offsprings[offspringIndex].stringIdentifier[period] = parentItem
            self.offspringsItemsToOrder[offspringIndex][parentItem - 1] -= 1

            if parentItem != 0: # No item has been produced for this period if is none
                gene = copy.deepcopy(parentGene)

                cost = 0
                # print("pro : ", parentItem, cost, offspringIndex, parentIndex)
                if offspringIndex != parentIndex:
                    gene.changeOverCost = 0
                    gene.calculateCost()
                    if self.offspringLastPlacedGene[offspringIndex] is not None:
                        self.offspringLastPlacedGene[offspringIndex].prevGene = (gene.item, gene.position)
                        self.offspringLastPlacedGene[offspringIndex].calculateChangeOverCost()
                        self.offspringLastPlacedGene[offspringIndex].calculateCost()
                        cost += self.offspringLastPlacedGene[offspringIndex].changeOverCost

                cost += gene.cost

                self.offsprings[offspringIndex].dnaArray[parentGene.item][parentGene.position] = gene
                self.offsprings[offspringIndex].cost += cost
                self.offspringLastPlacedGene[offspringIndex] = self.offsprings[offspringIndex].dnaArray[parentGene.item][parentGene.position]
                return self.offsprings[offspringIndex].dnaArray[parentGene.item][parentGene.position]

        return None


    def orderItem(self, offspringIndex, item, period):
        """
        """

        # items to order
        self.offspringsItemsToOrder[offspringIndex][item] -= 1

        # stringIdentifier
        self.offsprings[offspringIndex].stringIdentifier[period] = item + 1

        if item != -1:
            position = self.offspringsItemsToOrder[offspringIndex][item]

            # dnaArray
            gene = Gene(item, period, position)
            gene.calculateStockingCost()
            gene.calculateCost()

            self.offspringLastPlacedGene[offspringIndex].prevGene = (item, position)
            self.offspringLastPlacedGene[offspringIndex].calculateChangeOverCost()
            self.offspringLastPlacedGene[offspringIndex].calculateCost()

            self.offsprings[offspringIndex].dnaArray[item][position] = gene
            self.offsprings[offspringIndex].cost += (gene.cost + self.offspringLastPlacedGene[offspringIndex].changeOverCost)

            self.offspringLastPlacedGene[offspringIndex] = gene

            return gene

        return None
