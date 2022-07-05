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

        self.offspringsItemsToOrder = {0: set(), 1: set()}
        self.offspringsItemsToOrder[0] = {(item, position) for item, itemDemands in enumerate(InputDataInstance.instance.demandsArrayZipped) for position in range(len(itemDemands))} 
        nZeros = InputDataInstance.instance.nPeriods - InputDataInstance.instance.demandsArray.sum()
        # print("nZeros : ", nZeros)
        self.offspringsItemsToOrder[0] = self.offspringsItemsToOrder[0].union({(-1, i) for i in range(nZeros)})
        self.offspringsItemsToOrder[1] = copy.deepcopy(self.offspringsItemsToOrder[0])

        self.primeParent = self.parentChromosomes[0] if self.parentChromosomes[0] < self.parentChromosomes[1] else self.parentChromosomes[1]

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
        print("Crossover : ", self.parentChromosomes, self.parentChromosomes[0].genesByPeriod, self.parentChromosomes[1].genesByPeriod)

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

        # looping
        print("crossOverPeriod : ", self.crossOverPeriod)
        # self.crossOverPeriod = 4
        self.offspringLastPlacedGene = {0: None, 1: None}

        self.offsprings[0].stringIdentifier = ["*"] * InputDataInstance.instance.nPeriods
        self.offsprings[1].stringIdentifier = ["*"] * InputDataInstance.instance.nPeriods

        self.setOffsprings()

        self.offsprings[0].stringIdentifier = tuple(self.offsprings[0].stringIdentifier)
        self.offsprings[1].stringIdentifier = tuple(self.offsprings[1].stringIdentifier)


        if self.offsprings[0].dnaArray != Chromosome.createFromIdentifier(self.offsprings[0].stringIdentifier).dnaArray:
            print(" Watch out 0", self.offsprings[0].dnaArray, self.offsprings[0].cost)

        if self.offsprings[1].dnaArray != Chromosome.createFromIdentifier(self.offsprings[1].stringIdentifier).dnaArray:
            print(" Watch out 1", self.offsprings[1].dnaArray)

        # print("Cross Over result : ", [self.parentChromosomes, self.offsprings])

        # storing this result in the crossover memory before returning 
        # with CrossOverNode.crossOverMemory["lock"]:
        #     CrossOverNode.crossOverMemory["db"][((self.parentChromosomes[0]).stringIdentifier, (self.parentChromosomes[1]).stringIdentifier, crossOverPeriod)] = tuple(self.offsprings.values())

        return tuple(self.offsprings.values())



    def setOffsprings(self):
        """
        """

        # first, let's remove present dual genes
        itemsCounter = {0: None, 1: None}
        itemsCounter[0] = {item: len(InputDataInstance.instance.demandsArrayZipped[item]) for item in range(InputDataInstance.instance.nItems)} 
        itemsCounter[1] = copy.deepcopy(itemsCounter[0])

        for period in reversed(range(InputDataInstance.instance.nPeriods)):

            self.handleFirstSetOffspring(0, period, itemsCounter)

            self.handleFirstSetOffspring(1, period, itemsCounter)

        # Second, let's attempt to add missing genes

        itemsCounter[0] = {item: len(InputDataInstance.instance.demandsArrayZipped[item]) for item in range(InputDataInstance.instance.nItems)} 
        itemsCounter[0][-1] = InputDataInstance.instance.nPeriods - InputDataInstance.instance.demandsArray.sum()
        itemsCounter[1] = copy.deepcopy(itemsCounter[0])
        period = InputDataInstance.instance.nPeriods - 1

        print(self.offsprings, self.offspringsItemsToOrder)

        self.searchFixedOffspring(0, period, itemsCounter, self.offsprings, self.offspringLastPlacedGene, self.offspringsItemsToOrder)

        self.searchFixedOffspring(1, period, itemsCounter, self.offsprings, self.offspringLastPlacedGene, self.offspringsItemsToOrder)


        print(self.offsprings, "\n", self.offspringsItemsToOrder)


    def handleFirstSetOffspring(self, offspringIndex, period, itemsCounter):
        """
        """

        if period >= self.crossOverPeriod:
            parent = self.parentChromosomes[(0 if offspringIndex == 0 else 1)]
            parentPeriodValue = parent.stringIdentifier[period]
            if parentPeriodValue > 0:
                print("genesByPeriod : ", parent.genesByPeriod)
                parentGene = parent.genesByPeriod[period]
                self.offsprings[offspringIndex].stringIdentifier[period] = parentPeriodValue
                self.offsprings[offspringIndex].dnaArray[parentGene.item][parentGene.position] = copy.deepcopy(parentGene)
                self.offsprings[offspringIndex].genesByPeriod[period] = self.offsprings[offspringIndex].dnaArray[parentGene.item][parentGene.position]
                self.offspringsItemsToOrder[offspringIndex].remove((parentGene.item, parentGene.position))
                itemsCounter[offspringIndex][parentGene.item] -= 1
        else:
            parent = self.parentChromosomes[(0 if offspringIndex == 1 else 1)]
            parentPeriodValue = parent.stringIdentifier[period]
            if parentPeriodValue > 0:
                parentGene = parent.genesByPeriod[period]
                if self.offsprings[offspringIndex].dnaArray[parentGene.item][parentGene.position] is None:
                    if parentGene.position == itemsCounter[offspringIndex][parentGene.item] - 1:
                        self.offsprings[offspringIndex].stringIdentifier[period] = parentPeriodValue
                        self.offsprings[offspringIndex].dnaArray[parentGene.item][parentGene.position] = copy.deepcopy(parentGene)
                        self.offsprings[offspringIndex].genesByPeriod[period] = self.offsprings[offspringIndex].dnaArray[parentGene.item][parentGene.position]
                        self.offspringsItemsToOrder[offspringIndex].remove((parentGene.item, parentGene.position))
                        itemsCounter[offspringIndex][parentGene.item] -= 1
                    elif parentGene.position < itemsCounter[offspringIndex][parentGene.item] - 1:
                        if parent == self.primeParent:

                            # cleansing previous productions
                            for gene in self.offsprings[offspringIndex].dnaArray[parentGene.item]:
                                if gene is not None:
                                    self.offsprings[offspringIndex].dnaArray[parentGene.item][gene.position] = None
                                    self.offsprings[offspringIndex].stringIdentifier[gene.period] = 0
                                    self.offspringsItemsToOrder[offspringIndex].add((gene.item, gene.position))
                                    del self.offsprings[offspringIndex].genesByPeriod[gene.period]

                            self.offsprings[offspringIndex].stringIdentifier[period] = parentPeriodValue
                            self.offsprings[offspringIndex].dnaArray[parentGene.item][parentGene.position] = copy.deepcopy(parentGene)
                            self.offsprings[offspringIndex].genesByPeriod[period] = self.offsprings[offspringIndex].dnaArray[parentGene.item][parentGene.position]
                            self.offspringsItemsToOrder[offspringIndex].remove((parentGene.item, parentGene.position))
                            itemsCounter[offspringIndex][parentGene.item] = parentGene.position

                else:
                    offspringGene = self.offsprings[offspringIndex].dnaArray[parentGene.item][parentGene.position]
                    if parent == self.primeParent:
                        self.offsprings[offspringIndex].stringIdentifier[offspringGene.period] = "*"
                        self.offsprings[offspringIndex].stringIdentifier[period] = parentPeriodValue
                        offspringGene.period = period



    def searchFixedOffspring(self, offspringIndex, period, itemsCounter, offsprings, offspringLastPlacedGene, offspringsItemsToOrder):
        """
        """

        if period == -1:
            print("offspringIndex : ", offspringIndex, offsprings[offspringIndex], offspringsItemsToOrder[offspringIndex])
            Chromosome.evalAndFixDnaArray(offsprings[offspringIndex])
            self.offsprings[offspringIndex] = offsprings[offspringIndex]
            self._stopSearchEvents[offspringIndex].set()
            return None

        if offsprings[offspringIndex].stringIdentifier[period] == "*":
            items = self.arrangeSearchNextMoves(offspringIndex, period, itemsCounter, offsprings, offspringLastPlacedGene, offspringsItemsToOrder)

            if itemsCounter[offspringIndex][-1] > 0:
                items.append(-1)

            for item in items:
                itemsCounterCopy = copy.deepcopy(itemsCounter)
                offspringsCopy = copy.deepcopy(offsprings)
                offspringLastPlacedGeneCopy = copy.deepcopy(offspringLastPlacedGene)
                offspringsItemsToOrderCopy = copy.deepcopy(offspringsItemsToOrder)
                self.orderItem(offspringIndex = offspringIndex, item = item, period = period, itemsCounter = itemsCounterCopy, offsprings = offspringsCopy, offspringLastPlacedGene = offspringLastPlacedGeneCopy, offspringsItemsToOrder = offspringsItemsToOrderCopy)
                period -= 1
                self.searchFixedOffspring(offspringIndex, period, itemsCounterCopy,  offspringsCopy, offspringLastPlacedGeneCopy, offspringsItemsToOrderCopy)
                if self._stopSearchEvents[offspringIndex].is_set():
                    return None
        else:
            itemsCounterCopy = copy.deepcopy(itemsCounter)
            offspringsCopy = copy.deepcopy(offsprings)
            offspringsItemsToOrderCopy = copy.deepcopy(offspringsItemsToOrder)
            offspringLastPlacedGeneCopy = copy.deepcopy(offspringLastPlacedGene)
            offspringLastPlacedGeneCopy[offspringIndex] = offsprings[offspringIndex].genesByPeriod[period]
            itemsCounterCopy[offspringIndex][offsprings[offspringIndex].stringIdentifier[period] - 1] -= 1
            period -= 1
            # self.scoreOffspringPeriodItem(offspringIndex, period)
            self.searchFixedOffspring(offspringIndex, period, itemsCounterCopy, offspringsCopy, offspringLastPlacedGeneCopy, offspringsItemsToOrderCopy)
            if self._stopSearchEvents[offspringIndex].is_set():
                    return None


    def arrangeSearchNextMoves(self, offspringIndex, period, itemsCounter, offsprings, offspringLastPlacedGene, offspringsItemsToOrder):
        """
        """

        items = [item for item in itemsCounter[offspringIndex] if item >= 0 and itemsCounter[offspringIndex][item] > 0 and InputDataInstance.instance.demandsArrayZipped[item][itemsCounter[offspringIndex][item] - 1] >= period and (item, itemsCounter[offspringIndex][item] - 1) in offspringsItemsToOrder[offspringIndex]]
            
        itemsCost = sorted([ \
                        ( \
                            item, \
                            InputDataInstance.instance.stockingCostsArray[item] * (InputDataInstance.instance.demandsArrayZipped[item][itemsCounter[offspringIndex][item] - 1] - period) \
                            + InputDataInstance.instance.changeOverCostsArray[item][offspringLastPlacedGene[offspringIndex].item] \
                            + (0 if offsprings[offspringIndex].stringIdentifier[period - 1] in ["*", 0] else InputDataInstance.instance.changeOverCostsArray[offsprings[offspringIndex].stringIdentifier[period - 1] - 1][item])
                        ) \
                        for item in items \
        ], key= lambda pair: pair[1])

        items = [pair[0] for pair in itemsCost]

        return items


    def orderItem(self, offspringIndex, item, period, itemsCounter, offsprings, offspringLastPlacedGene, offspringsItemsToOrder):
        """
        """

        # items to order
        itemsCounter[offspringIndex][item] -= 1

        # stringIdentifier
        offsprings[offspringIndex].stringIdentifier[period] = item + 1
        offspringsItemsToOrder[offspringIndex].remove((item, itemsCounter[offspringIndex][item]))

        if item != -1:
            position = itemsCounter[offspringIndex][item]

            # dnaArray
            gene = Gene(item, period, position)
            gene.calculateStockingCost()
            gene.calculateCost()

            offsprings[offspringIndex].dnaArray[item][position] = gene
            offspringLastPlacedGene[offspringIndex] = gene

            return gene

        return None

