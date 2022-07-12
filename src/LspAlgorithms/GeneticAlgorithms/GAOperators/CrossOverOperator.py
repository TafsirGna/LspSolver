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
        print("Crossover : ", self.parentChromosomes)

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
        # self.crossOverPeriod =  4
        print("crossOverPeriod : ", self.crossOverPeriod)
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
        itemsCounter[0][-1] = InputDataInstance.instance.nPeriods - InputDataInstance.instance.demandsArray.sum()
        itemsCounter[1] = copy.deepcopy(itemsCounter[0])

        subPrimeParent = self.parentChromosomes[0] if self.parentChromosomes[1] == self.primeParent else self.parentChromosomes[1]

        for period in reversed(range(InputDataInstance.instance.nPeriods)):
            self.replicatePrimeParentGene(period, itemsCounter, subPrimeParent)

        # Second, let's attempt to add missing genes

        itemsCounter[0] = {item: len(InputDataInstance.instance.demandsArrayZipped[item]) for item in range(InputDataInstance.instance.nItems)} 
        itemsCounter[0][-1] = InputDataInstance.instance.nPeriods - InputDataInstance.instance.demandsArray.sum()
        itemsCounter[1] = copy.deepcopy(itemsCounter[0])
        
        # print(self.offsprings, self.offspringsItemsToOrder, itemsCounter)

        offspringLastPlacedGene = {0: None, 1: None}
        period = InputDataInstance.instance.nPeriods - 1
        self.searchFixedOffspring(0, self.offsprings[0], period, self.offspringsItemsToOrder[0], itemsCounter[0], offspringLastPlacedGene[0])

        self.searchFixedOffspring(1, self.offsprings[1], period, self.offspringsItemsToOrder[1], itemsCounter[1], offspringLastPlacedGene[1])

        # print(self.offsprings)


    def replicatePrimeParentGene(self, period, itemsCounter, subPrimeParent):
        """
        """
        parentPeriodValue = self.primeParent.stringIdentifier[period]

        if period >= self.crossOverPeriod:
            if parentPeriodValue > 0:
                # First offspring
                self.offsprings[0].stringIdentifier[period] = self.primeParent.stringIdentifier[period]
                parentGene = self.primeParent.genesByPeriod[period]
                self.offsprings[0].dnaArray[parentGene.item][parentGene.position] = copy.deepcopy(parentGene)
                self.offsprings[0].genesByPeriod[period] = self.offsprings[0].dnaArray[parentGene.item][parentGene.position]
                itemsCounter[0][parentGene.item] -= 1
                self.offspringsItemsToOrder[0].remove((parentGene.item, parentGene.position))
        else:

            # First offspring
            if subPrimeParent.stringIdentifier[period] > 0:
                parentGene = subPrimeParent.genesByPeriod[period]
                if parentGene.position == itemsCounter[0][parentGene.item] - 1:
                    self.offsprings[0].stringIdentifier[period] = subPrimeParent.stringIdentifier[period]
                    self.offsprings[0].dnaArray[parentGene.item][parentGene.position] = copy.deepcopy(parentGene)
                    self.offsprings[0].genesByPeriod[period] = self.offsprings[0].dnaArray[parentGene.item][parentGene.position]
                    itemsCounter[0][parentGene.item] -= 1
                    self.offspringsItemsToOrder[0].remove((parentGene.item, parentGene.position))

            # print("roro : ", parentPeriodValue)
            if parentPeriodValue > 0:
                # Second offspring
                self.offsprings[1].stringIdentifier[period] = self.primeParent.stringIdentifier[period]
                parentGene = self.primeParent.genesByPeriod[period]
                self.offsprings[1].dnaArray[parentGene.item][parentGene.position] = copy.deepcopy(parentGene)
                self.offsprings[1].genesByPeriod[period] = self.offsprings[1].dnaArray[parentGene.item][parentGene.position]
                # itemsCounter[0][parentGene.item] -= 1
                self.offspringsItemsToOrder[1].remove((parentGene.item, parentGene.position))

                # fill previous gaps
                for position in range(parentGene.position + 1, len(InputDataInstance.instance.demandsArrayZipped[parentGene.item]) - 1):
                    if self.offsprings[1].dnaArray[parentGene.item][position - 1] is None:
                        break

                    # print(parentGene.item, position, parentGene.position + 1, len(InputDataInstance.instance.demandsArrayZipped[parentGene.item]), parentGene.position + 1 >= len(InputDataInstance.instance.demandsArray[parentGene.item]) - 1)
                    parentGene = (subPrimeParent.dnaArray[parentGene.item][position])
                    if self.offsprings[1].dnaArray[parentGene.item][position] is None and parentGene.period > period and self.offsprings[1].stringIdentifier[parentGene.period] == "*": 
                        self.offsprings[1].stringIdentifier[parentGene.period] = parentPeriodValue
                        self.offsprings[1].dnaArray[parentGene.item][parentGene.position] = copy.deepcopy(parentGene)
                        self.offsprings[1].genesByPeriod[parentGene.period] = self.offsprings[1].dnaArray[parentGene.item][parentGene.position]
                        # itemsCounter[0][parentGene.item] -= 1
                        self.offspringsItemsToOrder[1].remove((parentGene.item, parentGene.position))



    def searchFixedOffspring(self, offspringIndex, offspring, period, offspringItemsToOrder, itemsCounter, offspringLastPlacedGene):
        """
        """

        # print("Searching : ", period, offspring, offspringItemsToOrder)

        if period == -1:
            if len(offspringItemsToOrder) == 0:
                # print("offspringIndex : ", offspringIndex, offspring)
                Chromosome.evalAndFixDnaArray(offspring)
                self.offsprings[offspringIndex] = offspring
                self._stopSearchEvents[offspringIndex].set()
            return None

        # items = self.provideSearchNextMoves(offspringIndex, offspring, offspringItemsToOrder)
        if offspring.stringIdentifier[period] == "*":
            items = self.provideSearchNextMoves(offspringIndex, offspring, period, offspringItemsToOrder, itemsCounter, offspringLastPlacedGene)
            # print('next moves : ', items)
            for item in items:
                offspringCopy = copy.deepcopy(offspring)
                offspringItemsToOrderCopy = copy.deepcopy(offspringItemsToOrder)
                itemsCounterCopy = copy.deepcopy(itemsCounter)
                offspringLastPlacedGeneCopy = copy.deepcopy(offspringLastPlacedGene)
                self.orderItem(offspringCopy, item, period, offspringItemsToOrderCopy, itemsCounterCopy, offspringLastPlacedGeneCopy)
                # raise Exception("yes")
                period -= 1 
                self.searchFixedOffspring(offspringIndex, offspringCopy, period, offspringItemsToOrderCopy, itemsCounterCopy, offspringLastPlacedGeneCopy)
                if self._stopSearchEvents[offspringIndex].is_set():
                    return None
        else:
            itemsCounter[offspring.stringIdentifier[period] - 1] -= 1
            offspringCopy = copy.deepcopy(offspring)
            offspringItemsToOrderCopy = copy.deepcopy(offspringItemsToOrder)
            itemsCounterCopy = copy.deepcopy(itemsCounter)
            offspringLastPlacedGene = offspring.genesByPeriod[period]
            offspringLastPlacedGeneCopy = copy.deepcopy(offspringLastPlacedGene)
            period -= 1 
            self.searchFixedOffspring(offspringIndex, offspringCopy, period, offspringItemsToOrderCopy, itemsCounterCopy, offspringLastPlacedGeneCopy)
            if self._stopSearchEvents[offspringIndex].is_set():
                return None


    def provideSearchNextMoves(self, offspringIndex, offspring, period, offspringItemsToOrder, itemsCounter, offspringLastPlacedGene):
        """
        """

        # items = sorted( \
        #     [item for item in offspringItemsToOrder if item[0] != -1], \
        #     key= lambda pair: InputDataInstance.instance.demandsArrayZipped[pair[0]][pair[1]] \
        # )

        # if len(items) == 0:
        #     items = [item for item in offspringItemsToOrder if item[0] == -1]
        #     for item in items:
        #         yield item
        # else:
        #     while len(items) > 0:
        #         item = items[0]
        #         itemPairs = [pair for pair in items if pair[0] == item[0]]
        #         for pair in itemPairs:
        #             items.remove(pair)
        #             yield pair


        # print("itemsCounter : ", itemsCounter)
        items = [item for item in itemsCounter if item >= 0 and itemsCounter[item] > 0 and InputDataInstance.instance.demandsArrayZipped[item][itemsCounter[item] - 1] >= period and (item, itemsCounter[item] - 1) in offspringItemsToOrder]
            
        itemsCost = sorted([ \
                        ( \
                            item, \
                            InputDataInstance.instance.stockingCostsArray[item] * (InputDataInstance.instance.demandsArrayZipped[item][itemsCounter[item] - 1] - period) \
                            + (InputDataInstance.instance.changeOverCostsArray[item][offspringLastPlacedGene.item] if offspringLastPlacedGene is not None else 0) \
                            + (0 if offspring.stringIdentifier[period - 1] in ["*", 0] else InputDataInstance.instance.changeOverCostsArray[offspring.stringIdentifier[period - 1] - 1][item])
                        ) \
                        for item in items \
        ], key= lambda pair: pair[1])

        items = [pair[0] for pair in itemsCost]

        if len(items) == 0 and itemsCounter[-1] > 0:
            items.append(-1)

        return items



    def improveOffspringQuality(self, offspring):
        """
        """


    def orderItem(self, offspring, item, period, offspringItemsToOrder, itemsCounter, offspringLastPlacedGene):
        """
        """

        # print("producing : ", period, offspring, offspringItemsToOrder)

        # stringIdentifier
        offspring.stringIdentifier[period] = item + 1
        itemsCounter[item] -= 1
        offspringItemsToOrder.remove((item, itemsCounter[item]))

        if item != -1:

            # dnaArray
            gene = Gene(item, period, itemsCounter[item])
            gene.calculateStockingCost()
            gene.calculateCost()

            offspring.dnaArray[gene.item][gene.position] = gene
            offspring.genesByPeriod[period] = gene
            # offspringLastPlacedGene[offspringIndex] = gene
            return gene


        return None
