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
        self.strategy = strategy
        if self.strategy == "roulette_wheel":
            self.rouletteProbabilities = [0] * len(self.population.chromosomes)
            self.setRouletteProbabilities()


    def fitnessCalculationTask(self, slice, resultQueue):
        """
        """

        maxCost = self.population.chromosomes[-1].cost + 1
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
        slices = np.array_split(self.population.chromosomes, nThreads)

        processes = []
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
        print("Roulette : ", self.population.chromosomes, " \n ", self.rouletteProbabilities)
        print("++++++++++++++++++++++++++")


    def select(self):
        """
        """

        result = None

        if self.strategy == "roulette_wheel":
            result = self.rouletteWheelSelect()

        return result


    def rouletteWheelSelect(self):
        """
        """
        # print("*************** : ",  len(self.population.chromosomes), len(self.rouletteProbabilities))

        chromosomeA, chromosomeB = np.random.choice(self.population.chromosomes, p=self.rouletteProbabilities), np.random.choice(self.population.chromosomes, p=self.rouletteProbabilities)
        chromosomeA, chromosomeB = Chromosome.popByThread[self.population.threadIdentifier]["content"][chromosomeA.stringIdentifier], Chromosome.popByThread[self.population.threadIdentifier]["content"][chromosomeB.stringIdentifier]

        return chromosomeA, chromosomeB
