from os import chroot
import random
import numpy as np

from LspAlgorithms.GeneticAlgorithms import Chromosome

class SelectionOperator:
    """
    """

    def __init__(self, population) -> None:
        """
        """
        
        self.population = population
        self.chromosomeIndex = 0


    def select(self):
        """
        """
        chromosome = self.population.chromosomes[self.chromosomeIndex]

        rouletteProbabilities = []
        gapSum = 0
        for oneChromosome in self.population.chromosomes:
            # gap = 0 if oneChromosome == chromosome else self.population.maxCostChromosome.cost - oneChromosome.cost
            gap = chromosome.cost - oneChromosome.cost
            gap = gap if gap >= 0 else 0
            rouletteProbabilities.append(gap)
            gapSum += gap

        if gapSum == 0:
            return chromosome, chromosome

        rouletteProbabilities = [float(gap/gapSum) for gap in rouletteProbabilities]

        if self.chromosomeIndex == len(self.population.chromosomes) - 1:
            self.chromosomeIndex = 0
        else:
            self.chromosomeIndex += 1

        return chromosome, np.random.choice(self.population.chromosomes, p=rouletteProbabilities)