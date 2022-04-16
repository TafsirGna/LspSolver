import numpy as np

from LspAlgorithms.GeneticAlgorithms import Chromosome

class SelectionOperator:
    """
    """

    def __init__(self, chromosomes, maxCost) -> None:
        """
        """
        
        self.chromosomes = chromosomes
        self.maxCost = maxCost
        self.rouletteProbabilities = self.prepSelection()

        # print("roulette ", rouletteProbabilities)


    def select(self):
        """
        """
        return np.random.choice(self.chromosomes, p=self.rouletteProbabilities), np.random.choice(self.chromosomes, p=self.rouletteProbabilities)


    def prepSelection(self):
        """
        """
        totalFitness = 0
        for chromosome in self.chromosomes:
            chromosome.fitnessValue = self.maxCost - chromosome.cost
            # print("888 ---> ", chromosome, chromosome.fitnessValue)
            totalFitness += chromosome.fitnessValue
        totalFitness = totalFitness
        # print("888 ---> ", totalFitness)

        return [float(chromosome.fitnessValue)/totalFitness for chromosome in self.chromosomes]