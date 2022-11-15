from collections import defaultdict
import multiprocessing as mp
import numpy as np
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Chromosome import Chromosome
from ParameterSearch.ParameterData import ParameterData
from queue import Queue
import concurrent.futures

class SelectionOperator:
    """
    """

    def __init__(self, population, strategy = "roulette_wheel") -> None:
        """
        """

        self.population = population
        self.chromosomes = list(self.population.chromosomes)

        self.rouletteProbabilities = [0] * len(self.chromosomes)
        self.setRouletteProbabilities()
        
        # the index tracking the current position of the cursor on the list 
        self.currentIndex = 0
        self.selectedPool = set()


    def fitnessCalculationTask(self, slice, resultQueue):
        """
        """

        maxCost = self.population.worst.cost + 1
        totalFitness = 0
        fitnessArray = []
        for chromosome in slice:
            fitness = maxCost - chromosome.cost
            totalFitness += fitness
            fitnessArray.append(fitness)

        fitnessArray.append(totalFitness)
        resultQueue.put(fitnessArray)


    def setRouletteProbabilities(self):
        """
        """

        nThreads = ParameterData.instance.nReplicaSubThreads
        slices = np.array_split(self.chromosomes, nThreads)

        # processes = []
        resultQueues = [Queue()] * nThreads

        with concurrent.futures.ThreadPoolExecutor() as executor:
            print(list(executor.map(self.fitnessCalculationTask, slices, resultQueues)))


        totalFitness = 0
        fitnessArray = []
        for resultQueue in resultQueues:
            result = resultQueue.get()
            totalFitness += result[-1]
            fitnessArray += result[:-1]

        self.rouletteProbabilities = [float(fitness/totalFitness) for fitness in fitnessArray]

        print("**************************")
        print("Roulette : ", self.chromosomes, " \n ", self.rouletteProbabilities)
        print("++++++++++++++++++++++++++")


    def select(self):
        """
        """

        return self.rouletteWheelSelect()


    def rouletteWheelSelect(self):
        """
        """

        if self.currentIndex >= len(self.chromosomes): # very much less likely to happen but you dunno
            return None, None

        chromosomeA = self.chromosomes[self.currentIndex]
        while chromosomeA in self.selectedPool:
            self.currentIndex += 1
            chromosomeA = self.chromosomes[self.currentIndex]

        chromosomeB = np.random.choice(self.chromosomes, p=self.rouletteProbabilities)
        while chromosomeB == chromosomeA:
            chromosomeB = np.random.choice(self.chromosomes, p=self.rouletteProbabilities)

        self.currentIndex += 1

        # adding selected chromosomes to the selectedpool property
        self.selectedPool.add(chromosomeA)
        self.selectedPool.add(chromosomeB)

        return chromosomeA, chromosomeB

        # chromosomeA, chromosomeB = np.random.choice(self.chromosomes, p=self.rouletteProbabilities), np.random.choice(self.chromosomes, p=self.rouletteProbabilities)
        # return chromosomeA, chromosomeB
