from collections import defaultdict
import random
import threading
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
        self.crossOverPeriod =  3
        print("crossOverPeriod : ", self.crossOverPeriod)
        self.offspringLastPlacedGene = {0: None, 1: None}

        self.offsprings[0].stringIdentifier = ["*"] * InputDataInstance.instance.nPeriods
        self.offsprings[1].stringIdentifier = ["*"] * InputDataInstance.instance.nPeriods

        self.setOffsprings()

        if self.offsprings[0] is not None:
            self.offsprings[0].stringIdentifier = tuple(self.offsprings[0].stringIdentifier)
            c = Chromosome.createFromIdentifier(self.offsprings[0].stringIdentifier)
            if self.offsprings[0].dnaArray != c.dnaArray:
                print(" Watch out 0", self.offsprings[0].dnaArray, " --- ", c.dnaArray)
        else:
            print("Crossover offspring 0 None")
            # del self.offsprings[0]

        if self.offsprings[1] is not None:
            self.offsprings[1].stringIdentifier = tuple(self.offsprings[1].stringIdentifier)
            c = Chromosome.createFromIdentifier(self.offsprings[1].stringIdentifier)
            if self.offsprings[1].dnaArray != c.dnaArray:
                print(" Watch out 1", self.offsprings[1].dnaArray)
        else:
            print("Crossover offspring 1 None")
            # del self.offsprings[1]

        print("Cross Over result : ", [self.parentChromosomes, self.offsprings])

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
        
        print(self.offsprings, self.offspringsItemsToOrder)

        offspringLastPlacedGene = {0: {"value": None}, 1: {"value": None}}
        period = InputDataInstance.instance.nPeriods - 1
        offsprings = copy.deepcopy(self.offsprings)
        self.offsprings = {0: None, 1: None}

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for i in [0, 1]:
                executor.submit(self.searchFixedOffspring, i, offsprings[i], period, self.offspringsItemsToOrder[i], itemsCounter[i], offspringLastPlacedGene[i], subPrimeParent)
        
        # print(self.offsprings)


    def replicatePrimeParentGene(self, period, itemsCounter, subPrimeParent):
        """
        """
        parentPeriodValue = self.primeParent.stringIdentifier[period]

        if period >= self.crossOverPeriod:
            if parentPeriodValue > 0:
                # First offspring
                self.offsprings[0].stringIdentifier[period] = self.primeParent.stringIdentifier[period]
                parentGene = self.primeParent.dnaArray[(self.primeParent.genesByPeriod[period])[0]][(self.primeParent.genesByPeriod[period])[1]]
                self.offsprings[0].dnaArray[parentGene.item][parentGene.position] = copy.deepcopy(parentGene)
                self.offsprings[0].genesByPeriod[period] = (parentGene.item, parentGene.position)
                itemsCounter[0][parentGene.item] -= 1
                self.offspringsItemsToOrder[0].remove((parentGene.item, parentGene.position))
        else:

            # First offspring
            if subPrimeParent.stringIdentifier[period] > 0:
                parentGene = subPrimeParent.dnaArray[(subPrimeParent.genesByPeriod[period])[0]][(subPrimeParent.genesByPeriod[period])[1]]
                if parentGene.position == itemsCounter[0][parentGene.item] - 1:
                    self.offsprings[0].stringIdentifier[period] = subPrimeParent.stringIdentifier[period]
                    self.offsprings[0].dnaArray[parentGene.item][parentGene.position] = copy.deepcopy(parentGene)
                    self.offsprings[0].genesByPeriod[period] = (parentGene.item, parentGene.position)
                    itemsCounter[0][parentGene.item] -= 1
                    self.offspringsItemsToOrder[0].remove((parentGene.item, parentGene.position))

            # Second offspring
            if parentPeriodValue > 0:
                # Second offspring
                self.offsprings[1].stringIdentifier[period] = self.primeParent.stringIdentifier[period]
                parentGene = self.primeParent.dnaArray[(self.primeParent.genesByPeriod[period])[0]][(self.primeParent.genesByPeriod[period])[1]]
                self.offsprings[1].dnaArray[parentGene.item][parentGene.position] = copy.deepcopy(parentGene)
                self.offsprings[1].genesByPeriod[period] = (parentGene.item, parentGene.position)
                self.offspringsItemsToOrder[1].remove((parentGene.item, parentGene.position))

            # fill previous gaps
            if period == 0:
                for period in range(self.crossOverPeriod, InputDataInstance.instance.nPeriods):
                    if subPrimeParent.stringIdentifier[period] > 0:
                        parentGene = subPrimeParent.dnaArray[(subPrimeParent.genesByPeriod[period])[0]][(subPrimeParent.genesByPeriod[period])[1]]
                        if self.offsprings[1].dnaArray[parentGene.item][parentGene.position] is None:
                            # if parentGene.position == 0 or (parentGene.position > 0 and self.offsprings[1].dnaArray[parentGene.item][parentGene.position - 1] is not None):
                            if (parentGene.position > 0 and self.offsprings[1].dnaArray[parentGene.item][parentGene.position - 1] is not None):
                                self.offsprings[1].stringIdentifier[period] = subPrimeParent.stringIdentifier[period]
                                self.offsprings[1].dnaArray[parentGene.item][parentGene.position] = copy.deepcopy(parentGene)
                                self.offsprings[1].genesByPeriod[period] = (parentGene.item, parentGene.position)
                                self.offspringsItemsToOrder[1].remove((parentGene.item, parentGene.position))



    def searchFixedOffspring(self, offspringIndex, offspring, period, offspringItemsToOrder, itemsCounter, offspringLastPlacedGene, subPrimeParent):
        """
        """

        # print("Searching : ", period, offspring, offspringLastPlacedGene["value"], "\n", offspring.dnaArray)

        if period == -1:
            if len(offspringItemsToOrder) == 0:
                # print("offspringIndex : ", offspringIndex, offspring)
                # Chromosome.evalAndFixDnaArray(offspring)
                # print("after offspringIndex : ", offspringIndex, offspring)
                if self.offsprings[offspringIndex] is None or (self.offsprings[offspringIndex] is not None and offspring < self.offsprings[offspringIndex]):
                    self.offsprings[offspringIndex] = offspring
                # self._stopSearchEvents[offspringIndex].set()
            return None

        if self.offsprings[offspringIndex] is not None and offspring >= self.offsprings[offspringIndex]:
            return None

        if offspring.stringIdentifier[period] == "*":
            items = self.provideSearchNextMoves(offspringIndex, offspring, period, offspringItemsToOrder, itemsCounter, offspringLastPlacedGene, subPrimeParent)
            # print('next moves : ', period, items, offspring)
            for item in items:
                offspringCopy = copy.deepcopy(offspring)
                offspringItemsToOrderCopy = copy.deepcopy(offspringItemsToOrder)
                itemsCounterCopy = copy.deepcopy(itemsCounter)
                offspringLastPlacedGeneCopy = copy.deepcopy(offspringLastPlacedGene)
                self.orderItem(offspringCopy, item, period, offspringItemsToOrderCopy, itemsCounterCopy, offspringLastPlacedGeneCopy)
                self.searchFixedOffspring(offspringIndex, offspringCopy, period - 1, offspringItemsToOrderCopy, itemsCounterCopy, offspringLastPlacedGeneCopy, subPrimeParent)
                # if self._stopSearchEvents[offspringIndex].is_set():
                #     return None
        else:
            itemsCounter[offspring.stringIdentifier[period] - 1] -= 1
            gene = offspring.dnaArray[(offspring.genesByPeriod[period])[0]][(offspring.genesByPeriod[period])[1]]
            gene.prevGene = None
            
            gene.changeOverCost = 0
            gene.calculateCost()
            offspring.cost += gene.stockingCost
            if offspringLastPlacedGene["value"] is None:
                gene.nextGene = None
            else:
                offspringLastPlacedGene["value"] = offspring.dnaArray[offspringLastPlacedGene["value"].item][offspringLastPlacedGene["value"].position]
                gene.nextGene = (offspringLastPlacedGene["value"].item, offspringLastPlacedGene["value"].position)
                offspringLastPlacedGene["value"].prevGene = (gene.item, gene.position)
                offspringLastPlacedGene["value"].calculateChangeOverCost()
                offspringLastPlacedGene["value"].calculateCost()
                offspring.cost += offspringLastPlacedGene["value"].changeOverCost

            offspringLastPlacedGene["value"] = offspring.dnaArray[gene.item][gene.position]
            self.searchFixedOffspring(offspringIndex, offspring, period - 1, offspringItemsToOrder, itemsCounter, offspringLastPlacedGene, subPrimeParent)
            # if self._stopSearchEvents[offspringIndex].is_set():
            #     return None


    def provideSearchNextMoves(self, offspringIndex, offspring, period, offspringItemsToOrder, itemsCounter, offspringLastPlacedGene, subPrimeParent):
        """
        """

        # print("itemsCounter : ", itemsCounter)
        items = [item for item in itemsCounter if item >= 0 and itemsCounter[item] > 0 and InputDataInstance.instance.demandsArrayZipped[item][itemsCounter[item] - 1] >= period and (item, itemsCounter[item] - 1) in offspringItemsToOrder]
            
        parentGene = None
        if offspringIndex == 0 and period < self.crossOverPeriod and subPrimeParent.stringIdentifier[period] > 0:
            gene = subPrimeParent.dnaArray[(subPrimeParent.genesByPeriod[period])[0]][(subPrimeParent.genesByPeriod[period])[1]]
            if gene.position == itemsCounter[gene.item] - 1:
                parentGene = gene

        if offspringIndex == 1 and period >= self.crossOverPeriod and subPrimeParent.stringIdentifier[period] > 0:
            gene = subPrimeParent.dnaArray[(subPrimeParent.genesByPeriod[period])[0]][(subPrimeParent.genesByPeriod[period])[1]]
            if gene.position == itemsCounter[gene.item] - 1:
                parentGene = gene

        parentItemFound = False
        if parentGene is not None and parentGene.item in items:
            parentItemFound = True
            items.remove(parentGene.item)

        itemsCost = sorted([ \
                        ( \
                            item, \
                            InputDataInstance.instance.stockingCostsArray[item] * (InputDataInstance.instance.demandsArrayZipped[item][itemsCounter[item] - 1] - period) \
                            + (InputDataInstance.instance.changeOverCostsArray[item][offspringLastPlacedGene["value"].item] if offspringLastPlacedGene["value"] is not None else 0) \
                            + (0 if offspring.stringIdentifier[period - 1] == "*" else InputDataInstance.instance.changeOverCostsArray[offspring.stringIdentifier[period - 1] - 1][item])
                        ) \
                        for item in items \
        ], key= lambda pair: pair[1])

        items = [pair[0] for pair in itemsCost]

        if parentItemFound:
            items.insert(0, parentGene.item)

        if len(items) == 0 and itemsCounter[-1] > 0:
            items.append(-1)

        return items


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
            offspring.cost += gene.stockingCost

            if offspringLastPlacedGene["value"] is None:
                gene.nextGene = None 
            else:
                offspringLastPlacedGene["value"] = offspring.dnaArray[offspringLastPlacedGene["value"].item][offspringLastPlacedGene["value"].position]
                gene.nextGene = (offspringLastPlacedGene["value"].item, offspringLastPlacedGene["value"].position) 
                offspringLastPlacedGene["value"].prevGene = (gene.item, gene.position)
                offspringLastPlacedGene["value"].calculateChangeOverCost()
                offspringLastPlacedGene["value"].calculateCost()
                offspring.cost += offspringLastPlacedGene["value"].changeOverCost

            offspring.dnaArray[gene.item][gene.position] = gene
            offspring.genesByPeriod[period] = (gene.item, gene.position)
            offspringLastPlacedGene["value"] = offspring.dnaArray[gene.item][gene.position]

            return gene

        return None
