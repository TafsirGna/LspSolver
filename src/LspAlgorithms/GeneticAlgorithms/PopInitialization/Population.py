import enum
from functools import total_ordering
from threading import Thread, local
import threading

import numpy as np
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
import random
from LspAlgorithms.GeneticAlgorithms.CrossOverOperator import CrossOverOperator
from LspAlgorithms.GeneticAlgorithms.Gene import Gene
from LspInputDataReading.LspInputDataInstance import InputDataInstance
from ParameterSearch.ParameterData import ParameterData

class Population:

    def __init__(self, chromosomes = [], popSize = None) -> None:
        """
        """
        self.chromosomes = chromosomes
        self.elites = []
        self.setElites()
        self.nextPopulation = None
        self._nextPopLock = threading.Lock()
        self.maxChromosomeCost = None

        self.popSize = popSize if popSize != None else ParameterData.instance.popSize

    def evolve(self):
        """
        """

        self.nextPopulation = Population([], self.popSize)
        self.applyGeneticOperators()
        return self.nextPopulation

    
    def setElites(self):
        """
        """
        if len(self.elites) > 0 or len(self.chromosomes) is 0:
            return

        nElites = int(float(len(self.chromosomes)) * ParameterData.instance.elitePercentage)
        nElites = ( 1 if nElites < 1 else nElites)

        # self.chromosomes.sorted(key= lambda chromosome: chromosome.cost) 
        chromosomes = sorted(self.chromosomes)

        self.elites = chromosomes[:nElites]


    def add(self, chromosome):
        """
        """

        if len(self.chromosomes) >= self.popSize:
            self.setElites()
            return None

        self.chromosomes.append(chromosome)

        # setting population max cost
        if self.maxChromosomeCost == None:
            self.maxChromosomeCost = chromosome.cost
        else:
            cost = chromosome.cost + 1
            if self.maxChromosomeCost < cost:
                self.maxChromosomeCost = cost

        return chromosome


    def threadTask(self, rouletteProbabilities):
        """
        """

        while len(self.nextPopulation.chromosomes) < self.popSize:

            chromosomeA, chromosomeB, chromosome = np.random.choice(self.chromosomes, p=rouletteProbabilities), np.random.choice(self.chromosomes, p=rouletteProbabilities), None

            if (random.random() < ParameterData.instance.crossOverRate):
                chromosome = Population.crossOverChromosomes(chromosomeA, chromosomeB)
                # print("+++", chromosome)

                if chromosome is not None and (random.random() < ParameterData.instance.mutationRate):
                    chromosome.mutate()

            if chromosome is not None:
                with self._nextPopLock:
                    if self.nextPopulation.add(chromosome) is None:
                        return
            


    def applyGeneticOperators(self, selection_strategy="roulette_wheel"):
        """
        """
        
        if selection_strategy == "roulette_wheel":
            self.applyRouletteWheel()


    def applyRouletteWheel(self):
        """
        """

        rouletteProbabilities = self.prepSelection()
        print("roulette ", rouletteProbabilities)
        threads = []

        for i in range(ParameterData.instance.nReplicaThreads):
            thread_T = Thread(target=self.threadTask, args=(rouletteProbabilities,))
            thread_T.start()
            threads.append(thread_T)
            
        [thread_T.join() for thread_T in threads]


    def prepSelection(self):
        """
        """
        totalFitness = 0
        for chromosome in self.chromosomes:
            chromosome.fitnessValue = self.maxChromosomeCost - chromosome.cost
            # print("888 ---> ", chromosome, chromosome.fitnessValue)
            totalFitness += chromosome.fitnessValue
        totalFitness = totalFitness
        # print("888 ---> ", totalFitness)

        return [float(chromosome.fitnessValue)/totalFitness for chromosome in self.chromosomes]


    def converged(self):
        """
        """
        uniques, unique_counts, fittest = [], [], self.chromosomes[0]

        for chromosome in self.chromosomes:
            if not (chromosome.dnaArray in uniques):
                uniques.append(chromosome.dnaArray)
                unique_counts.append(0)
            else:
                unique_counts[uniques.index(chromosome.dnaArray)] += 1

            if chromosome.cost < fittest.cost:
                fittest = chromosome

        localOptimal = uniques[unique_counts.index(max(unique_counts))]

        # Setting the threshold under which a populatioin is set to have converged
        threshold = int(ParameterData.instance.convergenceThresholdPercentage * len(self.chromosomes))
        threshold = 1 if threshold < 1 else threshold

        print('convergeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeed', len(uniques), self.chromosomes)
        if len(uniques) <= threshold and localOptimal == fittest.dnaArray:
            # print('convergeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeed')
            return True
        return False


    def __repr__(self):
        """
        """
        return "Population : {} : \nCost Total :{} ".format(self.chromosomes, 0)


    @classmethod
    def fillNullPeriods(cls, dnaArray):
        """
        """

        plainDNA = Chromosome.classRenderDnaArray(dnaArray)

        print("=== Before ", dnaArray, plainDNA , ' | ', InputDataInstance.instance.demandsArrayZipped)

        for item, itemGenes in enumerate(dnaArray):
            for position, itemGene in enumerate(itemGenes):
                print("item : ", item, 'index : ', itemGene, "None : ", itemGene is None, "indices : ", itemGenes)

                if itemGene is None:

                    lowerLimit = 0 if position == 0 else (dnaArray[item][position - 1]).period + 1
                    upperLimit = InputDataInstance.instance.demandsArrayZipped[item][position] + 1 if position == len(InputDataInstance.instance.demandsArrayZipped[item]) - 1 else (dnaArray[item][position + 1]).period

                    print("Portion : ", lowerLimit, upperLimit, plainDNA[lowerLimit:upperLimit])

                    j = upperLimit - 1
                    filled = False
                    while j >= lowerLimit:

                        periodValue = plainDNA[j]
                        print("periodValue : ", periodValue)
                        if periodValue == 0:
                            gene = Gene(item, j, position)
                            gene.calculateStockingCost()
                            (dnaArray[item][position]) = gene
                            plainDNA = Chromosome.classRenderDnaArray(dnaArray)
                            print("result 1 : ", dnaArray)
                            filled = True
                            break

                        j -= 1

                    # if it still none then 
                    if filled:
                        print("still none")
                        return None
        
        # print("=== After ", dnaArray, plainDNA, Chromosome.feasible(dnaArray, InputDataInstance.instance))

        return dnaArray

    # @classmethod
    # def repairDna(cls, dnaArray):
    #     """
    #     """

    #     dnaArray = Population.fillNullPeriods(dnaArray)

    #     if dnaArray == None:
    #         return None, 0

    #     dnaArray, cost = Chromosome.arrangeDna(dnaArray)

    #     # print("=== After ", dnaArray, Chromosome.classRenderDnaArray(dnaArray), cost)
    #     # print("=== After ", dnaArray, Chromosome.classRenderDnaArray(dnaArray), cost, Chromosome.calculateCostPlainDNA(Chromosome.classRenderDnaArray(dnaArray), InputDataInstance.instance), "price*", cost == Chromosome.calculateCostPlainDNA(Chromosome.classRenderDnaArray(dnaArray), InputDataInstance.instance))
    #     return dnaArray, cost


    @classmethod
    def crossOverChromosomes(cls, chromosomeA, chromosomeB) -> Chromosome:
        """
        """

        dnaArray = [[ None for _ in row ] for row in InputDataInstance.instance.demandsArrayZipped]
        
        # chromosomeA, chromosomeB = (chromosomeA, chromosomeB) if chromosomeA < chromosomeB else (chromosomeB, chromosomeA)
        # genesList = sorted([gene for itemProdGenes in chromosomeA.dnaArray for gene in itemProdGenes], key= lambda gene: gene.cost)

        visitedPeriods = []
        # for geneA in genesList:
        #     geneB = chromosomeB.dnaArray[geneA.item][geneA.position]
        #     geneA, geneB = (geneA, geneB) if geneA.stockingCost <= geneB.stockingCost else (geneB, geneA)
        #     if dnaArray[geneA.item][geneA.position] == None:
        #         if not(geneA.period in visitedPeriods):
        #             dnaArray[geneA.item][geneA.position] = geneA
        #             visitedPeriods.append(geneA.period)
        #         elif not(geneB.period in visitedPeriods):
        #             dnaArray[geneB.item][geneB.position] = geneB
        #             visitedPeriods.append(geneB.period)







        # for item, itemGenes in enumerate(chromosomeA.dnaArray):
        #     bottomLimit, topLimit = -1, InputDataInstance.instance.demandsArrayZipped[item][0]
        #     for position, geneA in enumerate(itemGenes):
        #         geneB = chromosomeB.dnaArray[item][position]
        #         geneA, geneB = (geneA, geneB) if geneA.stockingCost <= geneB.stockingCost else (geneB, geneA)
        #         if dnaArray[item][position] == None:
        #             if not(geneA.period in visitedPeriods) and (bottomLimit < geneA.period and geneA.period <= topLimit):
        #                 dnaArray[geneA.item][geneA.position] = geneA
        #                 visitedPeriods.append(geneA.period)
        #             elif not(geneB.period in visitedPeriods) and (bottomLimit < geneB.period and geneB.period <= topLimit):
        #                 dnaArray[geneB.item][geneB.position] = geneB
        #                 visitedPeriods.append(geneB.period)
        #         bottomLimit = (dnaArray[item][position]).period if (dnaArray[item][position]) is not None else bottomLimit
        #         topLimit = InputDataInstance.instance.demandsArrayZipped[item][position + 1] if position < len(itemGenes) - 1 else 0


        crossOverOperator = CrossOverOperator([chromosomeA, chromosomeB])
        chromosome = crossOverOperator.process()

        return chromosome
