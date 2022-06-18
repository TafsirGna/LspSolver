from collections import defaultdict
import copy
import random
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.Gene import Gene
from LspInputDataReading.LspInputDataInstance import InputDataInstance
import threading
import numpy as np


class LocalSearchNode:
    """
    """

    absoluteSearchedInstances = defaultdict(lambda: None)
    mutationsMemory = {"lock": threading.Lock(), "db":defaultdict(lambda: None)}
    genericGeneIndices = None

    def __init__(self, chromosome, rootChromosome = None) -> None:
        """
        """

        self.rootChromosome = rootChromosome
        self.chromosome = chromosome


    def generateChild(self, depthIndex):
        """
        """

        # genes = [gene for itemGenes in self.chromosome.dnaArray for gene in itemGenes]
        random.seed()
        # random.shuffle(genes)
        genesIndices = copy.deepcopy(LocalSearchNode.genericGeneIndices)

        while len(genesIndices) > 0:
            geneIndex = genesIndices[random.randrange(len(genesIndices))]
            gene = self.chromosome.dnaArray[geneIndex[0]][geneIndex[1]]
            genesIndices.remove(geneIndex)
            for mutation in LocalSearchNode.generateGeneMutations(gene, self.chromosome):
                chromosome = mutation[1]
                # print("Child : ", chromosome)
                rootChromosome = self.rootChromosome if self.rootChromosome is not None else self.chromosome
                # if LocalSearchNode.absoluteSearchedInstances[rootChromosome.stringIdentifier] is not None:
                #     (LocalSearchNode.absoluteSearchedInstances[rootChromosome.stringIdentifier]["path"][depthIndex]["moves"]).append(mutation[2])
                yield LocalSearchNode(chromosome, rootChromosome)

        # return []
        yield None


    def children(self):
        """
        """

        children = []

        for child in self.generateChild():
            # print("child : ", child)
            children.append(child)

        children.sort(reverse=True)
        return children


    @classmethod
    def createMutatedChromosome(cls, chromosome, swap):
        """
        """

        # checking if this combination of chromosome swap has already been visited
        chromosome1, chromosome2, theChromosome = LocalSearchNode.mutationsMemory["db"][(chromosome.stringIdentifier, swap[0], swap[1])], LocalSearchNode.mutationsMemory["db"][(chromosome.stringIdentifier, swap[1], swap[0])], None
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
                with LocalSearchNode.mutationsMemory["lock"]:
                    LocalSearchNode.mutationsMemory["db"][(stringIdentifier, swap[0], swap[1])] = Chromosome.pool[stringIdentifier]
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
                with LocalSearchNode.mutationsMemory["lock"]:
                    LocalSearchNode.mutationsMemory["db"][(stringIdentifier, swap[0], swap[1])] = Chromosome.pool[stringIdentifier]
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

        with LocalSearchNode.mutationsMemory["lock"]:
            LocalSearchNode.mutationsMemory["db"][(result.stringIdentifier, swap[0], swap[1])] = result
        return result


    @classmethod
    def generateGeneMutations(cls, gene1, chromosome, strategy = "all"):
        """
        """

        # print('gene1 : ', gene1.item, gene1.position, gene1.period, chromosome, chromosome.dnaArray)

        gene1LowerLimit = 0 if gene1.position == 0 else (chromosome.dnaArray[gene1.item][gene1.position - 1]).period + 1
        gene1UpperLimit = InputDataInstance.instance.demandsArrayZipped[gene1.item][gene1.position] + 1 if gene1.position == len(InputDataInstance.instance.demandsArrayZipped[gene1.item]) - 1 else ((chromosome.dnaArray[gene1.item][gene1.position + 1]).period if (chromosome.dnaArray[gene1.item][gene1.position + 1]) is not None else InputDataInstance.instance.demandsArrayZipped[gene1.item][gene1.position] + 1)
        gene1UpperLimit = InputDataInstance.instance.demandsArrayZipped[gene1.item][gene1.position] + 1 if InputDataInstance.instance.demandsArrayZipped[gene1.item][gene1.position] + 1 < gene1UpperLimit else gene1UpperLimit

        # print("lower and upper limit 1 : ", gene1LowerLimit, gene1UpperLimit)

        index = len(chromosome.stringIdentifier[gene1LowerLimit:gene1UpperLimit]) - 1
        for periodValue in reversed(chromosome.stringIdentifier[gene1LowerLimit:gene1UpperLimit]):
            period = index + gene1LowerLimit

            if periodValue == 0:
                swap = [(gene1.item, gene1.position), (-1, period)]
                mutation = [chromosome, LocalSearchNode.createMutatedChromosome(chromosome, swap), swap]
                yield mutation
            else:
                if strategy == "all":
                    item2 = periodValue - 1
                    if item2 != gene1.item:
                        gene2 = [gene for gene in chromosome.dnaArray[item2] if gene.period == period]
                        gene2 = gene2[0]
                        # print('gene2 : ', gene2.item, gene2.position, gene2.period)

                        gene2LowerLimit = 0 if gene2.position == 0 else (chromosome.dnaArray[gene2.item][gene2.position - 1]).period + 1
                        gene2UpperLimit = InputDataInstance.instance.demandsArrayZipped[gene2.item][gene2.position] + 1 if gene2.position == len(InputDataInstance.instance.demandsArrayZipped[gene2.item]) - 1 else (chromosome.dnaArray[gene2.item][gene2.position + 1]).period
                        gene2UpperLimit = InputDataInstance.instance.demandsArrayZipped[gene2.item][gene2.position] + 1 if InputDataInstance.instance.demandsArrayZipped[gene2.item][gene2.position] + 1 < gene2UpperLimit else gene2UpperLimit
                        # print("lower and upper limit 2 : ", gene2LowerLimit, gene2UpperLimit)

                        if (gene2LowerLimit <= gene1.period and gene1.period < gene2UpperLimit) and (gene1LowerLimit <= gene2.period and gene2.period < gene1UpperLimit):
                            swap = [(gene1.item, gene1.position), (gene2.item, gene2.position)]
                            mutation = [chromosome, LocalSearchNode.createMutatedChromosome(chromosome, swap), swap]
                            yield mutation

            index -= 1

        return []


    def __lt__(self, node) -> bool:
        """
        """
        return self.chromosome < node.chromosome

    def __eq__(self, node) -> bool:
        """
        """
        return self.chromosome == node.chromosome and self.rootChromosome == node.rootChromosome

    def __repr__(self) -> str:
        return str(self.chromosome)

    # def __hash__(self) -> int:
    #     return hash(self.chromosome.stringIdentifier)
