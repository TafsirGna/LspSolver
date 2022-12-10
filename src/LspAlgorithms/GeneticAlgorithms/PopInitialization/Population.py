from collections import defaultdict
from LspAlgorithms.GeneticAlgorithms.GAOperators.SelectionOperator import SelectionOperator
# from LspAlgorithms.GeneticAlgorithms.LspRuntimeMonitor import LspRuntimeMonitor
from ParameterSearch.ParameterData import ParameterData
# from LspAlgorithms.GeneticAlgorithms.GAOperators.LocalSearchEngine import LocalSearchEngine

class Population:

    popSizes = defaultdict(lambda: ParameterData.instance.popSize)
    mutatedPoolSize = defaultdict(lambda: 0)

    def __init__(self, threadIdentifier, chromosomes) -> None:
        """
        """

        self.threadIdentifier = threadIdentifier

        self.best, self.worst = None, None
        self.setChromosomes(chromosomes)

        self.selectionOperator = SelectionOperator(self)

    def setChromosomes(self, chromosomes):
        """
        """

        self.chromosomes = set(chromosomes)
        self.best = min(self.chromosomes)
        self.worst = max(self.chromosomes)


    def __repr__(self):
        """
        """
        
        return "Population : {}".format(self.chromosomes)
