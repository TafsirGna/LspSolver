

import random
from LspAlgorithms.GeneticAlgorithms.PopInitialization.Population import Population
from ParameterSearch.ParameterData import ParameterData


class NodeGenerator:

    instance = None
    
    def __init__(self, queue) -> None:
        self.queue = queue
        pass

    def generate(self):
        """
        """

        while len(self.queue) > 0:

            node = self.queue[-1]
            self.queue = self.queue[0:- 1]

            children = node.children()

            random.shuffle(children)
            self.queue += children

            if len(children) == 0: # leaf node
                yield node
    