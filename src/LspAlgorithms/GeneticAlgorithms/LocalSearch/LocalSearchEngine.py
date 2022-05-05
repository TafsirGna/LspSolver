import numpy as np
from LspAlgorithms.GeneticAlgorithms.LocalSearch.LocalSearchNode import LocalSearchNode
from ParameterSearch.ParameterData import ParameterData

class LocalSearchEngine:
    """
    """

    def __init__(self) -> None:
        pass


    def localSearchNode(self, chromosome):
        """
        """

        node = LocalSearchNode(chromosome)
        return node


    def process(self, chromosome, strategy = "simple_mutation"): 
        """ Process the given chromosome in order to return a mutated version
        strategy: simple_mutation|absolute_mutation|positive_mutation
        """

        node = self.localSearchNode(chromosome)
        queue = node.children()
        depthIndex = 0

        while len(queue) > 0:
            node = queue[-1]
            queue = queue[:-1]

            children = None
            if strategy == "simple_mutation": # simple means random here
                if depthIndex == 1:
                    # node = np.random.choice(queue)
                    return node.chromosome
                children = node.children()
            elif strategy == "positive_mutation":
                if node.chromosome.cost < chromosome.cost:
                    return node.chromosome
                children = node.children()
            elif strategy ==  "absolute_mutation":
                children = node.children()
                if len(children) == 0:
                    return node.chromosome

            queue += children
            depthIndex += 1

        return None


    def populate(self, chromosome, popSet):
        """
        """

        node = self.localSearchNode(chromosome)
        population = popSet[1]
        queue = []

        while len(population.chromosomes) < ParameterData.instance.popSize:
            for child in node.generateChild():
                queue.append(child)
                result = population.add(child.chromosome)
                if result is None:
                    return

            if len(queue) == 0:
                return
            node = queue[-1]
            queue = queue[:-1]
        