from LspAlgorithms.GeneticAlgorithms.LocalSearch.LocalSearchEngine import LocalSearchEngine
from LspRuntimeMonitor import LspRuntimeMonitor


class MutationOperator:
    """
    """

    def __init__(self, ) -> None:
        """
        """
        pass

    def process(self, chromosome, strategy = "simple_mutation"): # strategy :  medium/advanced
        """
        """
        strategy = LspRuntimeMonitor.mutation_strategy
        return (LocalSearchEngine()).process(chromosome, strategy)