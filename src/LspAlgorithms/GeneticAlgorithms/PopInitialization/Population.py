from collections import defaultdict
from math import ceil
from queue import Queue
import random
import concurrent.futures
import uuid
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
        self.uniques = defaultdict(lambda: None)
        for chromosome in self.chromosomes:
            self.uniques[chromosome.stringIdentifier] = chromosome

        self.elites = None

        self.maxCostChromosome, self.minCostChromosome = None, None

        self.popSize = popSize if popSize != None else ParameterData.instance.popSize
        self.threadId = None

        self.threadPipes = defaultdict(lambda: Queue(maxsize=ceil(self.popSize/ParameterData.instance.nReplicaThreads)))
        self.newPop = None


    def evolve(self):
        """
        """
        selectionOperator = SelectionOperator(self)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            print(list(executor.map(self.threadTask, [selectionOperator] * ParameterData.instance.nReplicaThreads)))
            # executor.submit(self.getNewPopulation)

        self.getNewPopulation()
        return self.newPop

    
    def getNewPopulation(self):
        """
        """

        self.newPop = Population(LspRuntimeMonitor.popsData[self.threadId]["elites"], self.popSize)
        self.newPop.threadId = self.threadId

        while len(self.newPop.chromosomes) < self.popSize:

            # print("okooooooooooooooooo 1")
            for pipe in self.threadPipes.values():
                # print("okooooooooooooooooo 2")
                chromosome = pipe.get()
                result = self.newPop.add(chromosome)
                if result is None:
                    return


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
                nElites = int(len(population.chromosomes) * ParameterData.instance.elitePercentage) 
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
        threadID = uuid.uuid4()

        while not self.threadPipes[threadID].full():

            chromosomeA, chromosomeB = selectionOperator.select()
            chromosome = None
            if (random.random() < ParameterData.instance.crossOverRate):
                chromosome = (CrossOverOperator([chromosomeA, chromosomeB])).process()
            else:
                chromosome = chromosomeA if chromosomeA < chromosomeB else chromosomeB

            if chromosome is not None and (random.random() < ParameterData.instance.mutationRate):
                # Proceding to mutate the chromosome
                chromosome = (MutationOperator()).process(chromosome)

            if chromosome is not None:
                # print("Chromo --- ", chromosome)
                self.threadPipes[threadID].put(chromosome)

            # print("Thread : ", threadID, chromosome)


    def __repr__(self):
        """
        """
        return "Population : {} : \nCost Total :{} ".format(self.chromosomes, 0)
