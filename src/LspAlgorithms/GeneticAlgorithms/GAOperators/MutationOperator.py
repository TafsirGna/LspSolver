from LspAlgorithms.GeneticAlgorithms.Chromosome import Chromosome
from LspAlgorithms.GeneticAlgorithms.LocalSearch.LocalSearchEngine import LocalSearchEngine
from LspRuntimeMonitor import LspRuntimeMonitor


class MutationOperator:
    """
    """

    def __init__(self, ) -> None:
        """
        """
        pass

    def process(self, chromosome): # strategy :  medium/advanced
        """
        """

        strategy = LspRuntimeMonitor.mutation_strategy
        result = (LocalSearchEngine()).process(chromosome, strategy)
        # print("Result : ", result)
        # No mutation found
        if len(result) == 0:
            return chromosome
        
        # print("Mutation result : ", chromosome, result[0])

        return result[0]