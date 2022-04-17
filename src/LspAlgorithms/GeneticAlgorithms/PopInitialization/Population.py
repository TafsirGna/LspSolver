import enum
from functools import total_ordering
from threading import Thread, local
import threading

import numpy as np
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
import random
from LspAlgorithms.GeneticAlgorithms.CrossOverOperator import CrossOverOperator
from LspAlgorithms.GeneticAlgorithms.Gene import Gene
from LspAlgorithms.GeneticAlgorithms.MutationOperator import MutationOperator
from LspAlgorithms.GeneticAlgorithms.SelectionOperator import SelectionOperator
from LspInputDataReading.LspInputDataInstance import InputDataInstance
from ParameterSearch.ParameterData import ParameterData

class Population:

    def __init__(self, chromosomes = [], popSize = None) -> None:
        """
        """
        self.chromosomes = chromosomes
        self.elites = []
        # self.setElites()
        self.nextPopulation = None
        self._nextPopLock = threading.Lock()
        self.maxChromosomeCost = None
        self.uniques = []

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
            # self.setElites()
            return None

        self.chromosomes.append(chromosome)

        if not(chromosome.stringIdentifier in self.uniques):
            self.uniques.append(chromosome.stringIdentifier)

        # setting population max cost
        if self.maxChromosomeCost == None:
            self.maxChromosomeCost = chromosome.cost
        else:
            cost = chromosome.cost + 1
            if self.maxChromosomeCost < cost:
                self.maxChromosomeCost = cost

        return chromosome


    def threadTask(self, selectionOperator):
        """
        """

        while len(self.nextPopulation.chromosomes) < self.popSize:

            chromosomeA, chromosomeB = selectionOperator.select()
            chromosome = None

            if (random.random() < ParameterData.instance.crossOverRate):
                crossOverOperator = CrossOverOperator([chromosomeA, chromosomeB])
                chromosome = crossOverOperator.process()
                # print("+++", chromosome)

                if chromosome is not None and (random.random() < ParameterData.instance.mutationRate):
                    # Proceding to mutate the chromosome
                    mutationOperator = MutationOperator(chromosome)
                    chromosome = mutationOperator.process()

            if chromosome is not None:
                with self._nextPopLock:
                    if self.nextPopulation.add(chromosome) is None:
                        return
            


    def applyGeneticOperators(self, selection_strategy="roulette_wheel"):
        """
        """

        selectionOperator = SelectionOperator(self.chromosomes, self.maxChromosomeCost)

        threads = []

        for i in range(ParameterData.instance.nReplicaThreads):
            thread_T = Thread(target=self.threadTask, args=(selectionOperator,))
            thread_T.start()
            threads.append(thread_T)
            
        [thread_T.join() for thread_T in threads]


    def __repr__(self):
        """
        """
        return "Population : {} : \nCost Total :{} ".format(self.chromosomes, 0)



    # @classmethod
    # def crossOverChromosomes(cls, chromosomeA, chromosomeB) -> Chromosome:
    #     """
    #     """

    #     dnaArray = [[ None for _ in row ] for row in InputDataInstance.instance.demandsArrayZipped]
        
    #     # chromosomeA, chromosomeB = (chromosomeA, chromosomeB) if chromosomeA < chromosomeB else (chromosomeB, chromosomeA)
    #     # genesList = sorted([gene for itemProdGenes in chromosomeA.dnaArray for gene in itemProdGenes], key= lambda gene: gene.cost)

    #     visitedPeriods = []
    #     # for geneA in genesList:
    #     #     geneB = chromosomeB.dnaArray[geneA.item][geneA.position]
    #     #     geneA, geneB = (geneA, geneB) if geneA.stockingCost <= geneB.stockingCost else (geneB, geneA)
    #     #     if dnaArray[geneA.item][geneA.position] == None:
    #     #         if not(geneA.period in visitedPeriods):
    #     #             dnaArray[geneA.item][geneA.position] = geneA
    #     #             visitedPeriods.append(geneA.period)
    #     #         elif not(geneB.period in visitedPeriods):
    #     #             dnaArray[geneB.item][geneB.position] = geneB
    #     #             visitedPeriods.append(geneB.period)







    #     # for item, itemGenes in enumerate(chromosomeA.dnaArray):
    #     #     bottomLimit, topLimit = -1, InputDataInstance.instance.demandsArrayZipped[item][0]
    #     #     for position, geneA in enumerate(itemGenes):
    #     #         geneB = chromosomeB.dnaArray[item][position]
    #     #         geneA, geneB = (geneA, geneB) if geneA.stockingCost <= geneB.stockingCost else (geneB, geneA)
    #     #         if dnaArray[item][position] == None:
    #     #             if not(geneA.period in visitedPeriods) and (bottomLimit < geneA.period and geneA.period <= topLimit):
    #     #                 dnaArray[geneA.item][geneA.position] = geneA
    #     #                 visitedPeriods.append(geneA.period)
    #     #             elif not(geneB.period in visitedPeriods) and (bottomLimit < geneB.period and geneB.period <= topLimit):
    #     #                 dnaArray[geneB.item][geneB.position] = geneB
    #     #                 visitedPeriods.append(geneB.period)
    #     #         bottomLimit = (dnaArray[item][position]).period if (dnaArray[item][position]) is not None else bottomLimit
    #     #         topLimit = InputDataInstance.instance.demandsArrayZipped[item][position + 1] if position < len(itemGenes) - 1 else 0


        

    #     return chromosome
