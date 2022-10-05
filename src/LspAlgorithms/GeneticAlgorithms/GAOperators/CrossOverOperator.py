from collections import defaultdict
import random
import threading
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Chromosome import Chromosome
from LspInputDataReading.LspInputDataInstance import InputDataInstance
import concurrent.futures
import copy
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Gene import Gene
from .LocalSearchEngine import LocalSearchEngine
from ..PopInitialization.Population import Population
from ParameterSearch.ParameterData import ParameterData
from .LocalSearchEngine import LocalSearchEngine
from LspAlgorithms.GeneticAlgorithms.PopInitialization.PseudoChromosome import PseudoChromosome
from LspAlgorithms.GeneticAlgorithms.LspRuntimeMonitor import LspRuntimeMonitor

class CrossOverOperator:
    """
    """

    crossOverMemory = {"lock": threading.Lock(), "content": defaultdict(lambda: None)}

    def __init__(self) -> None:
        """
        """

        pass


    def initCrossOver(self, parentChromosomes):
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

        self.parentChromosomes = (self.parentChromosomes[0], self.parentChromosomes[1]) if self.parentChromosomes[0] < self.parentChromosomes[1] else (self.parentChromosomes[1], self.parentChromosomes[0])

        # self._stopSearchEvents = {0: threading.Event(), 1: threading.Event()}



    def process(self, population):
        """
        """

        chromosomes = list()
        self.population = population

        while len(chromosomes) < Population.popSizes[population.threadIdentifier]:

            chromosomeA, chromosomeB = population.selectionOperator.select()

            if isinstance(chromosomeA, PseudoChromosome):
                chromosomeA = LocalSearchEngine.switchItems(chromosomeA.value)
            if isinstance(chromosomeB, PseudoChromosome):
                chromosomeB = LocalSearchEngine.switchItems(chromosomeB.value)

            chromosomeC, chromosomeD = None, None

            if (random.random() <= ParameterData.instance.crossOverRate):
                try:
                    chromosomeC, chromosomeD = self.mate([chromosomeA, chromosomeB])
                except Exception as e:
                    raise e
            else:
                # print("No crossover")
                chromosomeC, chromosomeD = chromosomeA, chromosomeB

            if chromosomeC is None:
                print("chromosomeC None")
            else:
                chromosomes.append(chromosomeC)

            if len(chromosomes) < Population.popSizes[population.threadIdentifier]:
                if chromosomeD is None:
                    print("chromosomeD None")
                else:
                    chromosomes.append(chromosomeD)

            print("chromosomes length : ", len(chromosomes), Population.popSizes[population.threadIdentifier])

        return chromosomes




    def mate(self, parentChromosomes, offspring_result = 2):
        """
        """

        self.initCrossOver(parentChromosomes)

        if offspring_result not in [1, 2]:
            # TODO: throw an error
            return None, None


        if self.parentChromosomes[0] == self.parentChromosomes[1]:
            return (self.parentChromosomes[0], self.parentChromosomes[1])

        # print("Crossover : ", self.parentChromosomes, self.parentChromosomes[0].dnaArray, self.parentChromosomes[1].dnaArray)
        print("Crossover : ", self.parentChromosomes)

        # before launching the recursive search
        gapLength = int(InputDataInstance.instance.nPeriods / 3)
        # random.seed()
        self.crossOverPeriod = random.randint(gapLength + 1, InputDataInstance.instance.nPeriods - (gapLength + 1))

        # checking the crossover memory for previous occurences of this context
        memoryResult = None
        with CrossOverOperator.crossOverMemory["lock"]:
            memoryResult = CrossOverOperator.crossOverMemory["content"][((self.parentChromosomes[0]).stringIdentifier, (self.parentChromosomes[1]).stringIdentifier, self.crossOverPeriod)] if CrossOverOperator.crossOverMemory["content"][((self.parentChromosomes[0]).stringIdentifier, (self.parentChromosomes[1]).stringIdentifier, self.crossOverPeriod)] is not None else \
                                (CrossOverOperator.crossOverMemory["content"][((self.parentChromosomes[1]).stringIdentifier, (self.parentChromosomes[0]).stringIdentifier, self.crossOverPeriod)] if CrossOverOperator.crossOverMemory["content"][((self.parentChromosomes[1]).stringIdentifier, (self.parentChromosomes[0]).stringIdentifier, self.crossOverPeriod)] is not None else None)
        if  memoryResult is not None:
            print("Retrieving crossover results : ", memoryResult)
            for offspring in memoryResult:
                LocalSearchEngine().process(offspring, "simple_mutation", {"threadId": self.population.threadIdentifier})
            return memoryResult

        # Initializing offsprings' stringIdentifier property

        # looping
        # self.crossOverPeriod =  3
        print("crossOverPeriod : ", self.crossOverPeriod)
        self.offspringLastPlacedGene = {0: None, 1: None}

        self.offsprings[0].stringIdentifier = ["*"] * InputDataInstance.instance.nPeriods
        self.offsprings[1].stringIdentifier = ["*"] * InputDataInstance.instance.nPeriods

        self.setOffsprings()

        print("Cross Over result : ", [self.parentChromosomes, self.offsprings])

        # storing this result in the crossover memory before returning 
        with CrossOverOperator.crossOverMemory["lock"]:
            CrossOverOperator.crossOverMemory["content"][((self.parentChromosomes[0]).stringIdentifier, (self.parentChromosomes[1]).stringIdentifier, self.crossOverPeriod)] = tuple(self.offsprings.values())

        return tuple(self.offsprings.values())



    def setOffsprings(self):
        """
        """

        # first, let's remove present dual genes
        itemsCounter = {0: None, 1: None}
        itemsCounter[0] = {item: len(InputDataInstance.instance.demandsArrayZipped[item]) for item in range(InputDataInstance.instance.nItems)} 
        itemsCounter[0][-1] = InputDataInstance.instance.nPeriods - InputDataInstance.instance.demandsArray.sum()
        itemsCounter[1] = copy.deepcopy(itemsCounter[0])

        for period in reversed(range(InputDataInstance.instance.nPeriods)):
            self.replicatePrimeParentGene(period, itemsCounter)

        # Second, let's attempt to add missing genes

        itemsCounter[0] = {item: len(InputDataInstance.instance.demandsArrayZipped[item]) for item in range(InputDataInstance.instance.nItems)} 
        itemsCounter[0][-1] = InputDataInstance.instance.nPeriods - InputDataInstance.instance.demandsArray.sum()
        itemsCounter[1] = copy.deepcopy(itemsCounter[0])
        
        print(self.offsprings, self.offspringsItemsToOrder)

        offspringLastPlacedGene = {0: {"value": None}, 1: {"value": None}}
        offsprings = copy.deepcopy(self.offsprings)
        self.offsprings = {0: None, 1: None}

        for i in [0, 1]:
            self.searchOffspring(i, offsprings[i], itemsCounter[i], offspringLastPlacedGene[i])

        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     for i in [0, 1]:
        #         executor.submit(self.searchOffspring, i, offsprings[i], itemsCounter[i], offspringLastPlacedGene[i])


    def replicatePrimeParentGene(self, period, itemsCounter):
        """
        """
        parentPeriodValue = self.parentChromosomes[0].stringIdentifier[period]

        if period >= self.crossOverPeriod:
            if parentPeriodValue > 0:
                # First offspring
                self.offsprings[0].stringIdentifier[period] = self.parentChromosomes[0].stringIdentifier[period]
                parentGene = self.parentChromosomes[0].dnaArray[(self.parentChromosomes[0].genesByPeriod[period])[0]][(self.parentChromosomes[0].genesByPeriod[period])[1]]
                self.offsprings[0].dnaArray[parentGene.item][parentGene.position] = copy.deepcopy(parentGene)
                self.offsprings[0].genesByPeriod[period] = (parentGene.item, parentGene.position)
                itemsCounter[0][parentGene.item] -= 1
                self.offspringsItemsToOrder[0].remove((parentGene.item, parentGene.position))
        else:

            # First offspring
            if self.parentChromosomes[1].stringIdentifier[period] > 0:
                parentGene = self.parentChromosomes[1].dnaArray[(self.parentChromosomes[1].genesByPeriod[period])[0]][(self.parentChromosomes[1].genesByPeriod[period])[1]]
                if parentGene.position == itemsCounter[0][parentGene.item] - 1:
                    self.offsprings[0].stringIdentifier[period] = self.parentChromosomes[1].stringIdentifier[period]
                    self.offsprings[0].dnaArray[parentGene.item][parentGene.position] = copy.deepcopy(parentGene)
                    self.offsprings[0].genesByPeriod[period] = (parentGene.item, parentGene.position)
                    itemsCounter[0][parentGene.item] -= 1
                    self.offspringsItemsToOrder[0].remove((parentGene.item, parentGene.position))

            # Second offspring
            if parentPeriodValue > 0:
                # Second offspring
                self.offsprings[1].stringIdentifier[period] = self.parentChromosomes[0].stringIdentifier[period]
                parentGene = self.parentChromosomes[0].dnaArray[(self.parentChromosomes[0].genesByPeriod[period])[0]][(self.parentChromosomes[0].genesByPeriod[period])[1]]
                self.offsprings[1].dnaArray[parentGene.item][parentGene.position] = copy.deepcopy(parentGene)
                self.offsprings[1].genesByPeriod[period] = (parentGene.item, parentGene.position)
                self.offspringsItemsToOrder[1].remove((parentGene.item, parentGene.position))

            # fill previous gaps
            if period == 0:
                for period in range(self.crossOverPeriod, InputDataInstance.instance.nPeriods):
                    if self.parentChromosomes[1].stringIdentifier[period] > 0:
                        parentGene = self.parentChromosomes[1].dnaArray[(self.parentChromosomes[1].genesByPeriod[period])[0]][(self.parentChromosomes[1].genesByPeriod[period])[1]]
                        if self.offsprings[1].dnaArray[parentGene.item][parentGene.position] is None:
                            # if parentGene.position == 0 or (parentGene.position > 0 and self.offsprings[1].dnaArray[parentGene.item][parentGene.position - 1] is not None):
                            if (parentGene.position > 0 and self.offsprings[1].dnaArray[parentGene.item][parentGene.position - 1] is not None):
                                self.offsprings[1].stringIdentifier[period] = self.parentChromosomes[1].stringIdentifier[period]
                                self.offsprings[1].dnaArray[parentGene.item][parentGene.position] = copy.deepcopy(parentGene)
                                self.offsprings[1].genesByPeriod[period] = (parentGene.item, parentGene.position)
                                self.offspringsItemsToOrder[1].remove((parentGene.item, parentGene.position))



    def searchOffspring(self, offspringIndex, offspring, itemsCounter, offspringLastPlacedGene, searchHorizon = 2):
        """
        """

        period = InputDataInstance.instance.nPeriods - 1
        queue = [{"offspringIndex": offspringIndex, "offspring": offspring, "itemsCounter": itemsCounter, "period": period, "offspringItemsToOrder": self.offspringsItemsToOrder[offspringIndex], "offspringLastPlacedGene": offspringLastPlacedGene}]

        while len(queue) > 0:
            searchArgs = queue[-1]
            queue = queue[:-1]

            # leaf node
            if self.isLeafReached(**searchArgs):
                break

            for prodChoice in self.listProdChoices(**searchArgs):
                queue.append(prodChoice)
                break



    # def searchOffspring(self, offspringIndex, offspring, itemsCounter, offspringLastPlacedGene, searchHorizon = 2):
    #     """
    #     """

    #     period = InputDataInstance.instance.nPeriods - 1
    #     higherLevelQueue = [{"offspringIndex": offspringIndex, "offspring": offspring, "itemsCounter": itemsCounter, "period": period, "offspringItemsToOrder": self.offspringsItemsToOrder[offspringIndex], "offspringLastPlacedGene": offspringLastPlacedGene}]
    #     sArgs = higherLevelQueue[0]

    #     while sArgs["period"] >= -1:

    #         # leaf node
    #         if self.isLeafReached(**sArgs):
    #             period = searchArgs["period"]
    #             break

    #         queue = [sArgs]
    #         # print("arrrrrrrrrrrrg : ", sArgs)
    #         while len(queue) > 0 and  (queue[0])["period"] > -1 and (queue[0])["period"] > sArgs["period"] - searchHorizon:
    #             searchArgs = queue[0]
    #             queue = queue[1:]

    #             # leaf node
    #             if self.isLeafReached(**searchArgs):
    #                 period = searchArgs["period"]
    #                 return None

    #             for prodChoice in self.listProdChoices(**searchArgs):
    #                 queue.append(prodChoice)
    #                 # break

    #         # print("len  : ", len(queue))
    #         higherLevelQueue = copy.deepcopy(queue)
    #         sArgs = sorted(higherLevelQueue, key=lambda item: item["offspring"])[0]
    #         # break

    #     print("Printing offspring ", offspringIndex, self.offsprings[offspringIndex])



    def isLeafReached(self, offspringIndex, offspring, period, offspringItemsToOrder, itemsCounter, offspringLastPlacedGene):
        """
        """

        if period == -1:
            if len(offspringItemsToOrder) == 0:
                # print("offspringIndex : ", offspringIndex, offspring)
                offspring.stringIdentifier = tuple(offspring.stringIdentifier)

                c = Chromosome.createFromIdentifier(offspring.stringIdentifier)
                if offspring.dnaArray != c.dnaArray:
                    print(" Watch out ",offspringIndex, offsprings.dnaArray, " --- ", c.dnaArray)

                if self.offsprings[offspringIndex] is None or (self.offsprings[offspringIndex] is not None and offspring < self.offsprings[offspringIndex]):
                    self.offsprings[offspringIndex] = offspring

                inPool = False
                with Chromosome.pool["lock"]:
                    if offspring.stringIdentifier in Chromosome.pool["content"]:
                        inPool = True

                if not inPool:
                    with Chromosome.pool["lock"]:
                        Chromosome.pool["content"][offspring.stringIdentifier] = self.population.threadIdentifier
                        # Chromosome.pool["content"][offspring.stringIdentifier] = {"threadId": 1, "value": offspring}
                    Chromosome.popByThread[self.population.threadIdentifier]["content"][offspring.stringIdentifier] = offspring
                    Chromosome.insertInSortedList(Chromosome.popByThread[self.population.threadIdentifier]["sortedList"], offspring, LspRuntimeMonitor.instance.sortedListLength[self.population.threadIdentifier])
                else:
                    (LocalSearchEngine().process(offspring, "simple_mutation", {"threadId": self.population.threadIdentifier}))

            return True

        return False


    def listProdChoices(self, offspringIndex, offspring, period, offspringItemsToOrder, itemsCounter, offspringLastPlacedGene):
        """
        """

        # if self.offsprings[offspringIndex] is not None and offspring > self.offsprings[offspringIndex]:
        #     return None

        if offspring.stringIdentifier[period] == "*":
            items = self.provideSearchNextMoves(offspringIndex, offspring, period, offspringItemsToOrder, itemsCounter, offspringLastPlacedGene)
            # print('next moves : ', period, items, offspring)
            for item in items:
                offspringCopy = copy.deepcopy(offspring)
                offspringItemsToOrderCopy = copy.deepcopy(offspringItemsToOrder)
                itemsCounterCopy = copy.deepcopy(itemsCounter)
                offspringLastPlacedGeneCopy = copy.deepcopy(offspringLastPlacedGene)
                self.orderItem(offspringCopy, item, period, offspringItemsToOrderCopy, itemsCounterCopy, offspringLastPlacedGeneCopy)
                result = {"offspringIndex": offspringIndex, "offspring": offspringCopy, "itemsCounter": itemsCounterCopy, "period": period - 1, "offspringItemsToOrder": offspringItemsToOrderCopy, "offspringLastPlacedGene": offspringLastPlacedGeneCopy}
                yield result
                # self.searchFixedOffspring(offspringIndex, offspringCopy, period - 1, offspringItemsToOrderCopy, itemsCounterCopy, offspringLastPlacedGeneCopy)
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
            result = {"offspringIndex": offspringIndex, "offspring": offspring, "itemsCounter": itemsCounter, "period": period - 1, "offspringItemsToOrder": offspringItemsToOrder, "offspringLastPlacedGene": offspringLastPlacedGene}
            yield result
            # self.searchFixedOffspring(offspringIndex, offspring, period - 1, offspringItemsToOrder, itemsCounter, offspringLastPlacedGene)


    def provideSearchNextMoves(self, offspringIndex, offspring, period, offspringItemsToOrder, itemsCounter, offspringLastPlacedGene):
        """
        """

        # print("itemsCounter : ", itemsCounter)
        items = [item for item in itemsCounter if item >= 0 and itemsCounter[item] > 0 and InputDataInstance.instance.demandsArrayZipped[item][itemsCounter[item] - 1] >= period and (item, itemsCounter[item] - 1) in offspringItemsToOrder]
            
        parentGene = None
        if offspringIndex == 0 and period < self.crossOverPeriod and self.parentChromosomes[1].stringIdentifier[period] > 0:
            gene = self.parentChromosomes[1].dnaArray[(self.parentChromosomes[1].genesByPeriod[period])[0]][(self.parentChromosomes[1].genesByPeriod[period])[1]]
            if gene.position == itemsCounter[gene.item] - 1:
                parentGene = gene

        if offspringIndex == 1 and period >= self.crossOverPeriod and self.parentChromosomes[1].stringIdentifier[period] > 0:
            gene = self.parentChromosomes[1].dnaArray[(self.parentChromosomes[1].genesByPeriod[period])[0]][(self.parentChromosomes[1].genesByPeriod[period])[1]]
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
