import numpy as np

from LspAlgorithms.GeneticAlgorithms import Chromosome
from ParameterSearch.ParameterData import ParameterData

class GATerminator:
    """
    """

    def __init__(self) -> None:
        """
        """
        pass


    def toTerminate(self, population):
        """
        """

        # uniques, unique_counts, fittest = [], [], self.chromosomes[0]

        # for chromosome in self.chromosomes:
        #     if not (chromosome.dnaArray in uniques):
        #         uniques.append(chromosome.dnaArray)
        #         unique_counts.append(0)
        #     else:
        #         unique_counts[uniques.index(chromosome.dnaArray)] += 1

        #     if chromosome.cost < fittest.cost:
        #         fittest = chromosome

        # localOptimal = uniques[unique_counts.index(max(unique_counts))]



        # Setting the threshold under which a populatioin is set to have converged
        threshold = int(ParameterData.instance.convergenceThresholdPercentage * population.popSize)
        threshold = 1 if threshold < 1 else threshold

        if len(population.uniques) <= threshold:
            return True
        return False
        