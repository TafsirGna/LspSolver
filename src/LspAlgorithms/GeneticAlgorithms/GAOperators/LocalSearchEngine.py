from collections import defaultdict
import threading
import copy
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
# from LspAlgorithms.GeneticAlgorithms.LocalSearch.LocalSearchNode import LocalSearchNode
from ParameterSearch.ParameterData import ParameterData
import concurrent.futures
from LspInputDataReading.LspInputDataInstance import InputDataInstance
import random
import numpy as np

class LocalSearchEngine:
    """
    """

    genericGeneIndices = None
    mutationsMemory = {"lock": threading.Lock(), "db":defaultdict(lambda: None)}

    def __init__(self) -> None:
        """
        """

        self.searchDepth = 0
        self.result = None
        self._stopSearchEvent = threading.Event()

        # if LocalSearchEngine.genericGeneIndices is None:
        #     LocalSearchEngine.genericGeneIndices = [(item, position) for item, itemGenes in enumerate(InputDataInstance.instance.demandsArrayZipped) for position, _ in enumerate(itemGenes)]


    def process(self, chromosome, strategy = "simple_mutation"):
        """Process the given chromosome in order to return a mutated version
        strategy: random_mutation|absolute_mutation|simple_mutation
        """

        # print("mutatiooooooon", strategy, chromosome, chromosome.dnaArray)

        self._visitedNodes = defaultdict(lambda: None)

        self.searchIndividu(chromosome, strategy)

        print("Mutation results : ", strategy, chromosome, self.result)

        if self.result.cost != Chromosome.createFromIdentifier(self.result.stringIdentifier).cost:
            print("Oaaaaaaaaaaaaaaaaauuuuuuuuuuuuuuuuuuuuuuuuuhhhhhhhhhhhhhhh")

        return (self.result if self.result is not None else chromosome)


    def searchIndividu(self, chromosome, strategy):
        """
        """

        results = []

        if strategy == "absolute_mutation":
            if self._visitedNodes[chromosome.stringIdentifier] is not None:
                return None

            print("chrom : ", chromosome, self.searchDepth)

        shuffledPeriods = [(period, item) for period, item in enumerate(chromosome.stringIdentifier)]

        # print("shuffledPeriods : ", shuffledPeriods, chromosome.stringIdentifier)
        random.shuffle(shuffledPeriods)

        for period, item in shuffledPeriods:

            periodGene, periodGeneLowerLimit, periodGeneUpperLimit = None, None, None

            if item > 0:
                # print("ouais : ", chromosome, period, item)
                periodGene = Chromosome.geneAtPeriod(chromosome, period)
                periodGeneLowerLimit, periodGeneUpperLimit = Chromosome.geneLowerUpperLimit(chromosome, periodGene)
            
            i = 1
            backwardPeriod, forwardPeriod = period, period
            while True:
                if forwardPeriod is not None:
                    forwardPeriod = period + i
                if backwardPeriod is not None:
                    backwardPeriod = period - i

                if backwardPeriod is not None and backwardPeriod < 0:
                    backwardPeriod = None

                if forwardPeriod is not None and forwardPeriod > InputDataInstance.instance.nPeriods - 1:
                    forwardPeriod = None

                # print(backwardPeriod, forwardPeriod)
                if backwardPeriod is not None :
                    backwardPeriodTab = [False]
                    result = self.handleBackwardForwardItem(chromosome, backwardPeriod, "backward", item, strategy, period, periodGene, periodGeneLowerLimit, periodGeneUpperLimit, results, backwardPeriodTab)
                    if backwardPeriodTab[-1] == True:
                        backwardPeriod = None

                    if result == "RETURN":
                        return None

                if forwardPeriod is not None :
                    forwardPeriodTab = [False]
                    result = self.handleBackwardForwardItem(chromosome, forwardPeriod, "forward", item, strategy, period, periodGene, periodGeneLowerLimit, periodGeneUpperLimit, results, forwardPeriodTab)
                    if forwardPeriodTab[-1] == True:
                        forwardPeriod = None

                    if result == "RETURN":
                        return None

                if backwardPeriod is None and forwardPeriod is None:
                    break

                i += 1

                if strategy == "absolute_mutation":
                    if len(results) > 0:
                        self.searchDepth += 1
                        self._visitedNodes[chromosome.stringIdentifier] = 1
                        self.searchIndividu(results[-1], strategy)

                        if self._stopSearchEvent.is_set():
                            return None


        if strategy == "absolute_mutation":
            if len(results) == 0:
                self.result = chromosome
                self._stopSearchEvent.set()
                return None
        elif strategy == "simple_mutation":
            self.result = np.random.choice(results)
            return None


    def handleBackwardForwardItem(self, chromosome, shiftPeriod, shift, item, strategy, period, periodGene, periodGeneLowerLimit, periodGeneUpperLimit, results, shiftPeriodTab):
        """
        """
        
        mutation = None
        if chromosome.stringIdentifier[shiftPeriod] > 0: 
            shiftPeriodGene = Chromosome.geneAtPeriod(chromosome, shiftPeriod)

            shiftPeriodGeneLowerLimit, shiftPeriodGeneUpperLimit = Chromosome.geneLowerUpperLimit(chromosome, shiftPeriodGene)
            condition = shiftPeriodGeneLowerLimit <= period and period < shiftPeriodGeneUpperLimit

            if item > 0:
                condition = condition and (periodGeneLowerLimit <= shiftPeriod and shiftPeriod < periodGeneUpperLimit)

            if condition:
                # print("mutating : ", backwardPeriodGene)
                swap = [(shiftPeriodGene.item, shiftPeriodGene.position), (-1, period)] if item == 0 else [(shiftPeriodGene.item, shiftPeriodGene.position), (periodGene.item, periodGene.position)] 
                mutation = LocalSearchEngine.createMutatedChromosome(chromosome, swap)
                # print("Mutation : ", mutation)
            else:
                # backwardPeriod = None
                shiftPeriodTab[-1] = True
        else:
            if item > 0:
                if (periodGeneLowerLimit <= shiftPeriod and shiftPeriod < periodGeneUpperLimit):
                    swap = [(periodGene.item, periodGene.position), (-1, shiftPeriod)]
                    mutation = LocalSearchEngine.createMutatedChromosome(chromosome, swap)
                else:
                    # backwardPeriod = None
                    shiftPeriodTab[-1] = True

        if mutation is not None:
            if strategy == "random_mutation":
                self.result = mutation
                return "RETURN"

            if strategy == "simple_mutation":
                results.append(mutation)
                self.result = mutation

            if mutation.cost < chromosome.cost or (mutation.cost < chromosome.cost and mutation.stringIdentifier != chromosome.stringIdentifier):
                if strategy == "absolute_mutation":
                    results.append(mutation)
                if strategy == "simple_mutation":
                    return "RETURN"


    @classmethod
    def createMutatedChromosome(cls, chromosome, swap):
        """
        """

        # checking if this combination of chromosome swap has already been visited
        chromosome1, chromosome2, theChromosome = LocalSearchEngine.mutationsMemory["db"][(chromosome.stringIdentifier, swap[0], swap[1])], LocalSearchEngine.mutationsMemory["db"][(chromosome.stringIdentifier, swap[1], swap[0])], None
        if chromosome1 is not None:
            theChromosome = chromosome1

        if chromosome2 is not None:
            theChromosome = chromosome2

        if theChromosome is not None:
            # print("SAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWWWWWWWWWWWWWWWWWWWWWWWW")
            return theChromosome



        # Making up the stringIdentifier of the result chromosome
        stringIdentifier = list(chromosome.stringIdentifier)
        dnaArray = None

        gene1Item, gene1Position = swap[0][0], swap[0][1]
        # print("swap : ", swap, chromosome, chromosome.dnaArray, swap[1][0] == -1)
        if swap[1][0] == -1:
            newPeriod = swap[1][1]
            stringIdentifier[newPeriod] = gene1Item + 1
            stringIdentifier[(chromosome.dnaArray[gene1Item][gene1Position]).period] = 0
            stringIdentifier = tuple(stringIdentifier)
            if Chromosome.pool[stringIdentifier] is not None:
                with LocalSearchEngine.mutationsMemory["lock"]:
                    LocalSearchEngine.mutationsMemory["db"][(stringIdentifier, swap[0], swap[1])] = Chromosome.pool[stringIdentifier]
                return Chromosome.pool[stringIdentifier]

            dnaArray = copy.deepcopy(chromosome.dnaArray)
            gene1 = dnaArray[gene1Item][gene1Position]

            cost = chromosome.cost
            cost -= gene1.cost

            nextGene1, nextGene0 = Chromosome.nextProdGene(gene1.period, dnaArray, chromosome.stringIdentifier), Chromosome.nextProdGene(newPeriod, dnaArray, chromosome.stringIdentifier)
            prevGene0 = Chromosome.prevProdGene(newPeriod, dnaArray, chromosome.stringIdentifier)
            condition1 = nextGene0 is not None and nextGene0 == gene1
            condition2 = prevGene0 is not None and prevGene0 == gene1

            if not (condition1 or condition2):

                # print("nextGene1, nextGene0 : ", nextGene1, nextGene0)
                cost -= nextGene1.changeOverCost if nextGene1 is not None else 0
                cost -= nextGene0.changeOverCost if nextGene0 is not None else 0

                if nextGene1 is not None:
                    # print("before nextGene1 : ", nextGene1, nextGene1.changeOverCost)
                    nextGene1.prevGene = gene1.prevGene
                    nextGene1.calculateChangeOverCost()
                    nextGene1.calculateCost()
                    # print("after nextGene1 : ", nextGene1, nextGene1.changeOverCost)
                    cost += nextGene1.changeOverCost

                if nextGene0 is not None:
                    # print("before nextGene0 : ", nextGene0, nextGene0.changeOverCost)
                    (dnaArray[gene1Item][gene1Position]).prevGene = nextGene0.prevGene

                    nextGene0.prevGene = (gene1.item, gene1.position)
                    nextGene0.calculateChangeOverCost()
                    nextGene0.calculateCost()
                    # print("after nextGene0 : ", nextGene0, nextGene0.changeOverCost)
                    cost += nextGene0.changeOverCost
                else:
                    (dnaArray[gene1Item][gene1Position]).prevGene = (prevGene0.item, prevGene0.position)

            (dnaArray[gene1Item][gene1Position]).period = newPeriod
            (dnaArray[gene1Item][gene1Position]).calculateChangeOverCost()
            (dnaArray[gene1Item][gene1Position]).calculateStockingCost()
            (dnaArray[gene1Item][gene1Position]).calculateCost()

            # print("Ending with gene1 : ", (dnaArray[gene1Item][gene1Position]))

            cost += (dnaArray[gene1Item][gene1Position]).cost

            # print("kokooooooooooo : ", cost, stringIdentifier, dnaArray)

        else:
            gene2Item, gene2Position = swap[1][0], swap[1][1]
            period1, period2 = (chromosome.dnaArray[gene1Item][gene1Position]).period, (chromosome.dnaArray[gene2Item][gene2Position]).period
            stringIdentifier[period1] =  gene2Item + 1
            stringIdentifier[period2] =  gene1Item + 1
            stringIdentifier = tuple(stringIdentifier)

            if Chromosome.pool[stringIdentifier] is not None:
                with LocalSearchEngine.mutationsMemory["lock"]:
                    LocalSearchEngine.mutationsMemory["db"][(stringIdentifier, swap[0], swap[1])] = Chromosome.pool[stringIdentifier]
                return Chromosome.pool[stringIdentifier]

            dnaArray = copy.deepcopy(chromosome.dnaArray)

            # fixing the chromosome dnaArray and calculating the cost
            # print("dnaArray : ", dnaArray)
            gene1 = (dnaArray[gene1Item][gene1Position])
            gene2 = (dnaArray[gene2Item][gene2Position])

            cost = chromosome.cost

            cost -= (gene1.cost + gene2.cost)

            # print("preveeees --- : ", gene1.prevGene, gene2.prevGene)

            if gene1.prevGene == (gene2Item, gene2Position):
                gene1.prevGene = gene2.prevGene
                gene2.prevGene = (gene1.item, gene1.position)
                nextGene = Chromosome.nextProdGene(gene1.period, dnaArray, chromosome.stringIdentifier)

                # print("before before nextGene A: ", nextGene)

                if nextGene is not None:
                    # print("before nextGene A: ", nextGene, nextGene.changeOverCost)
                    cost -= nextGene.changeOverCost
                    prevGene = (gene2.item, gene2.position)
                    # print("prevGene A: ", prevGene)
                    nextGene.prevGene = prevGene
                    nextGene.calculateChangeOverCost()
                    nextGene.calculateCost()
                    cost += nextGene.changeOverCost
                    # print("after nextGene A: ", nextGene, nextGene.changeOverCost)

            elif gene2.prevGene == (gene1Item, gene1Position):
                gene2.prevGene = gene1.prevGene
                gene1.prevGene = (gene2.item, gene2.position)
                nextGene = Chromosome.nextProdGene(gene2.period, dnaArray, chromosome.stringIdentifier)

                # print("before before nextGene B: ", nextGene)

                if nextGene is not None:
                    # print("before nextGene B: ", nextGene, nextGene.changeOverCost)
                    cost -= nextGene.changeOverCost
                    prevGene = (gene1.item, gene1.position)
                    # print("prevGene B: ", prevGene)
                    nextGene.prevGene = prevGene
                    nextGene.calculateChangeOverCost()
                    nextGene.calculateCost()
                    cost += nextGene.changeOverCost
                    # print("after nextGene B: ", nextGene, nextGene.changeOverCost)

            else:
                gene1.prevGene, gene2.prevGene = gene2.prevGene, gene1.prevGene
                nextGene1, nextGene2 = Chromosome.nextProdGene(gene1.period, dnaArray, chromosome.stringIdentifier), Chromosome.nextProdGene(gene2.period, dnaArray, chromosome.stringIdentifier)

                # print("before before nextGene1 nextGene2 : ", nextGene1, nextGene2)

                if nextGene1 is not None:
                    # print("before nextGene1 : ", nextGene1, nextGene1.changeOverCost)
                    cost -= nextGene1.changeOverCost
                    prevGene = (gene2.item, gene2.position)
                    # print("prevGene : ", prevGene)
                    nextGene1.prevGene = prevGene
                    nextGene1.calculateChangeOverCost()
                    nextGene1.calculateCost()
                    cost += nextGene1.changeOverCost
                    # print("after nextGene1 : ", nextGene1, nextGene1.changeOverCost)

                if nextGene2 is not None:
                    # print("before nextGene2 : ", nextGene2, nextGene2.changeOverCost)
                    cost -= nextGene2.changeOverCost
                    prevGene = (gene1.item, gene1.position)
                    # print("prevGene : ", prevGene)
                    nextGene2.prevGene = prevGene
                    nextGene2.calculateChangeOverCost()
                    nextGene2.calculateCost()
                    cost += nextGene2.changeOverCost
                    # print("after nextGene2 : ", nextGene2, nextGene2.changeOverCost)


            gene1.period, gene2.period = gene2.period, gene1.period

            gene1.calculateStockingCost()
            gene1.calculateChangeOverCost()
            gene1.calculateCost()

            gene2.calculateStockingCost()
            gene2.calculateChangeOverCost()
            gene2.calculateCost()

            cost += (gene1.cost + gene2.cost)

        # print("Coooooost : ", cost, stringIdentifier, dnaArray, Chromosome.createFromIdentifier(stringIdentifier))

        result = Chromosome()
        result.dnaArray = dnaArray
        result.stringIdentifier = stringIdentifier
        result.cost = cost

        with LocalSearchEngine.mutationsMemory["lock"]:
            LocalSearchEngine.mutationsMemory["db"][(result.stringIdentifier, swap[0], swap[1])] = result
        return result

