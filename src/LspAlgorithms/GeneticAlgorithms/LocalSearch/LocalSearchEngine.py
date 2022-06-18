from collections import defaultdict
import threading
import copy
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
# from LspAlgorithms.GeneticAlgorithms.LocalSearch.LocalSearchNode import LocalSearchNode
from ParameterSearch.ParameterData import ParameterData
import concurrent.futures
from LspInputDataReading.LspInputDataInstance import InputDataInstance
import random

class LocalSearchEngine:
    """
    """

    genericGeneIndices = None
    mutationsMemory = {"lock": threading.Lock(), "db":defaultdict(lambda: None)}

    def __init__(self) -> None:
        """
        """

        self.chromosome = None
        self.searchDepth = 0
        self.result = None
        self.nullPeriodsOrdered = None
        self._stopSearchEvent = threading.Event()

        # if LocalSearchEngine.genericGeneIndices is None:
        #     LocalSearchEngine.genericGeneIndices = [(item, position) for item, itemGenes in enumerate(InputDataInstance.instance.demandsArrayZipped) for position, _ in enumerate(itemGenes)]


    def process(self, chromosome, strategy = "simple_mutation"):
        """Process the given chromosome in order to return a mutated version
        strategy: simple_mutation|absolute_mutation|positive_mutation
        """

        # print("mutatiooooooon", strategy, chromosome, chromosome.dnaArray)

        self._visitedNodes = defaultdict(lambda: None)
        self.chromosome = chromosome

        self.searchIndividu(chromosome, strategy)

        return (self.result if self.result is not None else self.chromosome)


    def searchIndividu(self, chromosome, strategy):
        """
        """

        if strategy == "absolute_mutation":
            if self._visitedNodes[chromosome.stringIdentifier] is not None:
                return None

            print("chrom : ", chromosome, self.searchDepth)
            results = []

        if self.nullPeriodsOrdered is None:
            self.nullPeriodsOrdered = [period for period, periodValue in enumerate(self.chromosome.stringIdentifier) if periodValue == 0]

        print("nullPeriodsOrdered : ", self.nullPeriodsOrdered)
        random.shuffle(self.nullPeriodsOrdered)

        for nullPeriod in self.nullPeriodsOrdered:
            
            i = 1
            backwardPeriod, forwardPeriod = nullPeriod, nullPeriod
            while True:
                if forwardPeriod is not None:
                    forwardPeriod = nullPeriod + i
                if backwardPeriod is not None:
                    backwardPeriod = nullPeriod - i

                if backwardPeriod is not None and backwardPeriod < 0:
                    backwardPeriod = None

                if forwardPeriod is not None and forwardPeriod > InputDataInstance.instance.nPeriods - 1:
                    forwardPeriod = None

                # print(backwardPeriod, forwardPeriod)
                if backwardPeriod is not None and chromosome.stringIdentifier[backwardPeriod] > 0: 
                    backwardPeriodGene = Chromosome.geneAtPeriod(chromosome, backwardPeriod)

                    backwardPeriodGeneLowerLimit, backwardPeriodGeneUpperLimit = Chromosome.geneLowerUpperLimit(chromosome, backwardPeriodGene)
                    if backwardPeriodGeneLowerLimit <= nullPeriod and nullPeriod < backwardPeriodGeneUpperLimit:
                        print("mutating : ", backwardPeriodGene)
                        mutation = LocalSearchEngine.createMutatedChromosome(chromosome, [(backwardPeriodGene.item, backwardPeriodGene.position), (-1, nullPeriod)])
                        print("Mutation : ", mutation)
                        if mutation.cost <= chromosome.cost:
                            if strategy == "simple_mutation":
                                self.result = mutation
                                return None
                            elif strategy == "absolute_mutation":
                                results.append(mutation)
                    else:
                        backwardPeriod = None

                if forwardPeriod is not None and chromosome.stringIdentifier[forwardPeriod] > 0:
                    forwardPeriodGene = Chromosome.geneAtPeriod(chromosome, forwardPeriod)

                    forwardPeriodGeneLowerLimit, forwardPeriodGeneUpperLimit = Chromosome.geneLowerUpperLimit(chromosome, forwardPeriodGene)
                    if forwardPeriodGeneLowerLimit <= nullPeriod and nullPeriod < forwardPeriodGeneUpperLimit:
                        print("mutating : ", forwardPeriodGene)
                        mutation = LocalSearchEngine.createMutatedChromosome(chromosome, [(forwardPeriodGene.item, forwardPeriodGene.position), (-1, nullPeriod)])
                        print("Mutation : ", mutation)
                        if mutation.cost <= chromosome.cost:
                            if strategy == "simple_mutation":
                                self.result = mutation
                                return None
                    else:
                        forwardPeriod = None

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

