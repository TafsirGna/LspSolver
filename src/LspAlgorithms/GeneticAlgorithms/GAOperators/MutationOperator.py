from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from .LocalSearchEngine import LocalSearchEngine
from LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData
import random
# import numpy as np


class MutationOperator:
    """
    """

    def __init__(self, ) -> None:
        """
        """
        pass

    def processInstance(self, chromosome): # strategy :  medium/advanced
        """
        """

        strategy = "simple_mutation"
        result = (LocalSearchEngine()).process(chromosome, strategy)
        
        # # print("Mutation result : ", chromosome, result[0])
        return result


    def processPop(self, population):
        """ Got to apply mutation corresponding to the set mutation rate
        """

        mutationSize = int(population.popLength * ParameterData.instance.mutationRate)

        count = 0

        while count < mutationSize:
            stringIdentifiers = list(population.chromosomes.keys())
            stringIdentifier = stringIdentifiers[random.randint(0, len(stringIdentifiers) - 1)]
            element = population.chromosomes[stringIdentifier]

            result = self.processInstance(element["chromosome"])

            if result != element["chromosome"]:
                population.popLength -= 1
                if element["size"] == 1:
                    del population.chromosomes[stringIdentifier]
                else:
                    population.chromosomes[stringIdentifier]["size"] -= 1
                    
                population.add(result)
                count += 1

            # stringIdentifiers.remove(stringIdentifier)

        return population

