import random
import numpy as np
from LspAlgorithms.GeneticAlgorithms import Chromosome
from LspRuntimeMonitor import LspRuntimeMonitor

class SelectionOperator:
    """
    """

    def __init__(self, population) -> None:
        """
        """
        
        # self.chromosomeIndex = 0

        self.setRouletteProbabilities(population)


    def setRouletteProbabilities(self, population):
        """
        """

        self.chromosomes = [element["chromosome"] for element in population.chromosomes.values()]

        maxCost = LspRuntimeMonitor.popsData[population.lineageIdentifier]["max"][-1] + 1
        print(" maaaaaaaaaaaaaaaaaaaaaaaax : ", maxCost)
        totalFitness = 0
        for chromosome in self.chromosomes:
            chromosome.fitness = (maxCost - chromosome.cost) * population.chromosomes[chromosome.stringIdentifier]["size"]
            if chromosome.fitness < 0:
                print("------------------------------------------------------", maxCost, chromosome.cost)
            totalFitness += chromosome.fitness

        self.rouletteProbabilities = [float(chromosome.fitness/totalFitness) for chromosome in self.chromosomes]

        # print("**************************")
        # print("Roulette : ", self.population.maxCostChromosome, " \n  \n ", self.population.chromosomes, " \n \n ", self.rouletteProbabilities)
        # print("++++++++++++++++++++++++++")


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
