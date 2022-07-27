from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from .LocalSearchEngine import LocalSearchEngine
from LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData
import random
# from collections import defaultdict
# from ..PopInitialization.Population import Population
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


    def processPop(self, population, mutatedPoolSize):
        """ Got to apply mutation corresponding to the set mutation rate
        """

        stringIdentifiers = list(population.chromosomes.keys())
        tandems = []
        counterDict = dict()

        for _ in range(mutatedPoolSize):
            
            stringIdentifier = random.choice(stringIdentifiers)
            element = population.chromosomes[stringIdentifier]

            result = self.processInstance(element["chromosome"])
            tandems.append({"input": element["chromosome"], "output": result})

            if element["chromosome"].stringIdentifier not in counterDict:
                counterDict[element["chromosome"].stringIdentifier] = 1
            else:
                counterDict[element["chromosome"].stringIdentifier] += 1

            if counterDict[element["chromosome"].stringIdentifier] == element["size"]:
                stringIdentifiers.remove(stringIdentifier)


        for tandem in tandems:
            population.popLength -= 1
            if population.chromosomes[tandem["input"].stringIdentifier]["size"] == 1:
                del population.chromosomes[tandem["input"].stringIdentifier]
            else:
                population.chromosomes[tandem["input"].stringIdentifier]["size"] -= 1
                
            population.add(tandem["output"])

        return population

