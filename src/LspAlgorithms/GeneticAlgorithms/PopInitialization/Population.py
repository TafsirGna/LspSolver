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
        self.selectionOperatorLock = threading.Lock()
        self.maxCostChromosome, self.minCostChromosome = None, None
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

        if chromosome not in self.uniques:
            self.uniques.append(chromosome)

        # setting population max cost
        if self.maxCostChromosome is None:
            self.maxCostChromosome = chromosome
        else:
            if self.maxCostChromosome.cost < chromosome.cost + 1:
                self.maxCostChromosome = chromosome

        return chromosome


    def threadTask(self, selectionOperator):
        """
        """

        while len(self.nextPopulation.chromosomes) < self.popSize:

            chromosome = None
            if (random.random() < ParameterData.instance.crossOverRate):

                with self.selectionOperatorLock:
                    chromosomeA, chromosomeB = selectionOperator.select()

                crossOverOperator = CrossOverOperator([chromosomeA, chromosomeB])
                chromosome = crossOverOperator.process()
                # print("+++", chromosomeA, chromosomeB, chromosome)

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

        selectionOperator = SelectionOperator(self)

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
