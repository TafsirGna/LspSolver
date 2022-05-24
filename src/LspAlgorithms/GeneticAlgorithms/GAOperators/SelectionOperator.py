from collections import defaultdict
import multiprocessing as mp
import numpy as np
from LspAlgorithms.GeneticAlgorithms import Chromosome
from LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData

class SelectionOperator:
    """
    """

    def __init__(self, population) -> None:
        """
        """
        
        # self.chromosomeIndex = 0
        self.rouletteProbabilities = [0] * len(population.chromosomes)
        self.setRouletteProbabilities(population)


    def fitnessCalculationTask(self, maxCost, slice, resultQueue, population):
        """
        """

        totalFitness = 0
        fitnessArray = []
        for chromosome in slice:
            fitness = (maxCost - chromosome.cost) * population.chromosomes[chromosome.stringIdentifier]["size"]
            if fitness < 0:
                print("------------------------------------------------------", maxCost, chromosome.cost)
            totalFitness += fitness
            fitnessArray.append(fitness)

        fitnessArray.append(totalFitness)
        resultQueue.put(fitnessArray)


    def setRouletteProbabilities(self, population):
        """
        """

        self.chromosomes = [element["chromosome"] for element in population.chromosomes.values()]

        maxCost = LspRuntimeMonitor.popsData[population.lineageIdentifier]["max"][-1] + 1
        nProcesses = ParameterData.instance.nReplicaSubThreads
        slices = np.array_split(self.chromosomes, nProcesses)

        # Process code

        processes = []
        resultQueues = []

        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     for processIndex in range(nProcesses):
        #         resultQueue = Queue()
        #         executor.submit(self.fitnessCalculationTask, maxCost, slices[processIndex], resultQueue, population)
        #         resultQueues.append(resultQueue)

        for processIndex in range(nProcesses):
            resultQueue = mp.Queue()
            process = mp.Process(target=self.fitnessCalculationTask, args=(maxCost, slices[processIndex], resultQueue, population))
            process.start()
            processes.append(process)
            resultQueues.append(resultQueue)

        for process in processes:
            process.join()


        totalFitness = 0
        fitnessArray = []
        # print("lllllllllllllllllllllllllllllll : ", len(processesResult[0]))
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

        return self.selectApproach2()


    # def selectApproach1(self):
    #     """
    #     """
    #     chromosome = self.population.chromosomes[self.chromosomeIndex]

    #     rouletteProbabilities = []
    #     gapSum = 0
    #     for oneChromosome in self.population.chromosomes:
    #         # gap = 0 if oneChromosome == chromosome else self.population.maxCostChromosome.cost - oneChromosome.cost
    #         gap = chromosome.cost - oneChromosome.cost
    #         gap = gap if gap >= 0 else 0
    #         rouletteProbabilities.append(gap)
    #         gapSum += gap

    #     if gapSum == 0:
    #         return chromosome, chromosome

    #     rouletteProbabilities = [float(gap/gapSum) for gap in rouletteProbabilities]

    #     if self.chromosomeIndex == len(self.population.chromosomes) - 1:
    #         self.chromosomeIndex = 0
    #     else:
    #         self.chromosomeIndex += 1
        
    #     return chromosome, np.random.choice(self.population.chromosomes, p=rouletteProbabilities)


    def selectApproach2(self):
        """
        """

        return np.random.choice(self.chromosomes, p=self.rouletteProbabilities), np.random.choice(self.chromosomes, p=self.rouletteProbabilities)
