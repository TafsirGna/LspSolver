from collections import defaultdict
from threading import Thread
import threading
import random
import concurrent.futures
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.GAOperators.CrossOverOperator import CrossOverOperator
from LspAlgorithms.GeneticAlgorithms.GAOperators.MutationOperator import MutationOperator
from LspAlgorithms.GeneticAlgorithms.GAOperators.SelectionOperator import SelectionOperator
from LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData

class Population:

    def __init__(self, chromosomes = [], popSize = None) -> None:
        """
        """
        self.chromosomes = chromosomes
        self.elites = None

        self.nextPopulation = None
        self._nextPopLock = threading.Lock()
        self.selectionOperatorLock = threading.Lock()
        self.maxCostChromosome, self.minCostChromosome = None, None
        self.uniques = defaultdict(lambda: None)

        self.popSize = popSize if popSize != None else ParameterData.instance.popSize
        self.threadId = None

        #
        for chromosome in self.chromosomes:
            self.uniques[chromosome.stringIdentifier] = chromosome

    def evolve(self):
        """
        """
    
        self.uniques = defaultdict(lambda: None)
        # print("Staaaaaaaaaaaaaaaaaaaaart : ", self.uniques, "\n")
        self.nextPopulation = Population(LspRuntimeMonitor.popsData[self.threadId]["elites"], self.popSize)
        # print("Eliiiiiiiiiiiiiiiiiiiiites : ", LspRuntimeMonitor.popsData[self.threadId]["elites"])
        self.nextPopulation.threadId = self.threadId
        self.applyGeneticOperators()
        return self.nextPopulation


    def completeInit(self):
        """
        """

        chromosomes = sorted(self.uniques.values())
        self.maxCostChromosome = chromosomes[-1]
        self.minCostChromosome = chromosomes[0]
        # print("maaaaaaaaaaaaaax-------------", self.maxCostChromosome)

        self.elites = Population.elites(self)

    @classmethod
    def elites(cls, population):

        chromosomes = sorted(population.uniques.values())
        elites = []

        if LspRuntimeMonitor.popsData[population.threadId] is not None:
            nElites = len(LspRuntimeMonitor.popsData[population.threadId]["elites"])
            if nElites == 0:
                nElites = int(population.popSize * ParameterData.instance.elitePercentage) 
                nElites = (1 if nElites < 1 else nElites)
                elites = chromosomes[:nElites]
            else:
                elites = chromosomes[:nElites]
        # print("After Elite setting -- : ", self.elites)
        return elites


    def add(self, chromosome):
        """
        """

        if len(self.chromosomes) >= self.popSize:
            return None

        self.chromosomes.append(chromosome)

        if self.uniques[chromosome.stringIdentifier] is None:
            self.uniques[chromosome.stringIdentifier] = chromosome 

        # Chromosome Pool
        if Chromosome.pool[chromosome.stringIdentifier] is None:
            Chromosome.pool[chromosome.stringIdentifier] = chromosome   

        return chromosome


    def threadTask(self, selectionOperator):
        """
        """

        while len(self.nextPopulation.chromosomes) < self.popSize:

            chromosome = None
            if (random.random() < ParameterData.instance.crossOverRate):

                with self.selectionOperatorLock:
                    chromosomeA, chromosomeB = selectionOperator.select()

                chromosome = (CrossOverOperator([chromosomeA, chromosomeB])).process()
                # if not Chromosome.feasible(chromosome):
                #     print("Roooooooooooooooooooooooooooogue")
                # print("+++", chromosomeA, chromosomeB, chromosome)

                if chromosome is not None and (random.random() < ParameterData.instance.mutationRate):
                    # Proceding to mutate the chromosome
                    chromosome = (MutationOperator()).process(chromosome)

            if chromosome is not None:
                with self._nextPopLock:
                    if self.nextPopulation.add(chromosome) is None:
                        return
            


    def applyGeneticOperators(self, selection_strategy="roulette_wheel"):
        """
        """

        selectionOperator = SelectionOperator(self)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for i in range(ParameterData.instance.nReplicaThreads):
                executor.submit(self.threadTask, selectionOperator)


    def __repr__(self):
        """
        """
        return "Population : {} : \nCost Total :{} ".format(self.chromosomes, 0)
