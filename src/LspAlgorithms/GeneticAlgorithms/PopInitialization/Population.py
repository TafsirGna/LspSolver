from threading import Thread
import threading
import random
from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.GAOperators.CrossOverOperator import CrossOverOperator
from LspAlgorithms.GeneticAlgorithms.GAOperators.MutationOperator import MutationOperator
from LspAlgorithms.GeneticAlgorithms.GAOperators.SelectionOperator import SelectionOperator
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
            if self.maxCostChromosome.cost < chromosome.cost:
                self.maxCostChromosome = chromosome

        # setting population min cost
        if self.minCostChromosome is None:
            self.minCostChromosome = chromosome
        else:
            if self.minCostChromosome.cost > chromosome.cost:
                self.minCostChromosome = chromosome

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


    def localSeachOneIndividu(self):
        """ Selection randomly one chromosome upon which an advanced mutation function is performed
        """

        index = random.randrange(0, self.popSize - 1)
        # chromosome = random.choice(self.uniques)
        chromosome = self.chromosomes[index]

        mutationOperator = MutationOperator(chromosome)
        self.chromosomes[index] = mutationOperator.process(strategy="advanced")

        return


    def __repr__(self):
        """
        """
        return "Population : {} : \nCost Total :{} ".format(self.chromosomes, 0)
